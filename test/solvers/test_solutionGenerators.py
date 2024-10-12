from unittest import TestCase

from source.solvers.solutionGenerators import primitive_solution
from test.data_generators.test_instance_generator import gen_tiny_instance1


class Test(TestCase):
    def test_primitive_solution_tiny(self):
        instance = gen_tiny_instance1()
        # solution = gen_tiny_solution1()

        primitive_solution(instance)