# AI-Powered Business Central Code Refactoring (Alpha Version)

**DISCLAIMER: This is an alpha version of the tool. While it works for approximately 90% of all files, it still needs some polish and may encounter issues with certain edge cases. Use at your own risk. The authors and contributors of this project are not responsible for any damages or losses that may occur from using this tool. Always review the results carefully and maintain backups of your code before applying any changes.**

This project provides a set of tools to refactor and reorganize Business Central (BC) code using AI assistance. It helps in extracting namespaces, reworking existing code, and applying AI-suggested improvements to your BC codebase.

## Features

- Extract Business Central namespaces from existing code
- Rework and reorganize namespaces
- Apply AI-powered improvements to your codebase

## Prerequisites

- Python 3.7 or higher
- Required Python packages (install using `pip install -r requirements.txt`)
- Anthropic API key

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/bc-code-refactoring.git
   cd bc-code-refactoring
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root and add your Anthropic API key:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```

## Usage

### 0. Prepare Your Repository

Before starting the refactoring process, ensure you have a clean commit in your repository. This allows you to easily revert changes if anything goes wrong:

```
git add .
git commit -m "Clean state before refactoring"
```

### 1. Extract and Refactor Business Central Code

To extract, refactor, and improve your Business Central code:

1. Rename files in your codebase to include namespaces:
   ```
   python reworkNamespaces.py --input-dir /path/to/your/code --output-dir /path/to/output
   ```
   This script will rename your AL files to include namespaces based on their object types and names.

2. Extract base objects from a given Business Central base version:
   ```
   python extract_bc_namespaces.py --input-dir /path/to/base/version --output-file base_namespaces.json
   ```

3. Extract namespaces from your renamed code:
   ```
   python extract_bc_namespaces.py --input-dir /path/to/output --output-file your_namespaces.json
   ```

4. Apply AI-based improvements and add necessary `using` statements:
   ```
   python ai_rework_al_files.py --input-dir /path/to/output --output-dir /path/to/final_output --base-namespaces base_namespaces.json --your-namespaces your_namespaces.json
   ```
   This script uses AI to analyze your code, add necessary `using` statements, and apply other improvements based on the extracted namespaces.

This process will refactor your Business Central code by renaming files, extracting namespaces, and applying AI-suggested improvements. The final output will be in the specified `final_output` directory.

### 2. Handle Remaining Errors

After the AI-based refactoring, there may still be some errors or issues in your code. To address these:

1. Review the compiler errors in your development environment.
2. Manually fix any remaining issues, such as missing `using` statements or incorrect namespace references.
3. Test your code thoroughly to ensure all functionality is preserved.

If you encounter significant issues or are unsatisfied with the results, you can revert to the clean commit made before refactoring:

```
git reset --hard HEAD~1
```

Then, you can adjust your approach and repeat the process as needed.

## Tips for Working with the .env File

- Never commit your `.env` file to version control. It's already included in the `.gitignore` file.
- If you're working in a team, provide a `.env.example` file with placeholder values as a template.
- Ensure your Anthropic API key has the necessary permissions for the AI-based refactoring process.

## Troubleshooting

If you encounter issues with the AI-based refactoring:

1. Check that your Anthropic API key is correctly set in the `.env` file.
2. Ensure you have the latest version of the required dependencies.
3. Review the error messages and logs for any specific issues.
4. If problems persist, consider breaking down your codebase into smaller chunks for processing.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
