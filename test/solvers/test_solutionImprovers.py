from unittest import TestCase

from source.models.baseModels import RoundSolution, PSCP_Solution
from source.solvers.solutionImprovers import local_reorder
from test.generators.test_instance_generator import gen_small_instance1
from test.generators.test_solution_generator import gen_small_solution1


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
        instance = gen_small_instance1()
        solution = gen_small_solution1()

        actual_sol = local_reorder(instance,solution)

        rs_1 = RoundSolution([1, 1, 1, 1, 2, 2, 2])
        rs_2 = RoundSolution([1, 1, 1, 2, 2, 3, 1, 3, 3])
        rs_3 = RoundSolution([1, 1, 2, 1, 1, 1, 2, 1, 1])
        round_solutions = [rs_1, rs_2, rs_3]

        wanted_sol = PSCP_Solution(round_solutions)

        self.assertEqual(actual_sol.round_solutions[0].selected_colors, wanted_sol.round_solutions[0].selected_colors)