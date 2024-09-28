import json
from source.jsonIO.jsonRW import solution_to_json, instance_from_json, solution_from_json, load_json_file, \
    write_json_file
from source.solvers.solutionGenerators import random_solution, demands_first
from source.validator.ownSolutionValidator import validate

if __name__ == "__main__":
    #load the toyInstance.json
    toy_instance_data = load_json_file('../data/PSCCP_Instance7.json')

    #converting the json to the data structure
    toy_instance = instance_from_json(toy_instance_data)

    #printing the model like in the problem description
    print(toy_instance)

    random_sample_sol = random_solution(toy_instance)
    demand_sample_sol = demands_first(toy_instance)
    demand_old_sample_sol = demands_first(toy_instance,True)
    demand_old_prior_sample_sol = demands_first(toy_instance,True, True)

    #toy_solution_data = load_json_file('../data/ToySolution.json')
    #sampleSol = solution_from_json(toy_solution_data)
    #print(random_sample_sol)

    #json_output = solution_to_json(random_sample_sol)
    #write_json_file(json_output, 'ToySolution.json')

    print("Random Solution:")
    validate(toy_instance,random_sample_sol)

    print("\nDemands first solution:")
    validate(toy_instance, demand_sample_sol)

    print("\nDemands first with history color solution:")
    validate(toy_instance, demand_old_sample_sol)

    print("\nDemands first with history color and priorization solution:")
    validate(toy_instance, demand_old_prior_sample_sol)
