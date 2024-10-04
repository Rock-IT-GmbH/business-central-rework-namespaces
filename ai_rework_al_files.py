import os
import json
import requests
import sqlite3
from dotenv import load_dotenv
from tqdm import tqdm

# Load environment variables from .env file
load_dotenv()

def process_file_with_claude(file_path, prompt, api_key):
    with open(file_path, 'r', encoding='utf-8') as file:
        file_content = file.read()

    headers = {
        "Content-Type": "application/json",
        "X-API-Key": api_key,
        "anthropic-version": "2023-06-01",
    }

    data = {
        #"model": "claude-3-5-sonnet-20240620",
        "model": "claude-3-haiku-20240307",
        "max_tokens": 4096,
        "system": prompt,
        "messages": [
            {"role": "user", "content": file_content}
        ]
    }

    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers=headers,
        json=data
    )

    if response.status_code == 200:
        ai_response = response.json()['content'][0]['text']
        try:
            return json.loads(ai_response)
        except json.JSONDecodeError:
            raise ValueError("Claude's response is not in valid JSON format")
    else:
        raise Exception(f"API request failed with status code {response.status_code}: {response.text}")

def get_namespace_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if line.strip().startswith('namespace'):
                return line.strip()
    return None

def get_object_namespace(cursor, object_type, object_name):
    cursor.execute(
        "SELECT namespace FROM bc_objects WHERE object_type = ? AND object_name = ?",
        (object_type, object_name)
    )
    result = cursor.fetchone()
    return result[0] if result else None

def generate_using_statements(objects, cursor):
    usings = set()
    for obj in objects:
        namespace = get_object_namespace(cursor, obj['object_type'], obj['object_name'])
        if namespace:
            usings.add(f"using {namespace};")
    return sorted(list(usings))

def update_file_with_usings(file_path, using_statements):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    namespace_index = next((i for i, line in enumerate(lines) if line.strip().startswith('namespace')), -1)

    if namespace_index != -1:
        insert_index = namespace_index + 1
        using_statements.insert(0, '')  # Add a blank line before usings
        lines[insert_index:insert_index] = [f"{stmt}\n" for stmt in using_statements]

        with open(file_path, 'w', encoding='utf-8') as file:
            file.writelines(lines)
        return True
    return False

def process_folder(folder_path, prompt, db_path):
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    total_files = sum(1 for root, _, files in os.walk(folder_path) for file in files if file.endswith('.al'))
    processed_files = 0
    total_objects = 0

    with tqdm(total=total_files, desc="Processing files", unit="file") as pbar:
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.endswith('.al'):
                    file_path = os.path.join(root, file)
                    try:
                        # Check if the file has a namespace
                        if not get_namespace_from_file(file_path):
                            pbar.write(f"Skipping {file_path} - No namespace found")
                            continue

                        # Extract objects
                        file_results = process_file_with_claude(file_path, prompt, api_key)
                        total_objects += len(file_results)

                        # Generate and add using statements
                        using_statements = generate_using_statements(file_results, cursor)
                        if using_statements:
                            if update_file_with_usings(file_path, using_statements):
                                pbar.write(f"Updated {file_path} with using statements")
                            else:
                                pbar.write(f"Failed to update {file_path} with using statements")

                        processed_files += 1
                        pbar.update(1)

                    except Exception as e:
                        pbar.write(f"Error processing {file_path}: {str(e)}")

    conn.close()
    return processed_files, total_objects

def main():
    prompt = """
    Analyze the following AL code from Business Central Dynamics and list all referenced objects
    (pages, tables, reports, codeunits, queries, enums, interfaces) with their respective names. Ignore every already existing "using" line.
    Return your response as a JSON array of objects, where each object has two properties:
    'object_type' (lowercase) and 'object_name' (without quotes).
    For example:
    [
        {"object_type": "page", "object_name": "Customer List"},
        {"object_type": "table", "object_name": "Customer"},
    ]
    Only include the JSON array in your response, nothing else.
    """

    folder_path = input("Enter the path to the folder containing AL files: ")
    db_path = 'bc_objects.db'

    try:
        processed_files, total_objects = process_folder(folder_path, prompt, db_path)

        print(f"\nSummary:")
        print(f"Total files processed: {processed_files}")
        print(f"Total objects found: {total_objects}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
