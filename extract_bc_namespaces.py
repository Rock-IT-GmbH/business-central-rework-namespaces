import os
import re
import csv
import sqlite3
import sys

def extract_info(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Extract namespace
        namespace_match = re.search(r'namespace\s+([^;]+);', content)
        namespace = namespace_match.group(1) if namespace_match else ''

        # Extract object type, number (if present), and name
        object_pattern = r'''
            (table|page|report|codeunit|query|xmlport|enum|
            tableextension|pageextension|interface|profile|
            enumextension|reportextension|pagecustomization|
            permissionset|permissionsetextension|entitlement)
            \s+
            (?:(\d+)\s+)?  # Optional number
            (?:"([^"]+)"|(\w+))
        '''
        object_match = re.search(object_pattern, content, re.IGNORECASE | re.VERBOSE)
        if object_match:
            object_type = object_match.group(1)
            object_number = object_match.group(2) if object_match.group(2) else ''
            object_name = object_match.group(3) if object_match.group(3) else object_match.group(4)
        else:
            object_type = object_number = object_name = ''

        return object_type, object_number, object_name, namespace
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return '', '', '', ''

def process_directory(directory_path, output_csv, db_name):
    # Set up SQLite database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS bc_objects
                      (object_type TEXT, object_number TEXT, object_name TEXT, namespace TEXT, file_path TEXT)''')

    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile, \
         open('processing_log.txt', 'w', encoding='utf-8') as logfile, \
         open('error_log.txt', 'w', encoding='utf-8') as errorlog:

        writer = csv.writer(csvfile)
        writer.writerow(['Object Type', 'Object Number', 'Object Name', 'Namespace', 'File Path'])

        total_files = 0
        processed_files = 0

        for root, dirs, files in os.walk(directory_path):
            logfile.write(f"Entering directory: {root}\n")
            for file in files:
                if file.endswith('.al'):
                    total_files += 1
                    file_path = os.path.join(root, file)
                    logfile.write(f"  Processing file: {file_path}\n")
                    try:
                        obj_type, obj_number, obj_name, namespace = extract_info(file_path)
                        writer.writerow([obj_type, obj_number, obj_name, namespace, file_path])
                        #TODO: Add a check to see if the object already exists in the database and handle duplicates.
                        cursor.execute('''INSERT INTO bc_objects (object_type, object_number, object_name, namespace, file_path)
                                          VALUES (?, ?, ?, ?, ?)''', (obj_type, obj_number, obj_name, namespace, file_path))
                        processed_files += 1
                    except Exception as e:
                        error_message = f"Error processing {file_path}: {str(e)}\n"
                        print(error_message, file=sys.stderr)
                        errorlog.write(error_message)

        logfile.write(f"\nTotal .al files found: {total_files}\n")
        logfile.write(f"Successfully processed files: {processed_files}\n")

    # Commit changes and close database connection
    conn.commit()
    conn.close()

    return total_files, processed_files

# Usage
directory_path = input("Enter the path to the directory containing .al files: ")
output_csv = 'bc_objects.csv' #Only for quick access
db_name = 'bc_objects.db'#Changes here need to also be made in ai_rework_al_files.py

total_files, processed_files = process_directory(directory_path, output_csv, db_name)

print(f"CSV file has been created: {output_csv}")
print(f"SQLite database has been created: {db_name}")
print("Processing log has been created: processing_log.txt")
print("Error log has been created: error_log.txt")
print(f"Total .al files found: {total_files}")
print(f"Successfully processed files: {processed_files}")

if total_files != processed_files:
    print(f"Warning: {total_files - processed_files} files were not processed successfully. Check error_log.txt for details.", file=sys.stderr)
