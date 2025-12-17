#!/usr/bin/env python3
"""
Script to fix empty except blocks that are missing pass statements
"""
import os
import re

def fix_except_blocks(file_path):
    """Fix empty except blocks in a Python file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Pattern to match except blocks followed by empty lines or class/function definitions
        pattern = r'(\s*except\s+[^:]*:\s*\n)(\s*\n)(\s*(?:def|class|\S))'
        
        def replace_func(match):
            indent = match.group(1).split('except')[0]  # Get the indentation
            except_line = match.group(1)
            empty_line = match.group(2)
            next_line = match.group(3)
            
            # Add pass with proper indentation
            pass_line = indent + '    pass\n'
            return except_line + pass_line + empty_line + next_line
        
        # Apply the fix
        fixed_content = re.sub(pattern, replace_func, content)
        
        # Also handle except blocks at the end of file
        pattern2 = r'(\s*except\s+[^:]*:\s*\n)(\s*$)'
        def replace_func2(match):
            indent = match.group(1).split('except')[0]
            except_line = match.group(1)
            pass_line = indent + '    pass\n'
            return except_line + pass_line
        
        fixed_content = re.sub(pattern2, replace_func2, fixed_content)
        
        if fixed_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            print(f"Fixed: {file_path}")
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Fix all Python files in the backend directory"""
    backend_dir = '/home/athenas/Documents/project/10.07.2025 upatepro/upatepro/project/backend'
    
    fixed_count = 0
    for root, dirs, files in os.walk(backend_dir):
        # Skip virtual environment and __pycache__ directories
        dirs[:] = [d for d in dirs if d not in ['venv', '__pycache__', '.git']]
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if fix_except_blocks(file_path):
                    fixed_count += 1
    
    print(f"Fixed {fixed_count} files")

if __name__ == '__main__':
    main()
