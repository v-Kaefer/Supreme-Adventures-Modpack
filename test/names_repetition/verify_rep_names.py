import collections
import requests

def check_repetitions(names):
    counter = collections.Counter(names)
    repetitions = [name for name, count in counter.items() if count > 1]
    return repetitions

names = [
    "JEI",
    "REI",
    "EMI",
    "NEI",
    "JourneyMap",
    "Voxel's Map",
    "Antique Atlas",
    "Map Atlases",
    "FTB Chunks",
    "JEI",
    "REI",
    "EMI",
    "NEI",
    "JourneyMap",
    "Voxel's Map",
]

repetitions = check_repetitions(names)

if repetitions:
    # Create a pull request comment with the repeated names
    pull_request_comment = f"Repetitions found:\n\n"
    for name in repetitions:
        pull_request_comment += f"- {name}\n"

    # Make a POST request to the GitHub API to create a pull request comment
    url = "https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/comments"
    headers = {
        "Authorization": "Bearer {access_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "body": pull_request_comment
    }
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 201:
        print("Pull request comment created successfully.")
    else:
        print("Failed to create pull request comment.")
else:
    print("No repetitions found.")