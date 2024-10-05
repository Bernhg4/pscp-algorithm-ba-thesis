from source.models.baseModels import PSCP_Solution, RoundSolution


def gen_small_solution1():

    rs_1 = RoundSolution([1, 1, 2, 1, 1, 2, 2])

    round_solutions = [rs_1]

    return PSCP_Solution(round_solutions)

def gen_medium_solution1():

    rs_1 = RoundSolution([1, 1, 2, 1, 1, 2, 2])
    rs_2 = RoundSolution([1, 1, 2, 2, 1, 3, 1, 3, 3])
    rs_3 = RoundSolution([1, 1, 2, 1, 2, 2, 1, 1, 1])

    round_solutions = [rs_1, rs_2, rs_3]

    return PSCP_Solution(round_solutions)