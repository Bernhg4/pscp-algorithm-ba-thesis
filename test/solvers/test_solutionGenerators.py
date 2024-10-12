from unittest import TestCase

from source.solvers.solutionGenerators import primitive_solution
from test.data_generators.test_instance_generator import gen_tiny_instance1


class Test(TestCase):
    def test_primitive_solution_tiny(self):
        instance = gen_tiny_instance1()
        # solution = gen_tiny_solution1()

        primitive_solution(instance)

        '''

        res_1 = RoundSolution([2, 2, 1, 1, 2, 1, 1]))
        res_2 = RoundSolution([1, 1, 2, 2, 1, 3, 2, 3, 1])
        res_3 = RoundSolution([1, 1, 2, 1, 3, 2, 1, 1, 2])
        solution = PSCP_Solution([res_1, res_2, res_3])

        actual_sol = local_switch(instance, solution)
        rs_1 = RoundSolution([2, 2, 2, 1, 1, 1, 1])
        rs_2 = RoundSolution([1, 1, 1, 3, 2, 2, 2, 1, 3])
        rs_3 = RoundSolution([2, 1, 1, 1, 1, 3, 2, 2, 1])
        round_solutions = [rs_1, rs_2, rs_3]
        wanted_sol = PSCP_Solution(round_solutions)

        for ind in range(len(round_solutions)):
            self.assertEqual(wanted_sol.round_solutions[ind].selected_colors,
                             actual_sol.round_solutions[ind].selected_colors)

        '''