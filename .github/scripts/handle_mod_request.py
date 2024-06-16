import os
import requests
import json

# Load the API key from the environment
API_KEY = os.getenv('CURSEFORGE_API_KEY')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_REPO = 'v-Kaefer/Supreme-Adventures-Modpacks'  # Replace with your GitHub repo

MODS_LIST_FILE = 'mods_list.json'
OUTPUT_FILE = 'mods_list.json'

headers = {
    'x-api-key': API_KEY,
    'Content-Type': 'application/json'
}

def search_mods(mod_name):
    params = {
        'gameId': 432,
        'searchFilter': mod_name,
        'pageSize': 1
    }
    url = 'https://api.curseforge.com/v1/mods/search'
    response = requests.get(url, headers=headers, params=params)
    return response.json()

def get_mod_versions(mod_id):
    url = f'https://api.curseforge.com/v1/mods/{mod_id}/files'
    response = requests.get(url, headers=headers)
    return response.json()

def get_mods_by_ids(mod_ids):
    url = 'https://api.curseforge.com/v1/mods'
    body = {
        'modIds': mod_ids,
        'filterPcOnly': True
    }
    response = requests.post(url, headers=headers, json=body)
    return response.json()

def get_mod_description(mod_id):
    url = f'https://api.curseforge.com/v1/mods/{mod_id}/description'
    response = requests.get(url, headers=headers)
    return response.json()

def get_minecraft_versions():
    url = 'https://api.curseforge.com/v1/minecraft/version'
    response = requests.get(url, headers=headers)
    return response.json()

def get_mod_loaders():
    url = 'https://api.curseforge.com/v1/minecraft/modloader'
    response = requests.get(url, headers=headers)
    return response.json()

def get_github_issues():
    url = f'https://api.github.com/repos/{GITHUB_REPO}/issues'
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    response = requests.get(url, headers=headers)
    return response.json()

def read_mods_list():
    if os.path.exists(MODS_LIST_FILE):
        with open(MODS_LIST_FILE, 'r') as file:
            return json.load(file)
    return []

def update_mod_list():
    mods_data = []
    mod_ids = []
    mods_list = read_mods_list()

    for mod in mods_list:
        mod_name = mod['mod_name']
        search_results = search_mods(mod_name)
        if search_results['data']:
            mod_info = search_results['data'][0]
            mod_id = mod_info['id']
            mod_name = mod_info['name']
            versions = get_mod_versions(mod_id)
            mod_details = {
                'mod_name': mod_name,
                'mod_id': mod_id,
                'versions': [],
                'requested_by': mod['requested_by'],
                'votes': mod['votes']
            }
            for version in versions['data']:
                if 'gameVersions' in version:
                    mod_details['versions'].append({
                        'version': version['displayName'],
                        'minecraft_versions': version['gameVersions']
                    })
            mods_data.append(mod_details)
            mod_ids.append(mod_id)

    mod_details = get_mods_by_ids(mod_ids)
    for mod_detail in mod_details['data']:
        mod_id = mod_detail['id']
        for mod in mods_data:
            if mod['mod_id'] == mod_id:
                mod['mod_details'] = mod_detail

    for mod in mods_data:
        mod_description = get_mod_description(mod['mod_id'])
        mod['description'] = mod_description

    minecraft_versions = get_minecraft_versions()
    mod_loaders = get_mod_loaders()

    with open(OUTPUT_FILE, 'w') as f:
        output = {
            'mods': mods_data,
            'minecraft_versions': minecraft_versions,
            'mod_loaders': mod_loaders
        }
        json.dump(output, f, indent=2)

if __name__ == "__main__":
    update_mod_list()
