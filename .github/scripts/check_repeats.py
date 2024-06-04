import re
from collections import defaultdict
import os

def find_repeats(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.readlines()

    # Extract all mod names with their line numbers
    mod_names = []
    for line_number, line in enumerate(content, start=1):
        matches = re.findall(r'- ([\w\s\[\]\?]+)', line)
        for match in matches:
            mod_names.append((match.strip(), line_number))

    # Find duplicates
    name_count = defaultdict(list)
    for name, line_number in mod_names:
        name_count[name].append(line_number)


    # Report duplicates
    duplicates = {name: lines for name, lines in name_count.items() if len(lines) > 1}
    return duplicates

def main():
    file_path = 'modslist.md'
    duplicates = find_repeats(file_path)

    summary_file = os.getenv('GITHUB_STEP_SUMMARY', None)
    if duplicates:
        output = "Found repeated names:\n"
        for name, lines in duplicates.items():
            output += f"{name} is repeated on lines: {', '.join(map(str, lines))}\n"
        print(output)
        
        if summary_file:
            with open(summary_file, 'a') as summary:
                summary.write(output)
        
        # Create annotations for GitHub Actions
        for name, lines in duplicates.items():
            for line in lines:
                print(f"::error file={file_path},line={line}::{name} is repeated")
        
        exit(1)  # Exit with error code to fail the action
    else:
        print("No repeated names found.")
        if summary_file:
            with open(summary_file, 'a') as summary:
                summary.write("No repeated names found.\n")

if __name__ == "__main__":
    main()