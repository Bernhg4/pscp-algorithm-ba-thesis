import json
from source.jsonIO.jsonRW import to_json, from_json
from source.solvers.randomSolution import generate_random_solution
from source.validator.ownSolutionValidator import validate


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

    sampleSol = generate_random_solution(data_model)
    print(sampleSol)

    json_output = to_json(sampleSol)


    validate(data_model,sampleSol)

    #print the JSON output
    #print(json_output)
