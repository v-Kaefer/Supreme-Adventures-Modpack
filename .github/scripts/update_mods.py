import os
import requests
import json
import re

# Load the API key from the environment
API_KEY = os.getenv('CURSEFORGE_API_KEY')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_REPO = 'v-Kaefer/Supreme-Adventures-Modpack'  # Replace with your repository
VOTES_FILE = 'mod_votes.json'
OUTPUT_FILE = 'mods_list.json'

headers = {
    'x-api-key': API_KEY,
    'Content-Type': 'application/json'
}

github_headers = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
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

def load_votes():
    if os.path.exists(VOTES_FILE):
        with open(VOTES_FILE, 'r') as f:
            return json.load(f)
    return {"mods": []}

def save_votes(votes_data):
    with open(VOTES_FILE, 'w') as f:
        json.dump(votes_data, f, indent=2)

def fetch_github_issues():
    url = f'https://api.github.com/repos/{GITHUB_REPO}/issues'
    response = requests.get(url, headers=github_headers)
    return response.json()

def parse_issue_body(body):
    mod_name = re.search(r'\*\*Mod Name\*\*:\n<!-- (.*?) -->', body)
    mod_link = re.search(r'\*\*Mod Link\*\*:\n<!-- (.*?) -->', body)
    requested_by = re.search(r'\*\*Requested By\*\*:\n<!-- (.*?) -->', body)
    return {
        'name': mod_name.group(1).strip() if mod_name else '',
        'link': mod_link.group(1).strip() if mod_link else '',
        'requested_by': requested_by.group(1).strip() if requested_by else ''
    }

def update_votes_from_issues():
    issues = fetch_github_issues()
    votes_data = load_votes()

    for issue in issues:
        if ':sparkles: mod request' in [label['name'] for label in issue['labels']]:
            parsed_data = parse_issue_body(issue['body'])
            mod_name = parsed_data['name']
            user = parsed_data['requested_by']

            mod_entry = next((mod for mod in votes_data['mods'] if mod['name'] == mod_name), None)
            if mod_entry:
                if user not in mod_entry['usernames']:
                    mod_entry['votes'] += 1
                    mod_entry['usernames'].append(user)
            else:
                votes_data['mods'].append({
                    'name': mod_name,
                    'votes': 1,
                    'versions': [],
                    'usernames': [user]
                })

    save_votes(votes_data)

def update_mod_list():
    update_votes_from_issues()
    votes_data = load_votes()
    mods_data = []
    mod_ids = []

    for mod_entry in votes_data['mods']:
        mod_name = mod_entry['name']
        search_results = search_mods(mod_name)
        if search_results['data']:
            mod = search_results['data'][0]
            mod_id = mod['id']
            mod_name = mod['name']
            versions = get_mod_versions(mod_id)
            mod_info = {
                'mod_name': mod_name,
                'mod_id': mod_id,
                'versions': [],
                'votes': mod_entry['votes'],
                'usernames': mod_entry['usernames']
            }
            for version in versions['data']:
                if 'gameVersions' in version:
                    mod_info['versions'].append({
                        'version': version['displayName'],
                        'minecraft_versions': version['gameVersions']
                    })
            mods_data.append(mod_info)
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
