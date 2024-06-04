import re
import json
import os

class ModAddonClassifier:

    class Type:
        MOD = "MOD"
        ADDON = "ADDON"

    class mcVersion:
        v1_12 = "v1_12"
        v1_13 = "v1_13"
        v1_14 = "v1_14"
        v1_15 = "v1_15"
        v1_16 = "v1_16"
        v1_17 = "v1_17"
        v1_18 = "v1_18"
        v1_19 = "v1_19"
        v1_20 = "v1_20"

    class Modloader:
        FORGE = "FORGE"
        CURSEFORGE = "CURSEFORGE"
        FABRIC = "FABRIC"
        QUILT = "QUILT"
        NEOFORGE = "NEOFORGE"

    class Mod:
        def __init__(self, name, version, mc_version, modloader):
            self.type = ModAddonClassifier.Type.MOD
            self.name = name
            self.version = version
            self.mc_version = mc_version
            self.modloader = modloader

        def to_dict(self):
            return {
                "name": self.name,
                "type": self.type,
                "version": self.version,
                "mcVersion": self.mc_version,
                "modloader": self.modloader
            }

    class Addon:
        def __init__(self, name, version, mc_version, modloader):
            self.type = ModAddonClassifier.Type.ADDON
            self.name = name
            self.version = version
            self.mc_version = mc_version
            self.modloader = modloader

        def to_dict(self):
            return {
                "name": self.name,
                "type": self.type,
                "version": self.version,
                "mcVersion": self.mc_version,
                "modloader": self.modloader
            }

    def __init__(self, md_file_path, json_file_path):
        self.md_file_path = md_file_path
        self.json_file_path = json_file_path
        self.mods = {}
        self.addons = {}

    def parse(self):
        main_mod_pattern = re.compile(r"^\*\s*(.+?)(?:\s*\[(.*?),?\s*(.*?),?\s*(.*?)?\])?$")
        sub_addon_pattern = re.compile(r"^-\s*(.+?)(?:\s*\[(.*?),?\s*(.*?),?\s*(.*?)?\])?$")

        start_parsing = False

        with open(self.md_file_path, 'r') as file:
            for line in file:
                if line.strip() == "## Mods/Addons:":
                    start_parsing = True
                    continue

                if not start_parsing:
                    continue

                main_mod_match = main_mod_pattern.match(line)
                sub_addon_match = sub_addon_pattern.match(line)

                if main_mod_match:
                    name = main_mod_match.group(1).strip()
                    version = main_mod_match.group(2).strip() if main_mod_match.group(2) else None
                    mc_ver = self.parse_mc_version(main_mod_match.group(3).strip()) if main_mod_match.group(3) else None
                    modloader = self.parse_modloader(main_mod_match.group(4).strip()) if main_mod_match.group(4) else None

                    mod = self.Mod(name, version, mc_ver, modloader)
                    self.mods[name] = mod

                elif sub_addon_match:
                    name = sub_addon_match.group(1).strip()
                    version = sub_addon_match.group(2).strip() if sub_addon_match.group(2) else None
                    mc_ver = self.parse_mc_version(sub_addon_match.group(3).strip()) if sub_addon_match.group(3) else None
                    modloader = self.parse_modloader(sub_addon_match.group(4).strip()) if sub_addon_match.group(4) else None

                    addon = self.Addon(name, version, mc_ver, modloader)
                    self.addons[name] = addon

    def parse_mc_version(self, value):
        try:
            return getattr(self.mcVersion, value)
        except AttributeError:
            return None

    def parse_modloader(self, value):
        try:
            return getattr(self.Modloader, value.upper())
        except AttributeError:
            return None

    def read_json_file(self):
        if os.path.exists(self.json_file_path):
            with open(self.json_file_path, 'r') as file:
                return json.load(file)
        return {"mods": []}

    def write_json_file(self, data):
        with open(self.json_file_path, 'w') as file:
            json.dump(data, file, indent=2)

    def update_json_data(self, json_data):
        mods_array = json_data.get("mods", [])

        for mod in self.mods.values():
            mods_array.append(mod.to_dict())

        for addon in self.addons.values():
            mods_array.append(addon.to_dict())

        json_data["mods"] = mods_array

    def run(self):
        self.parse()
        json_data = self.read_json_file()
        self.update_json_data(json_data)
        self.write_json_file(json_data)

if __name__ == "__main__":
    classifier = ModAddonClassifier("modslist.md", "modslist.json")
    classifier.run()