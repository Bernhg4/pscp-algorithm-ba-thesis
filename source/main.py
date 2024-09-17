import json
from source.jsonIO.jsonRW import to_json, from_json
from source.models.baseModels import RoundSolution


#function for reading a json file
def load_json_file(filepath):
    file = open(filepath, 'r')
    return json.load(file)

if __name__ == "__main__":
    #load the toyInstance.json
    data = load_json_file('data/ToyInstance - Ohne Kommentare.json')

    #converting the json to the data structure
    data_model = from_json(data)

    #printing the model like in the problem description
    print(data_model)

    rounds = [
        RoundSolution([1, 1, 1, 3]),
        RoundSolution([2, 2, 2, 3, 3]),
        RoundSolution([1, 1, 2, 3, 2])
    ]

    json_output = to_json(rounds)

    # Print the JSON output
    print(json_output)
