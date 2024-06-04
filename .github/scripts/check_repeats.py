import re
from collections import defaultdict
import os

def find_repeats(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Extract all mod names
    mod_names = re.findall(r'- ([\w\s\[\]\?]+)', content)

    # Find duplicates
    name_count = defaultdict(list)
    for index, name in enumerate(mod_names):
        name_count[name.strip()].append(index + 1)

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
        
        exit(1)  # Exit with error code to fail the action
    else:
        print("No repeated names found.")
        if summary_file:
            with open(summary_file, 'a') as summary:
                summary.write("No repeated names found.\n")

if __name__ == "__main__":
    main()