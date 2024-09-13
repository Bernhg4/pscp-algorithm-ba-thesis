import json
from models.baseModels import from_json

def load_json_file(filepath):
    file = open(filepath, 'r')
    return json.load(file)

if __name__ == "__main__":
    # Load the JSON data from a file
    data = load_json_file('data/ToyInstance - Ohne Kommentare.json')

    # Convert the JSON data into the DataModel class
    data_model = from_json(data)

    # Print the DataModel (calls the __str__ method)
    print(data_model)
