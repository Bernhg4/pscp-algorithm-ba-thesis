import json
import sys

from source.jsonIO.json_rw import solution_to_json, instance_from_json, solution_from_json, load_json_file, \
    write_json_file
from source.solvers.solutionGenerators import random_solution, demands_first, demands_reverse, primitive_solution
from source.validator.ownSolutionValidator import validate
from test.data_generators.test_instance_generator import gen_tiny_instance1, gen_small_instance1, gen_medium_instance1, \
    gen_big_instance1, gen_tiny_instance2, gen_small_instance2, gen_medium_instance2, gen_big_instance2
from test.data_generators.test_solution_generator import gen_tiny_solution1, gen_small_solution1, gen_medium_solution1, \
    gen_big_solution1, gen_tiny_solution2, gen_small_solution2, gen_medium_solution2, gen_big_solution2

if __name__ == "__main__":

    instance_file = '../data/PSCCP_Instance1.json'
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
    reverse_sol = demands_reverse(toy_instance)
    primitive_sol = primitive_solution(toy_instance)

    demand_old_sol = demands_first(toy_instance,True)
    demand_old_prior_sol = demands_first(toy_instance,True, True)
    demand_old_prior_due_sol = demands_first(toy_instance,True, True,True)

    write_json_file(solution_to_json(random_sol),instance_file.replace('.json','_random_sol.json'))
    write_json_file(solution_to_json(demand_sol),instance_file.replace('.json','_demand_sol.json'))
    write_json_file(solution_to_json(demand_old_sol),instance_file.replace('.json','_demand_old_sol.json'))
    write_json_file(solution_to_json(demand_old_prior_sol),instance_file.replace('.json','_demand_old_prior_sol.json'))
    write_json_file(solution_to_json(demand_old_prior_due_sol),instance_file.replace('.json','_demand_old_prior_due_sol.json'))
    write_json_file(solution_to_json(reverse_sol),instance_file.replace('.json','_reverse_sol.json'))
    write_json_file(solution_to_json(reverse_sol),instance_file.replace('.json','_primitive_sol.json'))

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

    print("Primitive Solution:")
    validate(toy_instance, primitive_sol)


