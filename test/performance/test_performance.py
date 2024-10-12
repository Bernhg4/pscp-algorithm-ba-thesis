import time
from unittest import TestCase

from source.jsonIO.json_rw import load_json_file, instance_from_json
from source.solvers.solutionGenerators import random_solution
from source.validator.ownSolutionValidator import internal_validate


class Test(TestCase):

    instance_file7 = '../../data/PSCCP_Instance7.json'

    def test_random_solution_performance(self):

        instance_data = load_json_file(self.__class__.instance_file7)
        instance = instance_from_json(instance_data)

        start = time.time()

        random_sol = random_solution(instance)

        end = time.time()

        result = internal_validate(instance, random_sol)

        print("Random Solution: " + str(round(end-start,4)) + "s with (" + str(result[0]) + "," + str(result[1]) + ")")


