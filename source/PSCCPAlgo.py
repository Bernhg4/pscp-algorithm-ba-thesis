import json
import sys

from source.jsonIO.json_rw import solution_to_json, instance_from_json, solution_from_json, load_json_file, \
    write_json_file
from source.solvers.solutionGenerators import random_solution, demands_first, demands_reverse,  \
    heuristic_solution
from source.validator.ownSolutionValidator import validate
from test.data_generators.test_instance_generator import gen_tiny_instance1, gen_small_instance1, gen_medium_instance1, \
    gen_big_instance1, gen_tiny_instance2, gen_small_instance2, gen_medium_instance2, gen_big_instance2
from test.data_generators.test_solution_generator import gen_tiny_solution1, gen_small_solution1, gen_medium_solution1, \
    gen_big_solution1, gen_tiny_solution2, gen_small_solution2, gen_medium_solution2, gen_big_solution2

if __name__ == "__main__":

    instance_file = '../data/PSCCP_Instance3.json'
    #instance_file = '../data/ToyInstance_ok.json'
    time_limit_seconds = 60

    if len(sys.argv) == 3:
        instance_file = open(sys.argv[1])
        solution_file = open(sys.argv[2])

    #load the instance
    toy_instance_data = load_json_file(instance_file)

    #converting the json to the data structure
    toy_instance = instance_from_json(toy_instance_data)

    #printing the model like in the problem description
    print(toy_instance)

    random_sol = random_solution(toy_instance,time_limit_seconds)
    demand_sol = demands_first(toy_instance,time_limit_seconds)
    reverse_sol = demands_reverse(toy_instance,time_limit_seconds)

    demand_old_sol = demands_first(toy_instance,time_limit_seconds,True)
    demand_old_prior_sol = demands_first(toy_instance,time_limit_seconds,True, True)
    demand_old_prior_due_sol = demands_first(toy_instance,time_limit_seconds,True, True,True)
    heuristic_sol = heuristic_solution(toy_instance,time_limit_seconds,10)

    write_json_file(solution_to_json(random_sol),instance_file.replace('.json','_random_sol.json'))
    write_json_file(solution_to_json(demand_sol),instance_file.replace('.json','_demand_sol.json'))
    write_json_file(solution_to_json(demand_old_sol),instance_file.replace('.json','_demand_old_sol.json'))
    write_json_file(solution_to_json(demand_old_prior_sol),instance_file.replace('.json','_demand_old_prior_sol.json'))
    write_json_file(solution_to_json(demand_old_prior_due_sol),instance_file.replace('.json','_demand_old_prior_due_sol.json'))
    write_json_file(solution_to_json(reverse_sol),instance_file.replace('.json','_reverse_sol.json'))
    write_json_file(solution_to_json(heuristic_sol),instance_file.replace('.json','_heuristic_sol.json'))

    print("Random Solution:")
    validate(toy_instance,random_sol)

    print("\nDemands first solution:")
    validate(toy_instance, demand_sol)

    print("\nDemands first with old color solution:")
    validate(toy_instance, demand_old_sol)

    print("\nReverse demands solution:")
    validate(toy_instance, reverse_sol)

    print("\nDemands first with old color and prioritization color solution:")
    validate(toy_instance, demand_old_prior_sol)

    print("\nDemands first with old color and prioritization color & due_date solution:")
    validate(toy_instance, demand_old_prior_due_sol)

    print("\nHeuristic solution:")
    validate(toy_instance, heuristic_sol)


