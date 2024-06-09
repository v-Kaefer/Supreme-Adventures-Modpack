import json
import os
import requests
import logging
from cfapi_integration import CurseForgeAPI
from github import Github

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ModRequestHandler:
    def __init__(self, json_file_path, votes_file_path, github_token):
        self.json_file_path = json_file_path
        self.votes_file_path = votes_file_path
        self.github = Github(github_token)
        self.mods = self.load_mods()
        self.votes = self.load_votes()

    def load_mods(self):
        try:
            with open(self.json_file_path, 'r') as file:
                return json.load(file).get("mods", [])
        except FileNotFoundError:
            logging.warning(f"{self.json_file_path} not found. Starting with an empty list.")
            return []
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding JSON from {self.json_file_path}: {e}")
            return []

    def load_votes(self):
        try:
            with open(self.votes_file_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            logging.warning(f"{self.votes_file_path} not found. Starting with an empty dictionary.")
            return {}
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding JSON from {self.votes_file_path}: {e}")
            return {}

    def save_mods(self):
        try:
            with open(self.json_file_path, 'w') as file:
                json.dump({"mods": self.mods}, file, indent=2)
        except IOError as e:
            logging.error(f"Error writing to {self.json_file_path}: {e}")

    def save_votes(self):
        try:
            with open(self.votes_file_path, 'w') as file:
                json.dump(self.votes, file, indent=2)
        except IOError as e:
            logging.error(f"Error writing to {self.votes_file_path}: {e}")

    def is_mod_in_list(self, mod_name):
        return any(mod['name'].lower() == mod_name.lower() for mod in self.mods)

    def add_mod(self, mod_name, mod_details):
        if not self.is_mod_in_list(mod_name):
            self.mods.append(mod_details)
            self.save_mods()
            return True
        return False

    def add_vote(self, mod_name, user):
        if mod_name not in self.votes:
            self.votes[mod_name] = []
        if user not in self.votes[mod_name]:
            self.votes[mod_name].append(user)
            self.save_votes()
            return True
        return False

    def handle_mod_request(self, issue):
        mod_name = issue.title.replace("[MOD REQUEST] ", "").strip()
        user = issue.user.login
        api = CurseForgeAPI()

        if self.is_mod_in_list(mod_name):
            self.add_vote(mod_name, user)
            issue.create_comment(f"Mod '{mod_name}' is already in the list. Your vote has been added.")
            logging.info(f"Mod '{mod_name}' is already in the list. Vote added for user '{user}'.")
            return

        try:
            mods = api.search_mods(mod_name)
            if mods['data']:
                mod_id = mods['data'][0]['id']
                mod_details = api.get_mod_details(mod_id)
                mod_info = {
                    "name": mod_details['data']['name'],
                    "id": mod_id,
                    "version": mod_details['data']['latestFiles'][0]['displayName'],
                    "mcVersion": mod_details['data']['latestFiles'][0]['gameVersions'][0],
                    "modloader": mod_details['data']['latestFiles'][0]['modLoaders'][0]
                }
                if self.add_mod(mod_name, mod_info):
                    self.add_vote(mod_name, user)
                    issue.create_comment(f"Mod '{mod_name}' added successfully. Your vote has been added.")
                    logging.info(f"Mod '{mod_name}' added successfully. Vote added for user '{user}'.")
                else:
                    issue.create_comment(f"Mod '{mod_name}' is already in the list. Your vote has been added.")
                    logging.info(f"Mod '{mod_name}' is already in the list. Vote added for user '{user}'.")
            else:
                issue.create_comment(f"Mod '{mod_name}' not found on CurseForge.")
                logging.info(f"Mod '{mod_name}' not found on CurseForge.")
        except requests.RequestException as e:
            logging.error(f"Error fetching mod details from CurseForge: {e}")

# Example usage
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        logging.error("Usage: python mod_request_handler.py <issue_number>")
        sys.exit(1)

    issue_number = int(sys.argv[1])
    github_token = os.getenv("GITHUB_TOKEN")
    repo_name = os.getenv("GITHUB_REPOSITORY")

    handler = ModRequestHandler(".github/scripts/modslist.json", ".github/scripts/votes.json", github_token)
    repo = handler.github.get_repo(repo_name)
    issue = repo.get_issue(number=issue_number)
    handler.handle_mod_request(issue)