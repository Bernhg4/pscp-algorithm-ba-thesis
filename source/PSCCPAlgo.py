import json
import sys

from source.jsonIO.jsonRW import solution_to_json, instance_from_json, solution_from_json, load_json_file, \
    write_json_file
from source.solvers.solutionGenerators import random_solution, demands_first
from source.validator.ownSolutionValidator import validate

if __name__ == "__main__":

    instance_file = '../data/PSCCP_Instance6.json'
    #instance_file = '../data/MyToyInstance.json'

    if len(sys.argv) == 3:
        instance_file = open(sys.argv[1])
        solution_file = open(sys.argv[2])

    #load the instance
    toy_instance_data = load_json_file(instance_file)

    #converting the json to the data structure
    toy_instance = instance_from_json(toy_instance_data)

    #printing the model like in the problem description
    print(toy_instance)

    random_sol = random_solution(toy_instance)
    demand_sol = demands_first(toy_instance)
    demand_old_sol = demands_first(toy_instance,True)
    demand_old_prior_sol = demands_first(toy_instance,True, True)
    demand_old_prior_due_sol = demands_first(toy_instance,True, True,True)

    write_json_file(solution_to_json(random_sol), instance_file.replace('.json','_random_sol.json'))
    write_json_file(solution_to_json(demand_sol), instance_file.replace('.json','_demand_sol.json'))
    write_json_file(solution_to_json(demand_old_sol), instance_file.replace('.json','_demand_old_sol.json'))
    write_json_file(solution_to_json(demand_old_prior_sol), instance_file.replace('.json','_demand_old_prior_sol.json'))
    write_json_file(solution_to_json(demand_old_prior_due_sol), instance_file.replace('.json','_demand_old_prior_due_sol.json'))

    print("Random Solution:")
    validate(toy_instance,random_sol)

    print("\nDemands first solution:")
    validate(toy_instance, demand_sol)

    print("\nDemands first with old color solution:")
    validate(toy_instance, demand_old_sol)

    print("\nDemands first with old color and prioritization color solution:")
    validate(toy_instance, demand_old_prior_sol)

    print("\nDemands first with old color and prioritization color & due_date solution:")
    validate(toy_instance, demand_old_prior_due_sol)
