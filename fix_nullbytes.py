import os
import sys

def clean_file(filepath):
    """Clean null bytes from a file"""
    print(f"Processing: {filepath}")
    
    # Read the file in binary mode
    with open(filepath, 'rb') as f:
        content = f.read()
    
    # Check if there are null bytes
    if b'\x00' not in content:
        print(f"  No null bytes found in {filepath}")
        return False
    
    # Create backup
    backup_path = filepath + '.bak'
    with open(backup_path, 'wb') as f:
        f.write(content)
    
    # Clean the file
    cleaned = content.replace(b'\x00', b'')
    
    # Write back
    with open(filepath, 'wb') as f:
        f.write(cleaned)
    
    print(f"  Cleaned null bytes in {filepath} (backup created)")
    return True

def main():
    # Get the project root directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Scanning directory: {project_dir}")
    
    # Count files
    total_files = 0
    cleaned_files = 0
    
    # Walk through all directories
    for root, dirs, files in os.walk(project_dir):
        # Skip __pycache__ directories
        if '__pycache__' in dirs:
            dirs.remove('__pycache__')
        
        # Process Python files
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                total_files += 1
                
                if clean_file(filepath):
                    cleaned_files += 1
    
    # Print summary
    print("\nSummary:")
    print(f"Total Python files: {total_files}")
    print(f"Files cleaned: {cleaned_files}")

if __name__ == "__main__":
    main()
