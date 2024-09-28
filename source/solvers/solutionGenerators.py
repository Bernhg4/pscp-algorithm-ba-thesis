from random import randint

from source.models.baseModels import RoundSolution, PSCP_Solution


def random_solution(input_instance):
    round_solutions = []

    # loop over the rounds
    for round_ in input_instance.rounds:

        num_carriers = len(round_.scheduled_carriers)

        # generate a list of random colors
        selected_colors = [randint(1, input_instance.num_colors) for _ in range(num_carriers)]

        # create the output with the random solution
        round_solution = RoundSolution(selected_colors)

        round_solutions.append(round_solution)

    return PSCP_Solution([d for d in round_solutions])

def demands_first(input_instance, use_old_color=False, priorize_old_color=False):
    round_solutions = []
    all_demands = []

    #document all demands
    for demand in input_instance.demands:
        for _ in range(demand.quantity):  # Repeat for the quantity
            all_demands.append((demand.carrier_type, demand.color))  # Append each tuple

    #loop over each carrier of each round
    temp_col = 1 if input_instance.history_color==0 else input_instance.history_color
    for round_ in input_instance.rounds:
        selected_colors = []
        for current_carrier in round_.scheduled_carriers:
            #assign random color first or use history color
            if not use_old_color:
                temp_col = randint(1, input_instance.num_colors)
            del_index = -1

            if priorize_old_color:
                for dem_index, dem in enumerate(all_demands):
                    if dem[0] == current_carrier and dem[1] == temp_col:
                        del_index = dem_index
                        break

            if del_index == -1:
                # search for demand for current carrier
                for dem_index, dem in enumerate(all_demands):
                    if dem[0] == current_carrier:
                        temp_col = dem[1]
                        del_index = dem_index
                        break

            #remove 1 demand when found
            if del_index != -1:
                all_demands.pop(del_index)

            selected_colors.append(temp_col)

        round_solution = RoundSolution(selected_colors)

        round_solutions.append(round_solution)

    return PSCP_Solution([d for d in round_solutions])
