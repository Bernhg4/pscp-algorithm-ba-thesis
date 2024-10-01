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

def demands_first(input_instance, use_old_color=False, priorize_old_color=False, priorize_due_date=False):
    round_solutions = []
    all_demands = []

    #document all demands
    for demand in input_instance.demands:
        for _ in range(demand.quantity):  # Repeat for the quantity
            all_demands.append((demand.carrier_type, demand.color, demand.due_date))  # Append each tuple

    #if priorize_due_date:
    #all_demands = sorted(all_demands, key=lambda tup: tup[2])

    #nimmt liste von demands die am frühesten fertig sein müssen
    # davon eventuell die lastcolor sonst random

    #loop over each carrier of each round
    temp_col = 1 if input_instance.history_color==0 else input_instance.history_color
    for round_item in input_instance.rounds:
        selected_colors = []
        for current_carrier in round_item.scheduled_carriers:
            #assign random color first or use history color
            if not use_old_color:
                temp_col = randint(1, input_instance.num_colors)
            dem_del = (0,0,0)
            filtered_demands = [d for d in all_demands if d[0] == current_carrier]
            if filtered_demands:
                if priorize_old_color:
                    earliest_deadline = min(filtered_demands, key=lambda d: d[2])[2]
                    filtered_demands = [d for d in filtered_demands if d[2] == earliest_deadline]
                    for dem in filtered_demands:
                        if dem[1] == temp_col:
                            dem_del = dem
                    if dem_del == (0, 0, 0) and priorize_due_date:
                        dem_del = filtered_demands[randint(0, filtered_demands.__len__() - 1)]
                        temp_col = dem_del[1]

                if dem_del == (0, 0, 0):
                    for dem in all_demands:
                        if dem[0] == current_carrier:
                            temp_col = dem[1]
                            dem_del = dem
                            break

            #remove 1 demand when found
            if dem_del != (0,0,0):
                all_demands.remove(dem_del)

            selected_colors.append(temp_col)

        round_solution = RoundSolution(selected_colors)

        round_solutions.append(round_solution)

    return PSCP_Solution([d for d in round_solutions])
