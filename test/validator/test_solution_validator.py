import io
import json
import sys
from unittest import TestCase
from contextlib import redirect_stdout

from source.jsonIO.json_rw import load_json_file, instance_from_json, instance_to_json, solution_to_json, write_json_file
from source.solution_validator import validate_solution
from source.solvers.solutionGenerators import random_solution, demands_first, demands_reverse
from source.validator.ownSolutionValidator import validate


class Test(TestCase):
    def test_validator_instance1_random(self):
        instance_file_path = '../../data/PSCCP_Instance1.json'

        instance_data = load_json_file(instance_file_path)
        instance_model = instance_from_json(instance_data)
        random_sol = random_solution(instance_model)
        write_json_file(solution_to_json(random_sol), instance_file_path.replace('.json', '_random_sol.json'))

        f = io.StringIO()
        with redirect_stdout(f), open(instance_file_path, 'r') as instance_file, \
                open(instance_file_path.replace('.json', '_random_sol.json'), 'r') as solution_file:
            validate_solution(json.load(instance_file), json.load(solution_file))
        output = f.getvalue()

        f = io.StringIO()
        with redirect_stdout(f):
            validate(instance_model, random_sol)
        output2 = f.getvalue()
        print(output2)
        self.assertEqual(output, output2, "Outputs of own Validator and given Validator differ at <random solution>")

    def test_validator_instance2_demand(self):
        instance_file_path = '../../data/PSCCP_Instance2.json'

        instance_data = load_json_file(instance_file_path)
        instance_model = instance_from_json(instance_data)
        demand_sol = demands_first(instance_model)
        write_json_file(solution_to_json(demand_sol), instance_file_path.replace('.json', '_demand_sol.json'))

        f = io.StringIO()
        with redirect_stdout(f), open(instance_file_path, 'r') as instance_file, \
                open(instance_file_path.replace('.json', '_demand_sol.json'), 'r') as solution_file:
            validate_solution(json.load(instance_file), json.load(solution_file))
        output = f.getvalue()

        f = io.StringIO()
        with redirect_stdout(f):
            validate(instance_model, demand_sol)
        output2 = f.getvalue()
        print(output2)
        self.assertEqual(output, output2, "Outputs of own Validator and given Validator differ at <demand solution>")

    def test_validator_instance3_demand_prior(self):
        instance_file_path = '../../data/PSCCP_Instance3.json'

        instance_data = load_json_file(instance_file_path)
        instance_model = instance_from_json(instance_data)
        demand_old_prior_due_sol = demands_first(instance_model, True, True, True)
        write_json_file(solution_to_json(demand_old_prior_due_sol),
                        instance_file_path.replace('.json', '_demand_old_prior_due_sol.json'))

        f = io.StringIO()
        with redirect_stdout(f), open(instance_file_path, 'r') as instance_file, \
                open(instance_file_path.replace('.json', '_demand_old_prior_due_sol.json'), 'r') as solution_file:
            validate_solution(json.load(instance_file), json.load(solution_file))
        output = f.getvalue()

        f = io.StringIO()
        with redirect_stdout(f):
            validate(instance_model, demand_old_prior_due_sol)
        output2 = f.getvalue()
        print(output2)
        self.assertEqual(output, output2,
                         "Outputs of own Validator and given Validator differ at <demand with priority solution>")

    def test_validator_instance4_reverse_demand(self):

        instance_file_path = '../../data/PSCCP_Instance4.json'

        instance_data = load_json_file(instance_file_path)
        instance_model = instance_from_json(instance_data)
        reverse_sol = demands_reverse(instance_model)
        write_json_file(solution_to_json(reverse_sol), instance_file_path.replace('.json', '_reverse_sol.json'))

        f = io.StringIO()
        with redirect_stdout(f), open(instance_file_path, 'r') as instance_file, \
                open(instance_file_path.replace('.json', '_reverse_sol.json'), 'r') as solution_file:
            validate_solution(json.load(instance_file), json.load(solution_file))
        output = f.getvalue()

        f = io.StringIO()
        with redirect_stdout(f):
            validate(instance_model, reverse_sol)
        output2 = f.getvalue()
        print(output2)
        self.assertEqual(output, output2, "Outputs of own Validator and given Validator differ at <reverse demand solution>")


