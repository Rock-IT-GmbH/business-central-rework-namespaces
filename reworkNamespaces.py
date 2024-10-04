import os
import re
import time

def process_al_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    # Extract the some matching string from your file to create dynamics namespaces or just use a default one. Optional you could setup a namespace schema and let AI read the file and create the namespaces.
    match = re.search(r'\.\w+(\.\w+)?', content)
    if match:
        namespace = match.group(0)
    else:
        namespace = "DefaultNamespace"

    # Add namespace at the top of the file
    content = f"namespace {namespace};\n\n" + content

    # Remove your prefixes.
    # TODO: find a solution to deal with table and page extensions. Currently needs manual rework.
    content = re.sub(r'\prefix', '', content)

    # Write the modified content back to the file
    with open(file_path, 'w') as file:
        file.write(content)

    # If the source file starts with with a prefix, rename the file without the first two letters
    if os.path.basename(file_path).startswith("prefix"):#CHANGE PREFIX TO YOUR PREFIX
        new_file_path = os.path.join(os.path.dirname(file_path), os.path.basename(file_path)[2:])
        os.rename(file_path, new_file_path)

def process_directory(directory):
    total_files = sum([len(files) for r, d, files in os.walk(directory) if any(f.endswith('.al') for f in files)])
    processed_files = 0

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".al"):
                file_path = os.path.join(root, file)
                processed_files += 1
                progress = (processed_files / total_files) * 100
                print_loading(progress, file_path)
                process_al_file(file_path)
                time.sleep(0.1)  # Small delay to make the loading animation visible

    print("\nProcessing complete.")

def print_loading(progress, current_file):
    bar_length = 20
    filled_length = int(bar_length * progress // 100)
    _ = '=' * filled_length + '-' * (bar_length - filled_length)
    #TODO: Replace loading bar logic with a progress bar analog to AI process

if __name__ == "__main__":
    directory = input("Enter the directory path to process: ")
    process_directory(directory)
