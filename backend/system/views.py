import csv
import io
import os
import re
import shutil
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.http import FileResponse, HttpResponse
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.utils._os import safe_join

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import SystemSettings, Backup
from .serializers import SystemSettingsSerializer, BackupSerializer

# Helpers

def is_master(user):
    """Allow only master admin or superuser to access system endpoints."""
    # Your CustomUser uses `admin_type` for org role and `user_type` for approval class
    # Master is indicated by admin_type == 'master'
    if hasattr(user, 'admin_type') and user.admin_type == 'master':
        return True
    # Allow Django superusers as well
    if user.is_superuser:
        return True
    return False

class SystemSettingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not is_master(request.user):
            return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        obj, _ = SystemSettings.objects.get_or_create(id=1)
        return Response(SystemSettingsSerializer(obj).data)

    def put(self, request):
        if not is_master(request.user):
            return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        obj, _ = SystemSettings.objects.get_or_create(id=1)
        ser = SystemSettingsSerializer(obj, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data)

class SystemLogsView(APIView):
    permission_classes = [IsAuthenticated]

    # Regex for verbose formatter: '{levelname} {asctime} {module} {process:d} {thread:d} {message}'
    VERBOSE_RE = re.compile(r'^(DEBUG|INFO|WARNING|ERROR|CRITICAL)\s+(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2},\d{3})\s+([\w\.]+)\s+\d+\s+\d+\s+(.*)$')
    # Simple: '[SECURITY] {asctime} {levelname} {module} {message}'
    SECURITY_RE = re.compile(r'^\[SECURITY\]\s+(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2},\d{3})\s+(DEBUG|INFO|WARNING|ERROR|CRITICAL)\s+([\w\.]+)\s+(.*)$')

    def parse_line(self, line: str):
        m = self.VERBOSE_RE.match(line)
        if m:
            level, ts, module, msg = m.groups()
            return {
                'timestamp': ts,
                'level': level,
                'module': module,
                'message': msg,
            }
        m = self.SECURITY_RE.match(line)
        if m:
            ts, level, module, msg = m.groups()
            return {
                'timestamp': ts,
                'level': level,
                'module': module,
                'message': msg,
            }
        # Fallback: try to split on first 2 spaces
        parts = line.split(' ', 3)
        if len(parts) >= 4 and parts[0] in ('DEBUG','INFO','WARNING','ERROR','CRITICAL'):
            return {
                'timestamp': parts[1],
                'level': parts[0],
                'module': parts[2],
                'message': parts[3],
            }
        return {
            'timestamp': '',
            'level': '',
            'module': '',
            'message': line.strip(),
        }

    def get(self, request):
        if not is_master(request.user):
            return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        level = request.query_params.get('level')
        module = request.query_params.get('module')
        search = request.query_params.get('search')
        start = request.query_params.get('start')
        end = request.query_params.get('end')

        # Use safe_join to prevent path traversal
        log_files = [
            safe_join(settings.BASE_DIR, 'debug.log'),
            safe_join(settings.BASE_DIR, 'logs', 'django.log'),
            safe_join(settings.BASE_DIR, 'logs', 'security.log'),
        ]
        results = []
        for log_file in log_files:
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    for raw in f:
                        line_stripped = raw.strip()
                        # Parse
                        parsed = self.parse_line(line_stripped)
                        # Basic filters
                        if search and search.lower() not in line_stripped.lower():
                            continue
                        if level and level != 'all' and parsed.get('level') and parsed['level'] != level:
                            continue
                        if module and module != 'all' and parsed.get('module') and parsed['module'] != module:
                            continue
                        entry = {
                            'id': abs(hash(line_stripped)),
                            'timestamp': parsed.get('timestamp', ''),
                            'level': parsed.get('level', ''),
                            'module': parsed.get('module', ''),
                            'message': parsed.get('message', line_stripped),
                            'user': '',
                            'ip_address': ''
                        }
                        results.append(entry)
        # Sort by timestamp if present (desc)
        try:
            results.sort(key=lambda x: datetime.strptime(x['timestamp'], '%Y-%m-%d %H:%M:%S,%f') if x['timestamp'] else datetime.min, reverse=True)
        except (ValueError, TypeError) as e:
            # Log specific parsing errors
            pass
        # Pagination
        try:
            page = int(request.query_params.get('page', '1'))
            page_size = int(request.query_params.get('page_size', '50'))
        except ValueError:
            page, page_size = 1, 50
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        return Response({
            'count': len(results),
            'results': results[start_idx:end_idx]
        })

class SystemLogsExportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not is_master(request.user):
            return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['timestamp', 'level', 'module', 'message', 'user', 'ip_address'])
        for lf in [
            safe_join(settings.BASE_DIR, 'debug.log'),
            safe_join(settings.BASE_DIR, 'logs', 'django.log'),
            safe_join(settings.BASE_DIR, 'logs', 'security.log'),
        ]:
            if os.path.exists(lf):
                with open(lf, 'r', encoding='utf-8', errors='ignore') as f:
                    for raw in f:
                        # Use static method to avoid creating new instances
                        parsed = self.parse_line(raw.strip())
                        writer.writerow([
                            parsed.get('timestamp',''),
                            parsed.get('level',''),
                            parsed.get('module',''),
                            parsed.get('message',''),
                            '', ''
                        ])
        resp = HttpResponse(output.getvalue(), content_type='text/csv')
        resp['Content-Disposition'] = 'attachment; filename="system-logs.csv"'
        return resp

class BackupListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not is_master(request.user):
            return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        qs = Backup.objects.order_by('-created_at')
        return Response(BackupSerializer(qs, many=True).data)

    def post(self, request):
        if not is_master(request.user):
            return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        name = request.data.get('name') or f"backup_{now().strftime('%Y%m%d_%H%M%S')}"
        btype = request.data.get('type', 'full')
        description = request.data.get('description', '')

        # Create temp dir for backup assembly
        tmpdir = tempfile.mkdtemp()
        archive_name = f"{name}.zip"
        archive_path = os.path.join(tmpdir, archive_name)

        try:
            # Step 1: DB dump with input validation
            db_conf = settings.DATABASES['default']
            engine = db_conf['ENGINE']
            dump_path = safe_join(tmpdir, 'db.sql')
            if 'postgresql' in engine:
                # Validate database parameters to prevent injection
                db_name = str(db_conf['NAME']).replace(';', '').replace('&', '')
                db_user = str(db_conf['USER']).replace(';', '').replace('&', '')
                db_host = str(db_conf.get('HOST', 'localhost')).replace(';', '').replace('&', '')
                db_port = str(db_conf.get('PORT', '5432')).replace(';', '').replace('&', '')
                db_pass = db_conf.get('PASSWORD')
                
                # Validate port is numeric
                try:
                    int(db_port)
                except ValueError:
                    raise ValidationError('Invalid database port')
                    
                env = os.environ.copy()
                if db_pass:
                    env['PGPASSWORD'] = db_pass
                subprocess.check_call([
                    '/usr/bin/pg_dump', '-h', db_host, '-p', db_port, '-U', db_user, '-d', db_name, '-F', 'p', '-f', dump_path
                ], env=env)
            elif 'sqlite' in engine:
                db_name = str(db_conf['NAME'])
                # Validate SQLite database path
                if not os.path.exists(db_name) or not db_name.endswith('.db'):
                    raise ValidationError('Invalid SQLite database path')
                # sqlite .dump to SQL
                with open(dump_path, 'w', encoding='utf-8') as out:
                    subprocess.check_call(['/usr/bin/sqlite3', db_name, '.dump'], stdout=out)
            elif 'mysql' in engine:
                # Validate MySQL parameters
                db_name = str(db_conf['NAME']).replace(';', '').replace('&', '')
                db_user = str(db_conf['USER']).replace(';', '').replace('&', '')
                db_host = str(db_conf.get('HOST', 'localhost')).replace(';', '').replace('&', '')
                db_port = str(db_conf.get('PORT', '3306')).replace(';', '').replace('&', '')
                db_pass = db_conf.get('PASSWORD')
                
                # Validate port is numeric
                try:
                    int(db_port)
                except ValueError:
                    raise ValidationError('Invalid database port')
                    
                env = os.environ.copy()
                if db_pass:
                    env['MYSQL_PWD'] = db_pass
                with open(dump_path, 'w', encoding='utf-8') as out:
                    subprocess.check_call([
                        '/usr/bin/mysqldump', '-h', db_host, '-P', db_port, '-u', db_user, db_name
                    ], stdout=out, env=env)
            else:
                raise Exception(f'Unsupported DB engine: {engine}')

            # Step 2: Copy media with path validation
            media_src = settings.MEDIA_ROOT
            media_dst = safe_join(tmpdir, 'media')
            if os.path.exists(media_src) and os.path.isdir(media_src):
                shutil.copytree(media_src, media_dst)

            # Step 3: Zip it
            shutil.make_archive(archive_path.replace('.zip',''), 'zip', tmpdir)

            # Save model and move file to storage with path validation
            backup = Backup.objects.create(
                name=name,
                type=btype,
                description=description,
                status='completed',
            )
            # Move final archive into FileField with safe paths
            final_dir = safe_join(settings.MEDIA_ROOT, 'backups')
            os.makedirs(final_dir, exist_ok=True)
            final_path = safe_join(final_dir, archive_name)
            shutil.move(archive_path, final_path)
            rel_path = os.path.relpath(final_path, settings.MEDIA_ROOT)
            backup.file.name = rel_path
            backup.size = f"{os.path.getsize(final_path) / (1024*1024):.2f} MB"
            backup.save()

            return Response(BackupSerializer(backup).data, status=status.HTTP_201_CREATED)
        except subprocess.CalledProcessError as e:
            return Response({'error': f'Database dump failed: {e}'}, status=500)
        except Exception as e:
            return Response({'error': str(e)}, status=500)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

class BackupDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        if not is_master(request.user):
            return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        try:
            backup = Backup.objects.get(pk=pk)
        except Backup.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)
        # Remove file with error handling
        if backup.file and os.path.exists(backup.file.path):
            try:
                os.remove(backup.file.path)
            except (OSError, IOError) as e:
                # Log error but continue with database deletion
                pass
        backup.delete()
        return Response(status=204)

class BackupDownloadView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        if not is_master(request.user):
            return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        try:
            backup = Backup.objects.get(pk=pk)
        except Backup.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)
        if not backup.file:
            return Response({'error': 'File missing'}, status=404)
        # Use context manager for file handling
        filename = os.path.basename(backup.file.path)
        return FileResponse(open(backup.file.path, 'rb'), as_attachment=True, filename=filename)

class BackupRestoreView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        if not is_master(request.user):
            return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        try:
            backup = Backup.objects.get(pk=pk)
        except Backup.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)

        # Restoring from backup is dangerous in a live system; placeholder implementation
        # You may implement: stop app, drop & recreate DB, restore from db.sql, restore media
        # For safety, we just return a message
        return Response({'status': 'restore-not-implemented', 'note': 'Restore functionality requires offline implementation for safety'}, status=status.HTTP_501_NOT_IMPLEMENTED)

class BackupUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not is_master(request.user):
            return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        backup = Backup.objects.create(name=file.name, type='full', description='Uploaded backup', status='completed')
        backup.file.save(file.name, file, save=True)
        backup.size = f"{backup.file.size / (1024*1024):.2f} MB"
        backup.save()
        return Response(BackupSerializer(backup).data, status=status.HTTP_201_CREATED)

