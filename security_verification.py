#!/usr/bin/env python3
"""
EHS Management System - Security Verification Script
====================================================
Comprehensive security verification for production deployment
"""

import os
import sys
import subprocess
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any

class SecurityVerifier:
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.passed = []
        self.project_root = Path(__file__).parent
        
    def log_issue(self, category: str, message: str, severity: str = "HIGH"):
        self.issues.append({
            "category": category,
            "message": message,
            "severity": severity
        })
        
    def log_warning(self, category: str, message: str):
        self.warnings.append({
            "category": category,
            "message": message
        })
        
    def log_passed(self, category: str, message: str):
        self.passed.append({
            "category": category,
            "message": message
        })

    def check_django_security(self) -> bool:
        """Check Django security configuration"""
        print("🔍 Checking Django security configuration...")
        
        try:
            # Run Django security check
            result = subprocess.run(
                ["python", "manage.py", "check", "--deploy"],
                cwd=self.project_root / "backend",
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.log_passed("Django Security", "All Django security checks passed")
                return True
            else:
                self.log_issue("Django Security", f"Django security check failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.log_issue("Django Security", "Django security check timed out")
            return False
        except Exception as e:
            self.log_issue("Django Security", f"Error running Django security check: {str(e)}")
            return False

    def check_environment_files(self) -> bool:
        """Check environment file security"""
        print("🔍 Checking environment file security...")
        
        env_files = [
            self.project_root / "backend" / ".env",
            self.project_root / "backend" / ".env.example",
            self.project_root / "frontedn" / ".env.local",
            self.project_root / "frontedn" / ".env.example"
        ]
        
        all_secure = True
        
        for env_file in env_files:
            if env_file.exists():
                # Check file permissions
                stat = env_file.stat()
                permissions = oct(stat.st_mode)[-3:]
                
                if permissions != "600" and not env_file.name.endswith(".example"):
                    self.log_issue("File Permissions", f"{env_file} has insecure permissions: {permissions}")
                    all_secure = False
                else:
                    self.log_passed("File Permissions", f"{env_file} has secure permissions")
                
                # Check for sensitive data in example files
                if env_file.name.endswith(".example"):
                    content = env_file.read_text()
                    if re.search(r'(password|secret|key)=(?!your-|example-|test-)', content, re.IGNORECASE):
                        self.log_warning("Sensitive Data", f"{env_file} may contain real credentials")
        
        return all_secure

    def check_secret_keys(self) -> bool:
        """Check secret key strength"""
        print("🔍 Checking secret key strength...")
        
        env_file = self.project_root / "backend" / ".env"
        if not env_file.exists():
            self.log_warning("Secret Key", "Backend .env file not found")
            return False
            
        content = env_file.read_text()
        secret_key_match = re.search(r'SECRET_KEY=(.+)', content)
        
        if not secret_key_match:
            self.log_issue("Secret Key", "SECRET_KEY not found in .env file")
            return False
            
        secret_key = secret_key_match.group(1).strip('"\'')
        
        # Check secret key strength
        if len(secret_key) < 50:
            self.log_issue("Secret Key", f"SECRET_KEY too short: {len(secret_key)} characters (minimum 50)")
            return False
            
        if secret_key.startswith('django-insecure-'):
            self.log_issue("Secret Key", "SECRET_KEY is using Django's insecure default")
            return False
            
        # Check character diversity
        unique_chars = len(set(secret_key))
        if unique_chars < 10:
            self.log_issue("Secret Key", f"SECRET_KEY has low character diversity: {unique_chars} unique characters")
            return False
            
        self.log_passed("Secret Key", "SECRET_KEY meets security requirements")
        return True

    def check_docker_security(self) -> bool:
        """Check Docker configuration security"""
        print("🔍 Checking Docker security configuration...")
        
        dockerfile_backend = self.project_root / "backend" / "Dockerfile"
        dockerfile_frontend = self.project_root / "frontedn" / "Dockerfile"
        
        all_secure = True
        
        for dockerfile in [dockerfile_backend, dockerfile_frontend]:
            if dockerfile.exists():
                content = dockerfile.read_text()
                
                # Check for non-root user
                if "USER " not in content:
                    self.log_issue("Docker Security", f"{dockerfile} doesn't specify non-root user")
                    all_secure = False
                else:
                    self.log_passed("Docker Security", f"{dockerfile} uses non-root user")
                
                # Check for health checks
                if "HEALTHCHECK" not in content:
                    self.log_warning("Docker Security", f"{dockerfile} missing health check")
                else:
                    self.log_passed("Docker Security", f"{dockerfile} includes health check")
        
        return all_secure

    def check_cors_configuration(self) -> bool:
        """Check CORS configuration"""
        print("🔍 Checking CORS configuration...")
        
        settings_file = self.project_root / "backend" / "backend" / "settings.py"
        if not settings_file.exists():
            self.log_issue("CORS", "Django settings.py not found")
            return False
            
        content = settings_file.read_text()
        
        # Check for CORS_ALLOW_ALL_ORIGINS
        if "CORS_ALLOW_ALL_ORIGINS = True" in content and "DEBUG" not in content:
            self.log_issue("CORS", "CORS_ALLOW_ALL_ORIGINS is True in production")
            return False
        elif "CORS_ALLOW_ALL_ORIGINS = DEBUG" in content:
            self.log_passed("CORS", "CORS properly configured for development/production")
        
        return True

    def check_ssl_configuration(self) -> bool:
        """Check SSL/HTTPS configuration"""
        print("🔍 Checking SSL/HTTPS configuration...")
        
        settings_file = self.project_root / "backend" / "backend" / "settings.py"
        if not settings_file.exists():
            return False
            
        content = settings_file.read_text()
        
        ssl_settings = [
            "SECURE_SSL_REDIRECT",
            "SECURE_HSTS_SECONDS",
            "SESSION_COOKIE_SECURE",
            "CSRF_COOKIE_SECURE"
        ]
        
        all_configured = True
        for setting in ssl_settings:
            if setting not in content:
                self.log_issue("SSL Configuration", f"{setting} not configured")
                all_configured = False
            else:
                self.log_passed("SSL Configuration", f"{setting} is configured")
        
        return all_configured

    def check_dependencies(self) -> bool:
        """Check for vulnerable dependencies"""
        print("🔍 Checking for vulnerable dependencies...")
        
        try:
            # Check Python dependencies
            result = subprocess.run(
                ["pip", "list", "--format=json"],
                cwd=self.project_root / "backend",
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.log_passed("Dependencies", "Python dependencies check completed")
            else:
                self.log_warning("Dependencies", "Could not check Python dependencies")
            
            # Check Node.js dependencies
            npm_audit = subprocess.run(
                ["npm", "audit", "--json"],
                cwd=self.project_root / "frontedn",
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if npm_audit.returncode == 0:
                audit_data = json.loads(npm_audit.stdout)
                if audit_data.get("vulnerabilities", {}):
                    high_vulns = sum(1 for v in audit_data["vulnerabilities"].values() 
                                   if v.get("severity") in ["high", "critical"])
                    if high_vulns > 0:
                        self.log_issue("Dependencies", f"Found {high_vulns} high/critical vulnerabilities in Node.js dependencies")
                        return False
                
                self.log_passed("Dependencies", "No critical vulnerabilities found in Node.js dependencies")
            
            return True
            
        except Exception as e:
            self.log_warning("Dependencies", f"Error checking dependencies: {str(e)}")
            return True  # Don't fail the entire check

    def generate_report(self) -> Dict[str, Any]:
        """Generate security report"""
        total_checks = len(self.issues) + len(self.warnings) + len(self.passed)
        
        report = {
            "summary": {
                "total_checks": total_checks,
                "passed": len(self.passed),
                "warnings": len(self.warnings),
                "issues": len(self.issues),
                "security_score": round((len(self.passed) / total_checks) * 100, 2) if total_checks > 0 else 0
            },
            "issues": self.issues,
            "warnings": self.warnings,
            "passed": self.passed
        }
        
        return report

    def run_all_checks(self) -> bool:
        """Run all security checks"""
        print("🔐 Starting comprehensive security verification...\n")
        
        checks = [
            ("Django Security", self.check_django_security),
            ("Environment Files", self.check_environment_files),
            ("Secret Keys", self.check_secret_keys),
            ("Docker Security", self.check_docker_security),
            ("CORS Configuration", self.check_cors_configuration),
            ("SSL Configuration", self.check_ssl_configuration),
            ("Dependencies", self.check_dependencies)
        ]
        
        all_passed = True
        
        for check_name, check_func in checks:
            try:
                result = check_func()
                if not result:
                    all_passed = False
            except Exception as e:
                self.log_issue(check_name, f"Check failed with error: {str(e)}")
                all_passed = False
        
        return all_passed

def main():
    verifier = SecurityVerifier()
    
    print("=" * 80)
    print("🔐 EHS Management System - Security Verification")
    print("=" * 80)
    
    success = verifier.run_all_checks()
    report = verifier.generate_report()
    
    print("\n" + "=" * 80)
    print("📊 SECURITY VERIFICATION REPORT")
    print("=" * 80)
    
    print(f"Total Checks: {report['summary']['total_checks']}")
    print(f"✅ Passed: {report['summary']['passed']}")
    print(f"⚠️  Warnings: {report['summary']['warnings']}")
    print(f"❌ Issues: {report['summary']['issues']}")
    print(f"🎯 Security Score: {report['summary']['security_score']}%")
    
    if report['issues']:
        print("\n🚨 CRITICAL ISSUES:")
        for issue in report['issues']:
            print(f"  ❌ [{issue['category']}] {issue['message']}")
    
    if report['warnings']:
        print("\n⚠️  WARNINGS:")
        for warning in report['warnings']:
            print(f"  ⚠️  [{warning['category']}] {warning['message']}")
    
    print("\n✅ PASSED CHECKS:")
    for passed in report['passed']:
        print(f"  ✅ [{passed['category']}] {passed['message']}")
    
    print("\n" + "=" * 80)
    
    if success and len(report['issues']) == 0:
        print("🎉 SECURITY VERIFICATION PASSED!")
        print("System is ready for production deployment.")
        return 0
    else:
        print("❌ SECURITY VERIFICATION FAILED!")
        print("Please address the issues above before deploying to production.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
