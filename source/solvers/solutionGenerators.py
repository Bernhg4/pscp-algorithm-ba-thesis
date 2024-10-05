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
                        dem_del = filtered_demands[randint(0, len(filtered_demands) - 1)]
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

def demands_reverse(input_instance):
    round_solutions = []
    all_demands = []

    # document all demands
    for demand in input_instance.demands:
        for _ in range(demand.quantity):  # Repeat for the quantity
            all_demands.append((demand.carrier_type, demand.color, demand.due_date))  # Append each tuple
    #all_demands = sorted(all_demands, key=lambda d: d[2],reverse=True)

    # loop over each carrier of each round
    temp_col = -1
    round_number = len(input_instance.rounds)
    for round_item in reversed(input_instance.rounds):
        selected_colors = [-1 for _ in round_item.scheduled_carriers]
        col_ind = len(selected_colors)-1
        current_demands = [x for x in all_demands if x[2] >= round_number]

        for current_carrier in reversed(round_item.scheduled_carriers):

            dem_del = (0, 0, 0)
            filtered_demands = [d for d in current_demands if d[0] == current_carrier]
            if filtered_demands:
                for dem in filtered_demands:
                    if dem[1] == temp_col:
                        dem_del = dem

                if dem_del == (0, 0, 0):
                    dem_del = filtered_demands[randint(0, len(filtered_demands) - 1)]
                    temp_col = dem_del[1]

            if dem_del != (0, 0, 0):
                all_demands.remove(dem_del)
                current_demands.remove(dem_del)

            selected_colors[col_ind] = temp_col
            col_ind -= 1

        for ind in range(len(round_item.scheduled_carriers)):
            if selected_colors[ind] == -1:
                selected_colors[ind] = selected_colors[ind-1]
        temp_col = selected_colors[0]



        round_number -= 1
        round_solution = RoundSolution(selected_colors)
        round_solutions.append(round_solution)

    return PSCP_Solution([d for d in reversed(round_solutions)])