import copy
from unittest import TestCase

from numpy.ma.extras import average, median

from source.models.baseModels import RoundSolution, PSCP_Solution, PSCP_Instance, RoundInstance, Demand
from source.solvers.solutionGenerators import primitive_solution, random_solution, demands_first
from source.solvers.solutionImprovers import local_reorder, local_switch, primitive_local_improver, local_switch_groups
from source.validator.ownSolutionValidator import validate, internal_validate
from test.data_generators.test_instance_generator import gen_small_instance1, gen_medium_instance1, gen_tiny_instance1, \
    gen_tiny_instance2, gen_big_instance1, gen_small_instance2, gen_medium_instance2
from test.data_generators.test_solution_generator import gen_small_solution1, gen_medium_solution1, gen_tiny_solution1


class Test(TestCase):
    def test_local_reorder_small(self):
        instance = gen_small_instance1()
        solution = gen_small_solution1()

        actual_sol = local_reorder(instance, solution)

        rs_1 = RoundSolution([1, 1, 1, 1, 2, 2, 2])
        round_solutions = [rs_1]

        wanted_sol = PSCP_Solution(round_solutions)

        self.assertEqual(actual_sol.round_solutions[0].selected_colors, wanted_sol.round_solutions[0].selected_colors)

    def test_local_reorder_medium(self):
        instance = gen_medium_instance1()
        solution = gen_medium_solution1()

        actual_sol = local_reorder(instance, solution)

        rs_1 = RoundSolution([1, 1, 1, 1, 2, 2, 2])
        rs_2 = RoundSolution([1, 1, 1, 2, 2, 3, 3, 1, 3])
        rs_3 = RoundSolution([1, 1, 2, 1, 1, 2, 2, 2, 2])
        round_solutions = [rs_1, rs_2, rs_3]

        wanted_sol = PSCP_Solution(round_solutions)

        for ind in range(len(round_solutions)):
            self.assertEqual(wanted_sol.round_solutions[ind].selected_colors,actual_sol.round_solutions[ind].selected_colors)

    def test_local_switch_small(self):
        instance = gen_small_instance1()

        res_1 = RoundSolution([2, 2, 1, 1, 2, 1, 1])
        solution = PSCP_Solution([res_1])

        actual_sol = local_switch(instance, solution)
        rs_1 = RoundSolution([2, 2, 2, 1, 1, 1, 1])
        round_solutions = [rs_1]

        wanted_sol = PSCP_Solution(round_solutions)

        self.assertEqual(actual_sol.round_solutions[0].selected_colors, wanted_sol.round_solutions[0].selected_colors)

    def test_local_switch_medium(self):

        num_carriers = 3
        num_colors = 3
        history_color = 1
        demands = [
            Demand(7, 1, 1, 3),
            Demand(3, 1, 2, 3),
            Demand(4, 2, 1, 3),
            Demand(3, 2, 2, 3),
            Demand(3, 3, 1, 3),
            Demand(2, 3, 2, 3),
            Demand(2, 3, 3, 3)
        ]

        ri_1 = RoundInstance([1, 1, 2, 2, 2, 2, 1, 1])
        ri_2 = RoundInstance([1, 1, 3, 3, 3, 3, 1, 2, 2])
        ri_3 = RoundInstance([2, 2, 2, 1, 3, 3, 3, 1, 1])

        rounds = [ri_1, ri_2, ri_3]

        instance = PSCP_Instance(num_carriers, num_colors, history_color, demands, rounds)

        res_1 = RoundSolution([1, 2, 1, 1, 2, 2, 1, 1])
        res_2 = RoundSolution([1, 2, 1, 1, 2, 3, 1, 2, 2])
        res_3 = RoundSolution([1, 1, 2, 1, 3, 2, 1, 1, 2])
        solution = PSCP_Solution([res_1, res_2, res_3])
        #actual_sol = local_switch_groups(instance, solution)

        instance = gen_medium_instance2()

        wo_r_d = []
        wo_r_s = []
        wi_r_d = []
        wi_r_s = []
        maxcount = 1000

        for i in range(maxcount):
            solution = random_solution(instance)
            # solution = local_reorder(instance, solution)
            #validate(instance, solution)

            old_val = copy.deepcopy(internal_validate(instance, solution))
            for j in range(1000):
                solution = local_switch_groups(instance, solution)
                val = internal_validate(instance, solution)
                if val[0] == old_val[0] and val[1] == old_val[1]:
                    break
                old_val = copy.deepcopy(val)

            wo_r_d.append(old_val[0])
            wo_r_s.append(old_val[1])

        for i in range(maxcount):
            solution = random_solution(instance)
            solution = local_reorder(instance, solution)
            #validate(instance, solution)

            old_val = copy.deepcopy(internal_validate(instance, solution))
            for j in range(1000):
                solution = local_switch_groups(instance, solution)
                val = internal_validate(instance, solution)
                if val[0] == old_val[0] and val[1] == old_val[1]:
                    break
                old_val = copy.deepcopy(val)

            wi_r_d.append(old_val[0])
            wi_r_s.append(old_val[1])

        print("With reorder: (" + str(median(wi_r_d)) + "/" + str(median(wi_r_s)) + ")")
        print("Without reorder: (" + str(median(wo_r_s)) + "/" + str(median(wo_r_d)) + ")")


        #validate(instance, solution)

        #rs_1 = RoundSolution([2, 1, 1, 1, 2, 2, 1, 1])
        #rs_2 = RoundSolution([1, 2, 2, 2, 3, 1, 1, 2, 2])
        #rs_3 = RoundSolution([2, 1, 1, 1, 1, 3, 2, 2, 1])
        #round_solutions = [rs_1, rs_2, rs_3]
        #wanted_sol = PSCP_Solution(round_solutions)

        #for ind in range(len(round_solutions)):
        #    self.assertEqual(wanted_sol.round_solutions[ind].selected_colors,
        #                     actual_sol.round_solutions[ind].selected_colors)

    def test_primitive_local_improver_small(self):
        instance = gen_big_instance1()

        res_1 = RoundSolution([1, 1, 2, 2])
        res_2 = RoundSolution([1, 1, 1, 2])
        solution = PSCP_Solution([res_1, res_2])
        solution = random_solution(instance)

        validate(instance, solution)

        for i in range(1000):
            solution = primitive_local_improver(instance, solution)

        validate(instance, solution)

        #actual_sol = local_switch(instance, solution)
        #rs_1 = RoundSolution([2, 2, 2, 1, 1, 1, 1])
        #round_solutions = [rs_1]

        #wanted_sol = PSCP_Solution(round_solutions)

        #self.assertEqual(actual_sol.round_solutions[0].selected_colors, wanted_sol.round_solutions[0].selected_colors)