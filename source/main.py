import json
from source.jsonIO.jsonRW import to_json, from_json
from source.solvers.randomSolution import generate_random_solution


#function for reading a json file
def load_json_file(filepath):
    file = open(filepath, 'r')
    return json.load(file)

if __name__ == "__main__":
    #load the toyInstance.json
    data = load_json_file('../data/ToyInstance_ok.json')

    #converting the json to the data structure
    data_model = from_json(data)

    #printing the model like in the problem description
    print(data_model)

    rounds = generate_random_solution(data_model)

    json_output = to_json(rounds)

    #print the JSON output
    print(json_output)
