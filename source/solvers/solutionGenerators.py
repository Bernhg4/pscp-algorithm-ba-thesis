import copy
import csv
import itertools
import sys
import time
from collections import Counter
from datetime import datetime
from random import randint, random

from source.models.baseModels import RoundSolution, PSCP_Solution
from source.validator.ownSolutionValidator import internal_validate

filename = ""

def random_solution(input_instance, time_limit_seconds):
    round_solutions = []
    start_time = time.perf_counter()

    # loop over the rounds
    for round_ in input_instance.rounds:

        num_carriers = len(round_.scheduled_carriers)

        # generate a list of random colors
        selected_colors = [randint(1, input_instance.num_colors) for _ in range(num_carriers)]

        # create the output with the random solution
        round_solution = RoundSolution(selected_colors)

        round_solutions.append(round_solution)

        # check for time limit
        if time.perf_counter() - start_time > time_limit_seconds:
            return PSCP_Solution([d for d in round_solutions])

    return PSCP_Solution([d for d in round_solutions])

def demands_first(input_instance, time_limit_seconds, use_old_color=False, prioritize_old_color=False, prioritize_due_date=False):
    round_solutions = []
    all_demands = []
    start_time = time.perf_counter()

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
                if prioritize_old_color:
                    earliest_deadline = min(filtered_demands, key=lambda d: d[2])[2]
                    filtered_demands = [d for d in filtered_demands if d[2] == earliest_deadline]
                    for dem in filtered_demands:
                        if dem[1] == temp_col:
                            dem_del = dem
                        # check for time limit
                        if time.perf_counter() - start_time > time_limit_seconds:
                            return PSCP_Solution([d for d in round_solutions])
                    if dem_del == (0, 0, 0) and prioritize_due_date:
                        dem_del = filtered_demands[0]
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

            # check for time limit
            if time.perf_counter() - start_time > time_limit_seconds:
                return PSCP_Solution([d for d in round_solutions])

        round_solution = RoundSolution(selected_colors)

        round_solutions.append(round_solution)

    return PSCP_Solution([d for d in round_solutions])

def demands_reverse(input_instance, time_limit_seconds):
    round_solutions = []
    all_demands = []
    start_time = time.perf_counter()

    # document all demands
    for demand in input_instance.demands:
        for _ in range(demand.quantity):  # Repeat for the quantity
            all_demands.append((demand.carrier_type, demand.color, demand.due_date))  # Append each tuple

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
                    # check for time limit
                    if time.perf_counter() - start_time > time_limit_seconds:
                        return PSCP_Solution([d for d in reversed(round_solutions)])

                if dem_del == (0, 0, 0):
                    dem_del = filtered_demands[0]
                    temp_col = dem_del[1]

            if dem_del != (0, 0, 0):
                all_demands.remove(dem_del)
                current_demands.remove(dem_del)

            selected_colors[col_ind] = temp_col
            col_ind -= 1

            # check for time limit
            if time.perf_counter() - start_time > time_limit_seconds:
                return PSCP_Solution([d for d in reversed(round_solutions)])

        for ind in range(len(round_item.scheduled_carriers)):
            if selected_colors[ind] == -1:
                selected_colors[ind] = selected_colors[ind-1]
        temp_col = selected_colors[0]

        round_number -= 1
        round_solution = RoundSolution(selected_colors)
        round_solutions.append(round_solution)

    return PSCP_Solution([d for d in reversed(round_solutions)])

def heuristic_solution(input_instance, time_limit_seconds, demand_look_ahead):
    all_demands = []
    start_time = time.perf_counter()

    for demand in input_instance.demands:
        for _ in range(demand.quantity):  # Repeat for the quantity
            all_demands.append((demand.carrier_type, demand.color, demand.due_date))  # Append each tuple

    # frequency for each demand in the list
    second_value_counts = Counter(x[1] for x in all_demands)
    # sort by due date, then by the lowest frequency
    sorted_demands = sorted(all_demands, key=lambda x: (x[2], second_value_counts[x[1]]))

    #fill up solutions with 0
    round_solutions = []
    for round_list in input_instance.rounds:
        dummy_solution = []
        for _ in round_list.scheduled_carriers:
            dummy_solution.append(0)
        round_solutions.append(RoundSolution(dummy_solution))

    best_solution = round_solutions
    while sorted_demands:
        counter = 0
        best_demand = (0,0,0)
        best_cost = sys.maxsize


        # go through x=look_ahead_demands
        for demand in sorted_demands:
            if counter == demand_look_ahead:
                break

            #best solution for this demand
            cost_sol = __get_best_color_position(demand,input_instance,best_solution, start_time, time_limit_seconds)
            cost = cost_sol[0]
            sol = cost_sol[1]

            # if overall best cost with this assignment, use this
            if best_cost > cost:
                best_cost = cost
                best_solution = sol
                best_demand = demand
            counter += 1
        if best_demand == (0, 0, 0):
            break
        sorted_demands.remove(best_demand)

    # loop through remaining uncolored positions and assign the last used color
    last_col = 0
    for round_idx,round_item in enumerate(input_instance.rounds):
        for carrier_idx,carrier_schedule in enumerate(round_item.scheduled_carriers):
            if best_solution[round_idx].selected_colors[carrier_idx] != 0:
                last_col = best_solution[round_idx].selected_colors[carrier_idx]
                break

    last_col = (1 if last_col == 0 else last_col) if input_instance.history_color==0 else input_instance.history_color
    for round_idx,round_item in enumerate(input_instance.rounds):
        for carrier_idx,carrier_schedule in enumerate(round_item.scheduled_carriers):
            if best_solution[round_idx].selected_colors[carrier_idx] == 0:
                best_solution[round_idx].selected_colors[carrier_idx] = last_col
            else:
                last_col = best_solution[round_idx].selected_colors[carrier_idx]

    return PSCP_Solution([d for d in best_solution])

def __get_best_color_position(demand, instance,solution, start_time, time_limit_seconds):
    best_cost = sys.maxsize
    best_solution = None

    #only the scheduled carriers up to the due date are necessary
    temp_rounds = instance.rounds[:demand[2]]

    #loop from the back through the scheduled carriers
    round_idx = len(temp_rounds)-1
    for round_item in reversed(temp_rounds):
        for idx in reversed(range(0,len(solution[round_idx].selected_colors),1)):

            # if current position is right carrier and uncolored position
            if instance.rounds[round_idx].scheduled_carriers[idx] == demand[0] and solution[round_idx].selected_colors[idx] == 0:
                # apply color, check cost, undo
                solution[round_idx].selected_colors[idx] = demand[1]
                costs = internal_validate(instance,PSCP_Solution([d for d in solution]))
                temp_solution = copy.deepcopy(solution)
                solution[round_idx].selected_colors[idx] = 0

                if costs[1] < best_cost:
                    best_cost = costs[1]
                    best_solution = temp_solution

            # check for time limit
            if time.perf_counter() - start_time > time_limit_seconds:
                return best_cost, best_solution

        round_idx -= 1

    return best_cost, best_solution




'''
def primitive_solution(input_instance):
    rounds = input_instance.rounds
    max_color = input_instance.num_colors

    solution = random_solution(input_instance)
    best_solution = random_solution(input_instance)
    best_res = internal_validate(input_instance, best_solution)
    #run = 1

    color_range = range(1,max_color+1,1)
    round_combinations  = []

    for round_idx,round_item in enumerate(solution.round_solutions):
        sel_cols = round_item.selected_colors

        possible_combinations = list(itertools.product(color_range, repeat=len(sel_cols)))
        round_combinations.append(possible_combinations)

    all_possible_combinations = itertools.product(*round_combinations)

    # Create a new instance for each combination of all rounds
    for combination_set in all_possible_combinations:
        #new_instance = copy.deepcopy(instance)

        # Assign the combination for each round
        for i, combination in enumerate(combination_set):
            solution.round_solutions[i].selected_colors = list(combination)
            res = internal_validate(input_instance, solution)
            if res[0] < best_res[0] or (res[0] == best_res[0] and res[1] < best_res[1]):
                best_res = res
                best_solution = copy.deepcopy(solution)
                #print("New best solution: " + str(res[0]) + "_" + str(res[1]))
                #print("run " + str(run) + ": " + str(res[0]) + "_" + str(res[1]))
            #run += 1


    return best_solution
'''