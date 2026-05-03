import os
import re

# Directories to ignore
IGNORE_DIRS = {'tests', 'OpenGL', '__pycache__', '.git', 'scripts', '.gemini'}
# Files to ignore
IGNORE_FILES = {'compress.py', '.gitignore', '.python-version', 'README.md', 'compressed.py'}

# Manual ordering to ensure base classes are defined before they are used/inherited
# This helps make the resulting single file valid.
DIR_PRIORITY = ['core', 'components', 'anomalies', 'game']

def get_all_files():
    all_files = []
    for root, dirs, files in os.walk('.'):
        # Remove ignored directories from search
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for file in files:
            if file.endswith('.py') and file not in IGNORE_FILES:
                rel_path = os.path.relpath(os.path.join(root, file), '.')
                all_files.append(rel_path)
    
    # Sort files based on directory priority
    def sort_key(path):
        parts = path.split(os.sep)
        if len(parts) == 1: # main.py or other root files
            return (len(DIR_PRIORITY), path)
        
        dir_name = parts[0]
        if dir_name in DIR_PRIORITY:
            return (DIR_PRIORITY.index(dir_name), path)
        return (len(DIR_PRIORITY) + 1, path)

    all_files.sort(key=sort_key)
    return all_files

def compress():
    files = get_all_files()
    
    # Patterns for internal imports that should be commented out
    # e.g., "from components.transform import Transform" or "from .chair_state import ChairState"
    internal_import_patterns = [
        re.compile(r'^from\s+(core|components|game|anomalies)\..*import.*'),
        re.compile(r'^from\s+\..*import.*'),
        re.compile(r'^import\s+(core|components|game|anomalies).*')
    ]

    print("# " + "="*50)
    print("# AUTO-GENERATED COMPRESSED PROJECT FILE")
    print("# " + "="*50 + "\n")

    for file_path in files:
        print(f"\n# {file_path}")
        print("# " + "-"*len(file_path))
        
        with open(file_path, 'r') as f:
            lines = f.readlines()
            
            for line in lines:
                is_internal = any(p.match(line.strip()) for p in internal_import_patterns)
                
                # Special case: don't comment out OpenGL or standard library imports
                if is_internal:
                    print(f"# {line}", end='')
                else:
                    print(line, end='')
        print("\n")

if __name__ == "__main__":
    compress()
