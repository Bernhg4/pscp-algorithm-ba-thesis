from random import randint

from source.models.baseModels import RoundSolution


def generate_random_solution(datamodel):
    round_solutions = []

    # loop over the rounds
    for round_ in datamodel.rounds:

        num_carriers = len(round_.scheduled_carriers)

        # generate a list of random colors
        selected_colors = [randint(1, 3) for _ in range(num_carriers)]

        # create the output with the random solution
        round_solution = RoundSolution(selected_colors)

        round_solutions.append(round_solution)

    return round_solutions

