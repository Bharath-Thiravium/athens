#!/usr/bin/env python
"""
Setup script to initialize RAG system locally
Run this after installing dependencies and setting up pgvector
"""
import os
import sys
import django
import subprocess
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

def check_redis():
    """Check if Redis is running"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✓ Redis is running")
        return True
    except Exception as e:
        print(f"✗ Redis not running: {e}")
        print("Install and start Redis:")
        print("  sudo apt-get install -y redis-server")
        print("  sudo systemctl enable --now redis-server")
        return False

def check_pgvector():
    """Check if pgvector extension is available"""
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        print("✓ pgvector extension is available")
        return True
    except Exception as e:
        print(f"✗ pgvector extension not available: {e}")
        print("Install pgvector:")
        print("  sudo apt-get install postgresql-16-pgvector")
        print("  (adjust version number to match your PostgreSQL)")
        return False

def run_migrations():
    """Run Django migrations"""
    try:
        subprocess.run([sys.executable, 'manage.py', 'makemigrations', 'ai_bot'], check=True)
        subprocess.run([sys.executable, 'manage.py', 'migrate'], check=True)
        print("✓ Migrations completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Migration failed: {e}")
        return False

def build_initial_index():
    """Build the initial RAG index"""
    try:
        from ai_bot.vector_rag_service import VectorRAGService
        rag = VectorRAGService()
        stats = rag.rebuild_index()
        print(f"✓ RAG index built: {stats}")
        return True
    except Exception as e:
        print(f"✗ Failed to build RAG index: {e}")
        return False

def test_rag_query():
    """Test a simple RAG query"""
    try:
        from ai_bot.hybrid_rag_service import HybridRAGService
        rag = HybridRAGService()
        result = rag.query("test query")
        print(f"✓ RAG query test successful: {result['type']}")
        return True
    except Exception as e:
        print(f"✗ RAG query test failed: {e}")
        return False

def main():
    print("🚀 Setting up RAG system...")
    print()
    
    checks = [
        ("Redis", check_redis),
        ("pgvector", check_pgvector),
        ("Migrations", run_migrations),
        ("RAG Index", build_initial_index),
        ("RAG Query", test_rag_query),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"Checking {name}...")
        success = check_func()
        results.append((name, success))
        print()
    
    print("=" * 50)
    print("SETUP SUMMARY:")
    print("=" * 50)
    
    all_passed = True
    for name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{name:15} {status}")
        if not success:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 RAG setup completed successfully!")
        print()
        print("Next steps:")
        print("1. Start Celery worker: python -m celery -A backend.celery_app worker -l info")
        print("2. Start Django server: python manage.py runserver")
        print("3. Test RAG queries via API or chat UI")
    else:
        print("❌ Setup incomplete. Please fix the failed checks above.")
        sys.exit(1)

if __name__ == '__main__':
    main()
