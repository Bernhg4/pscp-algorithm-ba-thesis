from source.models.baseModels import PSCP_Solution, RoundSolution

def gen_tiny_solution1():

    rs_1 = RoundSolution([2, 3])
    rs_2 = RoundSolution([2 ,2])

    round_solutions = [rs_1,rs_2]

    return PSCP_Solution(round_solutions)

def gen_tiny_solution2():

    rs_1 = RoundSolution([2, 2, 3])

    round_solutions = [rs_1]

    return PSCP_Solution(round_solutions)

def gen_small_solution1():

    rs_1 = RoundSolution([2, 2, 1, 1, 1, 2, 2])

    round_solutions = [rs_1]

    return PSCP_Solution(round_solutions)

def gen_small_solution2():

    rs_1 = RoundSolution([3, 3, 2, 2])
    rs_2 = RoundSolution([3, 1, 1, 2])
    rs_3 = RoundSolution([1, 1, 2, 2])

    round_solutions = [rs_1, rs_2, rs_3]

    return PSCP_Solution(round_solutions)

def gen_medium_solution1():

    rs_1 = RoundSolution([1, 1, 2, 2, 2, 1, 1])
    rs_2 = RoundSolution([1, 1, 3, 3, 3, 3, 1, 2 ,2])
    rs_3 = RoundSolution([2, 2, 2, 1, 3, 3, 3, 1 ,1])

    round_solutions = [rs_1, rs_2, rs_3]

    return PSCP_Solution(round_solutions)

def gen_medium_solution2():

    rs_1 = RoundSolution([4, 4, 3, 3, 3, 4, 4])
    rs_2 = RoundSolution([4, 1, 1, 2, 2, 1])
    rs_3 = RoundSolution([3, 3, 3, 4])
    rs_4 = RoundSolution([1, 1, 3, 4, 4, 2, 1])

    round_solutions = [rs_1, rs_2, rs_3, rs_4]

    return PSCP_Solution(round_solutions)


def gen_big_solution1():

    rs_1 = RoundSolution([1, 1, 2, 2, 2, 1, 1])
    rs_2 = RoundSolution([1, 1, 3, 3, 3, 3, 1, 2 ,2])
    rs_3 = RoundSolution([2, 2, 2, 1, 3, 3, 3, 1 ,1])
    rs_4 = RoundSolution([4, 4, 4, 4, 4, 5, 5, 5])
    rs_5 = RoundSolution([4, 4, 4, 5, 5, 5, 5])

    round_solutions = [rs_1, rs_2, rs_3, rs_4, rs_5]

    return PSCP_Solution(round_solutions)

def gen_big_solution2():

    rs_1 = RoundSolution([2, 1, 3, 4, 6, 1, 3])
    rs_2 = RoundSolution([2, 3, 3, 1, 1, 4, 5, 4 ,6])
    rs_3 = RoundSolution([2, 1, 1, 1 ,4 ,5, 6])
    rs_4 = RoundSolution([4, 1, 1, 2, 2, 2 ,5])
    rs_5 = RoundSolution([4, 4, 4, 5, 5, 5, 5])
    rs_6 = RoundSolution([6, 6, 6, 5 ,6 ,6 ,6])

    round_solutions = [rs_1, rs_2, rs_3, rs_4, rs_5, rs_6]

    return PSCP_Solution(round_solutions)

