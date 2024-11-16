import copy
import io
import json
import sys
from unittest import TestCase
from contextlib import redirect_stdout

from source.jsonIO.json_rw import load_json_file, instance_from_json, instance_to_json, solution_to_json, write_json_file
from source.models.baseModels import Demand, RoundInstance, PSCP_Instance, PSCP_Solution, RoundSolution
from source.solution_validator import validate_solution
from source.solvers.solutionGenerators import random_solution, demands_first, demands_reverse
from source.validator.ownSolutionValidator import validate, internal_validate, delta_validation_start, \
    delta_color_changes


class Test(TestCase):
    def test_validator_instance1_random(self):
        instance_file_path = '../../data/instance1.json'

        instance_data = load_json_file(instance_file_path)
        instance_model = instance_from_json(instance_data)
        random_sol = random_solution(instance_model,60)
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
        instance_file_path = '../../data/instance2.json'

        instance_data = load_json_file(instance_file_path)
        instance_model = instance_from_json(instance_data)
        demand_sol = demands_first(instance_model,60)
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
        instance_file_path = '../../data/instance3.json'

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
        instance_file_path = '../../data/instance4.json'

        instance_data = load_json_file(instance_file_path)
        instance_model = instance_from_json(instance_data)
        reverse_sol = demands_reverse(instance_model, 60)
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
        self.assertEqual(output, output2,
                         "Outputs of own Validator and given Validator differ at <reverse demand solution>")

    def test_validator_instance7_demand_prior(self):
        instance_file_path = '../../data/PSCCP_Instance7.json'

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

    def test_delta_start_instance7_random(self):
        instance_file_path = '../../data/PSCCP_Instance7.json'

        instance_data = load_json_file(instance_file_path)
        instance_model = instance_from_json(instance_data)

        rand_sol = random_solution(instance_model, 5)

        for i in range(100):
            res_validator = internal_validate(instance_model, rand_sol)
            delta_start = delta_validation_start(instance_model, rand_sol)

            self.assertEqual(res_validator[0], delta_start[2], "Different count of violations!")
            self.assertEqual(res_validator[1], delta_start[1], "Different count of color changes!")

            sum_violations = 0
            for j in range(len(delta_start[0])):
                sum_violations += max(0,delta_start[0][j][4])

            self.assertEqual(res_validator[0], sum_violations, "Different sum of violations with standard!")
            self.assertEqual(delta_start[2], sum_violations, "Different sum of violations with delta!")

    def test_delta_validation_small_instance(self):
        num_carriers = 3
        num_colors = 33
        history_color = 1
        demands = [
            Demand(4, 1, 1, 3),
            Demand(4, 2, 2, 3),
            Demand(4, 3, 3, 3),
            Demand(3, 1, 11, 2)
        ]
        ri_1 = RoundInstance([1, 1, 2, 2, 3])
        ri_2 = RoundInstance([1, 1, 2, 1, 3])
        ri_3 = RoundInstance([1, 1, 2, 3, 3])
        rounds = [ri_1, ri_2, ri_3]
        instance = PSCP_Instance(num_carriers, num_colors, history_color, demands, rounds)

        res_1 = RoundSolution([1, 1, 2, 2, 3])
        res_2 = RoundSolution([11, 11, 2, 1, 3])
        res_3 = RoundSolution([1, 1, 2, 3, 3])
        solution_1 = PSCP_Solution([res_1, res_2, res_3])

        # color manipulation
        round_idx_lst = [0, 1, 2, 1]
        sel_col_idx_lst = [0, 2, 1, 3]
        new_color_lst = [2, 11, 2, 11]

        delta_cc_lst = [2, -1, 0, 0]
        dem_viol_lst = [1, 2, 1, 0]
        dem_vio_cng_lst = [0, 1, 0, -1]

        old_sol = copy.deepcopy(solution_1)
        for i in range(len(round_idx_lst)):
            temp_sol = copy.deepcopy(solution_1)
            print(f"Running round {i}")

            init_res = delta_validation_start(instance, solution_1)
            checked_demands = init_res[0]
            color_changes = init_res[1]
            demand_violations = init_res[2]

            sel_color = temp_sol.round_solutions[round_idx_lst[i]].selected_colors[sel_col_idx_lst[i]]
            carrier = instance.rounds[round_idx_lst[i]].scheduled_carriers[sel_col_idx_lst[i]]

            temp_sol.round_solutions[round_idx_lst[i]].selected_colors[sel_col_idx_lst[i]] = new_color_lst[i]

            # check 2
            demand_violation_change = 0
            old_demand = [x for x in checked_demands if x[0] == carrier and x[1] == sel_color]
            new_demand = [x for x in checked_demands if x[0] == carrier and x[1] == new_color_lst[i]]

            if old_demand:
                old_demand = old_demand[0]
                demand_violation_change += 1 if old_demand[4] >= 0 else 0
            if new_demand:
                new_demand = new_demand[0]
                demand_violation_change += -1 if new_demand[4] > 0 else 0

            # check 1
            delta_cc = delta_color_changes(instance, old_sol, temp_sol, round_idx_lst[i], sel_col_idx_lst[i])

            # if demand_violation_change < 0 or (demand_violation_change == 0) and delta_cc < 0:
            color_changes += delta_cc
            # check 3
            demand_violations += demand_violation_change
            if new_demand:
                checked_demands[checked_demands.index(new_demand)] = (
                    new_demand[0], new_demand[1], new_demand[2], new_demand[3], new_demand[4] - 1)
            if old_demand:
                checked_demands[checked_demands.index(old_demand)] = (
                    old_demand[0], old_demand[1], old_demand[2], old_demand[3], old_demand[4] + 1)

            self.assertEqual(delta_cc_lst[i], delta_cc, "Wrong delta color changes!")
            self.assertEqual(dem_vio_cng_lst[i], demand_violation_change, "Wrong demand violation change!")
            self.assertEqual(dem_viol_lst[i], demand_violations, "Wrong demand violations!")

            res_validator = internal_validate(instance, temp_sol)
            sum_violations = 0
            for j in range(len(checked_demands)):
                sum_violations += max(0, checked_demands[j][4])

            self.assertEqual(res_validator[0], sum_violations, "Different sum of violations with standard!")

    def test_delta_color_changes(self):
        num_carriers = 3
        num_colors = 3
        history_color = 1
        demands = []
        ri_1 = RoundInstance([1, 1, 2, 2, 3])
        ri_2 = RoundInstance([1, 1, 2, 1, 3])
        ri_3 = RoundInstance([1, 1, 2, 3, 3])
        rounds = [ri_1, ri_2, ri_3]
        instance = PSCP_Instance(num_carriers, num_colors, history_color, demands, rounds)

        res_1 = RoundSolution([1, 1, 2, 2, 3])
        res_2 = RoundSolution([1, 1, 2, 1, 3])
        res_3 = RoundSolution([3, 3, 2, 1, 3])
        solution_1 = PSCP_Solution([res_1,res_2,res_3])

        #color manipulation
        round_idx_lst =     [0, 0, 2, 2, 1, 1, 1, 1, 1, 1]
        sel_col_idx_lst =   [0, 0, 4, 4, 4, 4, 0, 0, 2, 2]
        new_color_lst =     [1, 2, 2, 1, 1, 2, 3, 2, 3, 1]

        delta_cc_lst =      [0, 2, 0, -1, 0, 1, 0, 1, 0, -2]
        total_cc_lst =      [9, 11, 9, 8, 9, 10, 9, 10,9 , 7]

        old_sol = copy.deepcopy(solution_1)
        for i in range(len(round_idx_lst)):
            temp_sol = copy.deepcopy(solution_1)
            print(f"Running round {i}")

            init_res = delta_validation_start(instance, solution_1)
            color_changes = init_res[1]

            temp_sol.round_solutions[round_idx_lst[i]].selected_colors[sel_col_idx_lst[i]] = new_color_lst[i]

            # check 1
            delta_cc = delta_color_changes(instance, old_sol, temp_sol, round_idx_lst[i], sel_col_idx_lst[i])

            #if demand_violation_change < 0 or (demand_violation_change == 0) and delta_cc < 0:
            color_changes += delta_cc

            self.assertEqual(delta_cc_lst[i],delta_cc,"Wrong delta color changes!")
            self.assertEqual(total_cc_lst[i],color_changes,"Wrong total color changes!")