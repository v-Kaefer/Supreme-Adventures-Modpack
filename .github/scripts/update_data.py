import json

# Load existing data
with open('data.json', 'r') as file:
    data = json.load(file)

# Update the data
data['new_key'] = 'new_value'

# Save updated data
with open('data.json', 'w') as file:
    json.dump(data, file, indent=2)
