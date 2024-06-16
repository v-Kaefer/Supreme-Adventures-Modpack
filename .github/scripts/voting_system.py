import json

class VotingSystem:
    def __init__(self, json_file_path):
        self.json_file_path = json_file_path
        self.votes = self.load_votes()

    def load_votes(self):
        try:
            with open(self.json_file_path, 'r') as file:
                return json.load(file).get("votes", {})
        except FileNotFoundError:
            return {}

    def save_votes(self):
        with open(self.json_file_path, 'w') as file:
            json.dump({"votes": self.votes}, file, indent=2)

    def vote_for_mod(self, mod_name, user):
        if mod_name in self.votes:
            if user not in self.votes[mod_name]:
                self.votes[mod_name].append(user)
        else:
            self.votes[mod_name] = [user]
        self.save_votes()

    def get_top_voted_mods(self, top_n=5):
        sorted_votes = sorted(self.votes.items(), key=lambda item: len(item[1]), reverse=True)
        return sorted_votes[:top_n]