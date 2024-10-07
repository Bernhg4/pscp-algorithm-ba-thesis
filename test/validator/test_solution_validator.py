import io
import json
import sys
from unittest import TestCase
from contextlib import redirect_stdout

from source.jsonIO.jsonRW import load_json_file, instance_from_json, instance_to_json, solution_to_json, write_json_file
from source.solution_validator import validate_solution
from source.solvers.solutionGenerators import random_solution, demands_first, demands_reverse
from source.validator.ownSolutionValidator import validate


class Test(TestCase):
    def test_validate_solution_instance1(self):

        instance_file_path = '../../data/PSCCP_Instance1.json'

        instance_data = load_json_file(instance_file_path)

        toy_instance = instance_from_json(instance_data)

        random_sol = random_solution(toy_instance)
        demand_sol = demands_first(toy_instance)
        reverse_sol = demands_reverse(toy_instance)
        demand_old_prior_due_sol = demands_first(toy_instance, True, True, True)

        write_json_file(solution_to_json(random_sol), instance_file_path.replace('.json', '_random_sol.json'))
        write_json_file(solution_to_json(demand_sol), instance_file_path.replace('.json', '_demand_sol.json'))
        write_json_file(solution_to_json(demand_old_prior_due_sol),instance_file_path.replace('.json', '_demand_old_prior_due_sol.json'))
        write_json_file(solution_to_json(reverse_sol), instance_file_path.replace('.json', '_reverse_sol.json'))

        f = io.StringIO()
        with redirect_stdout(f), open(instance_file_path, 'r') as instance_file, \
                    open(instance_file_path.replace('.json', '_random_sol.json'), 'r') as solution_file:
            validate_solution(json.load(instance_file), json.load(solution_file))
        output = f.getvalue()

        f = io.StringIO()
        with redirect_stdout(f):
            validate(toy_instance, random_sol)
        output2 = f.getvalue()

        print(output2)

        self.assertEqual(output, output2, "Outputs of validate and validate_solution differ")


