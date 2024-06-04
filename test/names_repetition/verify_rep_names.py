import collections
import requests
import os

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

    # Fetch all pull requests
    url = "https://api.github.com/repos/v-Kaefer/Supreme-Adventures-Modpack/pulls"
    headers = {
        "Authorization": f"Bearer {os.getenv('MODS_NAME_REP')}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    pull_requests = response.json()

    # For each pull request
    for pr in pull_requests:
        # Get the pull request number
        issue_number = pr["number"]

        # Perform your check for repetitions
        repetitions = check_repetitions(names)

        if repetitions:
            # Create a pull request comment with the repeated names
            pull_request_comment = f"Repetitions found:\n\n"
            for name in repetitions:
                pull_request_comment += f"- {name}\n"

            # Make a POST request to the GitHub API to create a pull request comment
            url = f"https://api.github.com/repos/v-Kaefer/Supreme-Adventures-Modpack/issues/{issue_number}/comments"
            data = {
                "body": pull_request_comment
            }
            response = requests.post(url, headers=headers, json=data)

            if response.status_code == 201:
                print(f"Pull request comment created successfully for PR #{issue_number}.")
            else:
                print(f"Failed to create pull request comment for PR #{issue_number}.")
        else:
            print(f"No repetitions found for PR #{issue_number}.")

print(response.json())