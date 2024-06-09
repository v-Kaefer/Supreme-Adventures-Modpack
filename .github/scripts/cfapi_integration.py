import os
import requests
import logging

class CurseForgeAPI:
    BASE_URL = "https://api.curseforge.com/v1"
    HEADERS = {
        "x-api-key": os.getenv("CURSEFORGE_API_KEY")
    }

    @staticmethod
    def search_mods(mod_name):
        url = f"{CurseForgeAPI.BASE_URL}/mods/search"
        params = {"query": mod_name}
        response = requests.get(url, headers=CurseForgeAPI.HEADERS, params=params)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def get_mod_details(mod_id):
        url = f"{CurseForgeAPI.BASE_URL}/mods/{mod_id}"
        response = requests.get(url, headers=CurseForgeAPI.HEADERS)
        response.raise_for_status()
        return response.json()

# Example usage
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        logging.error("Usage: python cfapi_integration.py <mod_name>")
        sys.exit(1)

    mod_name = sys.argv[1]
    api = CurseForgeAPI()
    mods = api.search_mods(mod_name)
    print(mods)
    if mods['data']:
        mod_id = mods['data'][0]['id']
        mod_details = api.get_mod_details(mod_id)
        print(mod_details)