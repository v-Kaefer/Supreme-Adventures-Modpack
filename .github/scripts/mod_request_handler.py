import json
import os
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ModRequestHandler:
    def __init__(self, json_file_path):
        self.json_file_path = json_file_path
        self.mods = self.load_mods()

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

    def save_mods(self):
        try:
            with open(self.json_file_path, 'w') as file:
                json.dump({"mods": self.mods}, file, indent=2)
        except IOError as e:
            logging.error(f"Error writing to {self.json_file_path}: {e}")

    def is_mod_in_list(self, mod_name):
        return any(mod['name'].lower() == mod_name.lower() for mod in self.mods)

    def add_mod(self, mod_name, mod_details):
        if not self.is_mod_in_list(mod_name):
            self.mods.append(mod_details)
            self.save_mods()
            return True
        return False

    def handle_mod_request(self, mod_name):
        api = CurseForgeAPI()
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
                    logging.info(f"Mod '{mod_name}' added successfully.")
                else:
                    logging.info(f"Mod '{mod_name}' is already in the list.")
            else:
                logging.info(f"Mod '{mod_name}' not found on CurseForge.")
        except requests.RequestException as e:
            logging.error(f"Error fetching mod details from CurseForge: {e}")

class CurseForgeAPI:
    def __init__(self):
        self.api_key = os.getenv('CURSEFORGE_API_KEY')
        self.base_url = 'https://api.curseforge.com'

    def search_mods(self, mod_name):
        headers = {'x-api-key': self.api_key}
        response = requests.get(f"{self.base_url}/v1/mods/search?gameId=432&searchFilter={mod_name}", headers=headers)
        response.raise_for_status()
        return response.json()

    def get_mod_details(self, mod_id):
        headers = {'x-api-key': self.api_key}
        response = requests.get(f"{self.base_url}/v1/mods/{mod_id}", headers=headers)
        response.raise_for_status()
        return response.json()

# Example usage
if __name__ == "__main__":
    handler = ModRequestHandler(".github/scripts/modslist.json")
    handler.handle_mod_request("Sodium")