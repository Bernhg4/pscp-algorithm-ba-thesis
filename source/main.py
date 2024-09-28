import json
from source.jsonIO.jsonRW import solution_to_json, instance_from_json, solution_from_json, load_json_file, \
    write_json_file
from source.solvers.randomSolution import generate_random_solution
from source.validator.ownSolutionValidator import validate

if __name__ == "__main__":
    #load the toyInstance.json
    toy_instance_data = load_json_file('../data/ToyInstance_ok.json')

    #converting the json to the data structure
    toy_instance = instance_from_json(toy_instance_data)

    #printing the model like in the problem description
    print(toy_instance)

    #sampleSol = generate_random_solution(toy_instance)

    # Toy solution: Demand 1: 4 von 5, Demand 2: ok, Demand 3: 1 zu spät
    # Demand violations 1, constraint violation 1, color changes 7
    toy_solution_data = load_json_file('../data/ToySolution.json')
    sampleSol = solution_from_json(toy_solution_data)
    print(sampleSol)

    json_output = solution_to_json(sampleSol)
    write_json_file(json_output, 'ToySolution.json')

    validate(toy_instance,sampleSol)
