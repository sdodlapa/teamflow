#!/usr/bin/env python3
"""
Fix database compatibility issues by replacing PostgreSQL-specific features
with SQLite-compatible alternatives.
"""

import os
import re
from pathlib import Path

def fix_file(file_path):
    """Fix a single file for database compatibility."""
    
    print(f"Fixing {file_path}...")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Track if we made changes
    original_content = content
    
    # Remove PostgreSQL-specific imports
    content = re.sub(r'from sqlalchemy\.dialects\.postgresql import UUID, ARRAY\n', '', content)
    content = re.sub(r'from sqlalchemy\.dialects\.postgresql import UUID\n', '', content)
    content = re.sub(r'from sqlalchemy\.dialects\.postgresql import ARRAY\n', '', content)
    content = re.sub(r', UUID, ARRAY', '', content)
    content = re.sub(r', UUID', '', content)
    content = re.sub(r', ARRAY', '', content)
    
    # Fix UUID column definitions
    content = re.sub(r'Column\(UUID\(as_uuid=True\), ([^,]+), ([^,]+), ([^)]+)\)', 
                     r'Column(Integer, \1, \2)', content)
    content = re.sub(r'Column\(UUID\(as_uuid=True\), ([^,]+), ([^)]+)\)', 
                     r'Column(Integer, \1)', content)
    content = re.sub(r'Column\(UUID\(as_uuid=True\), ([^)]+)\)', 
                     r'Column(Integer, \1)', content)
    
    # Fix foreign key UUID references
    content = re.sub(r'ForeignKey\("([^"]+)\.id"\), nullable=True, index=True\)',
                     r'ForeignKey("\1.id"), nullable=True, index=True)', content)
    
    # Fix ARRAY column types
    content = re.sub(r'Column\(ARRAY\(String\), ([^)]+)\)', 
                     r'Column(String(1000), \1)', content)
    content = re.sub(r'Column\(ARRAY\(String\)([^)]*)\)', 
                     r'Column(String(1000)\1)', content)
    
    # Fix default values for UUIDs
    content = re.sub(r'default=uuid\.uuid4', 'default=lambda: str(uuid.uuid4())', content)
    
    # Fix enum defaults to use .value
    content = re.sub(r'default=([A-Za-z]+\.[A-Z_]+)([,)])', r'default=\1.value\2', content)
    
    # Add uuid import if needed and not present
    if 'uuid.uuid4' in content and 'import uuid' not in content:
        if 'from datetime import datetime' in content:
            content = content.replace('from datetime import datetime', 'import uuid\nfrom datetime import datetime')
        else:
            content = 'import uuid\n' + content
    
    # Write back if changed
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"  ✅ Fixed {file_path}")
        return True
    else:
        print(f"  ⏭️  No changes needed for {file_path}")
        return False

def main():
    """Fix all model files."""
    
    models_dir = Path("app/models")
    
    if not models_dir.exists():
        print("❌ Models directory not found. Run this from the backend directory.")
        return 1
    
    files_to_fix = [
        "security.py",
        "webhooks.py",
        "analytics.py", 
        "workflow.py",
        "search.py",
        "file_management.py"
    ]
    
    fixed_count = 0
    
    for file_name in files_to_fix:
        file_path = models_dir / file_name
        if file_path.exists():
            if fix_file(file_path):
                fixed_count += 1
        else:
            print(f"⚠️  File not found: {file_path}")
    
    print(f"\n🎉 Fixed {fixed_count} files for SQLite compatibility!")
    return 0

if __name__ == "__main__":
    exit(main())