import copy
import csv
import itertools
import math
import random
import statistics
import time
from datetime import datetime
from fileinput import filename
from random import randint, choice
from turtle import distance

import numpy as np

from source.models.baseModels import RoundSolution, PSCP_Solution
from source.validator.ownSolutionValidator import internal_validate, delta_color_changes, delta_validation_start

filename = ""
logpoints = []
def init_logging(instance_name,algorithm, add_rows):
    global filename
    filename = f'logging/ts_{instance_name}_{algorithm}_{datetime.now().strftime("%H_%M_%S")}.csv'
    global logpoints
    logpoints = []
    # Initialize the CSV file with headers if it doesn't already exist
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file, delimiter=";")
        # Check if the file is empty before writing the header
        if file.tell() == 0:
            #writer.writerow([f"Time series for {algorithm} with Instance {instance_name}"])
            writer.writerow(["Timestamp","Violations", "Changes"] + (["Temperature", "CurrentChanges"] if add_rows else [])) # headers

def run_improver(instance, solution, method, time_limit_seconds):
    old_res = internal_validate(instance, solution)
    #old_sol = copy.deepcopy(solution)

    start = time.perf_counter()
    while True:
        solution = method(instance, solution, start, time_limit_seconds)

        # check for time limit
        if time.perf_counter() - start > time_limit_seconds:
            log_write()
            return solution

        val_sol = internal_validate(instance, solution)
        if old_res[0] == val_sol[0] and old_res[1] == val_sol[1]:
            log_write()
            return solution
        else:
            old_res = copy.deepcopy(val_sol)

def run_meta_heuristic(instance, solution, time_limit_seconds, t_init, demand_bias, cool_rate, cutoff):

    # Calculate the initial temperature based on the formula
    std_dev = sample_stand_dev(instance, solution, demand_bias)
    #temperature = std_dev #/ np.log(1 / desired_accept_prob - 1)
    temperature = std_dev * t_init

    start = time.perf_counter()
    best_sol = copy.deepcopy(solution)
    start_temperature = temperature
    stagnation_count = 0
    stagnation_cutoff = 1000

    # delta
    init_res = delta_validation_start(instance, solution)
    checked_demands = init_res[0]
    init_color_changes = init_res[1]
    init_demand_violations = init_res[2]

    best_solution = (best_sol,init_demand_violations,init_color_changes)
    curr_sol = (best_sol,init_demand_violations,init_color_changes)

    while True:

        temp_solution = meta_heuristic(instance,best_solution, curr_sol,checked_demands, temperature, demand_bias, stagnation_count)
        temperature *= cool_rate

        best_solution = temp_solution[0]
        curr_sol = temp_solution[1]
        stagnation_count = temp_solution[2]

        #print(f"{temp_solution[0][2]}, {temp_solution[1][2]}")

        # check for time limit
        if time.perf_counter() - start > time_limit_seconds:
            log_write()
            return best_solution[0]

        # reheat if temperature low and stagnation
        if temperature <= cutoff and stagnation_count >= stagnation_cutoff:
            temperature = start_temperature
            stagnation_count = 0

def primitive_improver(input_instance, solution, start_time, time_limit_seconds, first_improvement,
                       debug_delta_changes=False):
    max_color = input_instance.num_colors

    best_solution = copy.deepcopy(solution)
    curr_solution = copy.deepcopy(solution)
    best_res = internal_validate(input_instance, solution)
    init_changes = best_res[1]
    init_violations = best_res[0]

    # delta
    init_res = delta_validation_start(input_instance, solution)
    checked_demands = init_res[0]
    init_color_changes = init_res[1]
    color_changes = init_res[1]
    init_demand_violations = init_res[2]
    demand_violations = init_res[2]

    run = 0

    #if best_res[0] != init_demand_violations and best_res[1] != init_color_changes:
    #print(f'delta ({init_demand_violations}/{init_color_changes})')
    #print(f'full ({init_violations}/{init_changes})')
    #    pass
    #got_delta = False
    #got_stand = False

    # check for time limit
    if time.perf_counter() - start_time > time_limit_seconds:
        return best_solution

    # runs = sel_colors * num_colors * sel_colors(start at every color) * selected_colors

    round_idx = 0
    while round_idx < len(solution.round_solutions):
        round_item = solution.round_solutions[round_idx]
        max_count = len(round_item.selected_colors)

        idx = 0
        while idx < max_count:
            sel_col_idx = idx
            sel_color = round_item.selected_colors[sel_col_idx % max_count]
            carrier = input_instance.rounds[round_idx].scheduled_carriers[idx]

            for c in range(1, max_color + 1, 1):
                run += 1

                new_color = ((sel_color + c - 1) % max_color) + 1
                solution.round_solutions[round_idx].selected_colors[sel_col_idx % max_count] = new_color

                if sel_color == new_color:
                    break

                if debug_delta_changes:
                    # check demand change
                    demand_violation_change = 0
                    old_demand = [x for x in checked_demands if x[0] == carrier and x[1] == sel_color and x[2] > round_idx]
                    #old_demand = [x for x in checked_demands if x[0] == carrier and x[1] == sel_color]
                    new_demand = [x for x in checked_demands if x[0] == carrier and x[1] == new_color and x[2] > round_idx]
                    #new_demand = [x for x in checked_demands if x[0] == carrier and x[1] == new_color]

                    if old_demand:
                        for od in old_demand:
                            demand_violation_change += 1 if od[4] >= 0 else 0
                    if new_demand:
                        for nd in new_demand:
                            demand_violation_change += -1 if nd[4] > 0 else 0

                    # check color changes
                    delta_cc = delta_color_changes(input_instance, curr_solution, solution, round_idx, idx)
                    if demand_violation_change < 0 or (demand_violation_change == 0 and delta_cc < 0):
                        if first_improvement:
                            color_changes += delta_cc
                            demand_violations += demand_violation_change
                            best_solution = copy.deepcopy(solution)
                            log_data_point([demand_violations, color_changes])
                            if new_demand:
                                for nd in new_demand:
                                    checked_demands[checked_demands.index(nd)] = (
                                        nd[0], nd[1], nd[2], nd[3], nd[4] - 1)
                            if old_demand:
                                for od in old_demand:
                                    checked_demands[checked_demands.index(od)] = (
                                        od[0], od[1], od[2], od[3], od[4] + 1)
                            return best_solution
                        else:
                            best_solution = copy.deepcopy(solution)
                            if (((demand_violations+demand_violation_change) == init_demand_violations - 1 or demand_violations == 0)
                                    and (color_changes+delta_cc) == init_color_changes - 2):
                                color_changes += delta_cc
                                demand_violations += demand_violation_change
                                log_data_point([demand_violations, color_changes])
                                return best_solution

                if not debug_delta_changes:
                    res = internal_validate(input_instance, solution)

                    #if res[0] != (demand_violations + demand_violation_change) and res[1] != (color_changes + delta_cc):
                    #if res[1] != (color_changes + (0 if got_delta else delta_cc)):
                    #if res[0] != (demand_violations + (0 if got_delta else demand_violation_change)):
                        #print()


                    if res[0] < best_res[0] or (res[0] == best_res[0] and res[1] < best_res[1]):
                        best_res = copy.deepcopy(res)
                        best_solution = copy.deepcopy(solution)
                        log_data_point([best_res[0], best_res[1]])

                        if first_improvement or (best_res[0] == init_violations - 1 and best_res[1] == init_changes - 2):
                            #got_stand = True
                            return best_solution

                #if got_stand != got_delta:
                #    print(f'new stand ({best_res[0]}/{best_res[1]})')
                #    print(f'new delta ({demand_violations}/{color_changes})')
                #    print()

                #if got_delta or got_stand:
                #    return best_solution


                # check for time limit
                if time.perf_counter() - start_time > time_limit_seconds:
                    return best_solution

            idx += 1
        round_idx += 1

    if debug_delta_changes:
        log_data_point([demand_violations, color_changes])
    else:
        log_data_point([best_res[0], best_res[1]])
    return best_solution

def meta_heuristic(instance, best_sol, curr_sol,checked_demands, temperature, demand_bias, stagnation_count):

    #initializations
    current_solution = curr_sol[0]
    original_solution = copy.deepcopy(curr_sol[0])

    # select round and index to change color
    selected_round = randint(0,len(current_solution.round_solutions)-1)
    selected_index = randint(0,len(instance.rounds[selected_round].scheduled_carriers)-1)

    # select new color which is not current one
    current_color = current_solution.round_solutions[selected_round].selected_colors[selected_index]
    current_carrier = instance.rounds[selected_round].scheduled_carriers[selected_index]
    colors = [i for i in range(1, instance.num_colors + 1) if i != current_color]
    new_color = choice(colors)

    # assign new color and validate
    current_solution.round_solutions[selected_round].selected_colors[selected_index] = new_color

    # check demand change
    delta_demand_violation = 0
    old_demand = [x for x in checked_demands if x[0] == current_carrier and x[1] == current_color and x[2] > selected_round]
    new_demand = [x for x in checked_demands if x[0] == current_carrier and x[1] == new_color and x[2] > selected_round]

    if old_demand:
        for od in old_demand:
            delta_demand_violation += 1 if od[4] >= 0 else 0
    if new_demand:
        for nd in new_demand:
            delta_demand_violation += -1 if nd[4] > 0 else 0

    # check color changes
    delta_cc = delta_color_changes(instance, original_solution, current_solution, selected_round, selected_index)

    delta_cost = delta_demand_violation * demand_bias + delta_cc

    accept = False

    # accept always if less demand violations or same demand violations and less color changes
    if delta_demand_violation < 0 or (delta_demand_violation == 0 and delta_cc < 0):
        accept = True
    else:
        scaled_value = -delta_cost / max(temperature, 1e-10)
        try:
            accept_prob = math.exp(scaled_value)  # Use exponential acceptance function
        except OverflowError:
            accept_prob = 0  # If overflow occurs, set acceptance probability to 0

        do_accept = random.uniform(0, 1)
        if do_accept < accept_prob:
            accept = True

        if random.uniform(0, 1) < 0.25:
            # print(f"temp:{temperature} delta: {scaled_cost} accept: {accept_prob} solution:{curr_sol[2]}")
            pass

    # else:
    #    # accept under certain conditions
    #    scaled_cost = delta_cost
    #    # scaled_cost = delta_cost / max_delta * scale_fact
    #    # scaled_value = -delta_cost / temperature
    #    scaled_value = -scaled_cost / max(temperature, 1e-10)
    #
    #    try:
    #        accept_prob = math.exp(scaled_value)  # Use exponential acceptance function
    #    except OverflowError:
    #        accept_prob = 0  # If overflow occurs, set acceptance probability to 0
    #
    #    # accept_prob = math.exp(scaled_value) if scaled_value < 700 else 1
    #
    #    do_accept = random.uniform(0, 1)
    #    if do_accept < accept_prob:
    #        accept = True
    #
    #    if random.uniform(0, 1) < 0.25:
    #        # print(f"temp:{temperature} delta: {scaled_cost} accept: {accept_prob} solution:{curr_sol[2]}")
    #        pass

    if accept:
        curr_sol = (current_solution,curr_sol[1] + delta_demand_violation, curr_sol[2] + delta_cc)
        if (delta_cc + delta_demand_violation) != 0:
            stagnation_count = 0
    else:
        curr_sol = (original_solution,curr_sol[1] , curr_sol[2])
        stagnation_count += 1

    if curr_sol[1] <= best_sol[1] and curr_sol[2] <= best_sol[2]:
        best_sol = (copy.deepcopy(current_solution), curr_sol[1], curr_sol[2])

    log_data_point([best_sol[1], best_sol[2], f"{temperature}", curr_sol[2]])
    return best_sol, curr_sol, stagnation_count

def first_improver(input_instance, solution, start_time, time_limit_seconds):
    return primitive_improver(input_instance, solution, start_time, time_limit_seconds,True, False)

    max_color = input_instance.num_colors

    best_solution = copy.deepcopy(solution)
    best_res = internal_validate(input_instance, solution)
    run = 0
    num_idx_changes = 1

    init_res = delta_validation_start(input_instance, solution)
    checked_demands = init_res[0]
    color_changes = init_res[1]
    demand_violations = init_res[2]

    #print(f"inits: full={best_res[0]}/{best_res[1]} delta={demand_violations}/{color_changes}")
    if best_res[1] == 191:
        pass

    # check for time limit
    if time.perf_counter() - start_time > time_limit_seconds:
        return best_solution

    #runs = sel_colors * num_colors * sel_colors(start at every color) * selected_colors

    round_idx = 0
    while round_idx < len(solution.round_solutions):
        round_item = solution.round_solutions[round_idx]
        max_count = len(round_item.selected_colors)

        idx = 0
        while idx < max_count:
            sel_col_idx = idx
            sel_color = round_item.selected_colors[sel_col_idx % max_count]
            carrier = input_instance.rounds[round_idx].scheduled_carriers[idx]


            for c in range(1, max_color+1, 1):
                new_color = ((sel_color + c - 1) % max_color) + 1
                run += 1

                solution.round_solutions[round_idx].selected_colors[sel_col_idx % max_count] = new_color

                #if idx == 8 and round_idx == 7 and c == 5:
                    #pass

                if debug_delta_changes:
                    # check demand change
                    demand_violation_change = 0
                    old_demand = [x for x in checked_demands if x[0] == carrier and x[1] == sel_color]
                    new_demand = [x for x in checked_demands if x[0] == carrier and x[1] == new_color]

                    if old_demand:
                        #old_demand = old_demand[0]
                        #demand_violation_change += 1 if old_demand[4] >= 0 else 0
                        for od in old_demand:
                            demand_violation_change += 1 if od[4] >= 0 else 0
                    if new_demand:
                        #new_demand = new_demand[0]
                        #demand_violation_change += -1 if new_demand[4] > 0 else 0
                        for nd in new_demand:
                            demand_violation_change += -1 if nd[4] > 0 else 0

                    # check color changes
                    delta_cc = delta_color_changes(input_instance, best_solution, solution, round_idx, idx)
                    if demand_violation_change < 0 or (demand_violation_change == 0) and delta_cc < 0:
                        color_changes += delta_cc
                        demand_violations += demand_violation_change
                        best_solution = copy.deepcopy(solution)
                        log_data_point([demand_violations, color_changes])
                        if new_demand:
                            #inde = checked_demands.index(new_demand)
                            #checked_demands[checked_demands.index(new_demand)] = (
                            #new_demand[0], new_demand[1], new_demand[2], new_demand[3], new_demand[4] - 1)
                            for nd in new_demand:
                                checked_demands[checked_demands.index(nd)] = (
                                    nd[0], nd[1], nd[2], nd[3], nd[4] - 1)
                        if old_demand:
                            #oinde = checked_demands.index(old_demand)
                            #checked_demands[checked_demands.index(old_demand)] = (
                            #    old_demand[0], old_demand[1], old_demand[2], old_demand[3], old_demand[4] + 1)
                            for od in old_demand:
                                checked_demands[checked_demands.index(od)] = (
                                    od[0], od[1], od[2], od[3], od[4] + 1)

                        #print(f"{run}_delta: ({demand_violations}/{color_changes})")
                        return best_solution

                if not debug_delta_changes:
                    res = internal_validate(input_instance, solution)
                    #temp_delta_res = delta_validation_start(input_instance, solution)
                    #dvs = temp_delta_res[2]
                    #ccs = temp_delta_res[1]

                    if res[0] < best_res[0] or (res[0] == best_res[0] and res[1] < best_res[1]):
                        best_res = copy.deepcopy(res)
                        best_solution = copy.deepcopy(solution)
                        log_data_point([best_res[0], best_res[1]])

                        #print(f"{run}_full: ({res[0]}/{res[1]})")
                        return best_solution

                #check for time limit
                if time.perf_counter() - start_time > time_limit_seconds:
                    return best_solution

            #solution.round_solutions[round_idx].selected_colors[sel_col_idx % max_count] = sel_color

            idx += 1
            #solution.round_solutions = best_solution.round_solutions
            #solution = copy.deepcopy(best_solution)

        round_idx += 1

    if debug_delta_changes:
        log_data_point([demand_violations, color_changes])
    else:
        log_data_point([best_res[0],best_res[1]])
    return best_solution

def first_improver_delta(input_instance, solution, start_time, time_limit_seconds):
    return primitive_improver(input_instance, solution, start_time, time_limit_seconds, True, True)

def sample_stand_dev(instance, solution, demand_bias):

    samples = []

    # delta
    init_res = delta_validation_start(instance, solution)
    checked_demands = init_res[0]
    init_color_changes = init_res[1]
    init_demand_violations = init_res[2]

    for i in range(50):
        current_solution = copy.deepcopy(solution)

        # select round and index to change color
        selected_round = randint(0, len(current_solution.round_solutions) - 1)
        selected_index = randint(0, len(instance.rounds[selected_round].scheduled_carriers) - 1)

        # select new color which is not current one
        current_color = current_solution.round_solutions[selected_round].selected_colors[selected_index]
        current_carrier = instance.rounds[selected_round].scheduled_carriers[selected_index]
        colors = [i for i in range(1, instance.num_colors + 1) if i != current_color]
        new_color = choice(colors)

        # assign new color and validate
        current_solution.round_solutions[selected_round].selected_colors[selected_index] = new_color

        # check demand change
        delta_demand_violation = 0
        old_demand = [x for x in checked_demands if
                      x[0] == current_carrier and x[1] == current_color and x[2] > selected_round]
        new_demand = [x for x in checked_demands if
                      x[0] == current_carrier and x[1] == new_color and x[2] > selected_round]

        if old_demand:
            for od in old_demand:
                delta_demand_violation += 1 if od[4] >= 0 else 0
        if new_demand:
            for nd in new_demand:
                delta_demand_violation += -1 if nd[4] > 0 else 0

        # check color changes
        delta_cc = delta_color_changes(instance, solution, current_solution, selected_round, selected_index)

        # nur delta_cc
        samples.append(delta_demand_violation * demand_bias + delta_cc)

    return statistics.stdev(samples)

def best_improver(input_instance, solution, start_time, time_limit_seconds):
    return primitive_improver(input_instance, solution, start_time, time_limit_seconds, False, False)

    max_color = input_instance.num_colors

    best_solution = copy.deepcopy(solution)
    best_res = internal_validate(input_instance, solution)
    init_changes = best_res[1]
    init_violations = best_res[0]

    #delta
    init_res = delta_validation_start(input_instance, solution)
    checked_demands = init_res[0]
    init_color_changes = init_res[1]
    color_changes = init_res[1]
    init_demand_violations = init_res[2]
    demand_violations = init_res[2]

    run = 0

    # check for time limit
    if time.perf_counter() - start_time > time_limit_seconds:
        return best_solution

    round_idx = 0
    while round_idx < len(solution.round_solutions):
        round_item = solution.round_solutions[round_idx]
        max_count = len(round_item.selected_colors)

        idx = 0
        while idx < max_count:
            sel_col_idx = idx
            sel_color = round_item.selected_colors[sel_col_idx % max_count]
            carrier = input_instance.rounds[round_idx].scheduled_carriers[idx]

            for c in range(1, max_color + 1, 1):
                new_color = ((sel_color + c - 1) % max_color) + 1
                solution.round_solutions[round_idx].selected_colors[sel_col_idx % max_count] = new_color
                run += 1

                if debug_delta_changes:

                    # check demand change
                    demand_violation_change = 0
                    old_demand = [x for x in checked_demands if x[0] == carrier and x[1] == sel_color]
                    new_demand = [x for x in checked_demands if x[0] == carrier and x[1] == new_color]

                    if old_demand:
                        for od in old_demand:
                            demand_violation_change += 1 if od[4] >= 0 else 0
                    if new_demand:
                        for nd in new_demand:
                            demand_violation_change += -1 if nd[4] > 0 else 0

                    # check color changes
                    delta_cc = delta_color_changes(input_instance, best_solution, solution, round_idx, idx)
                    if demand_violation_change < 0 or (demand_violation_change == 0) and delta_cc < 0:
                        color_changes += delta_cc
                        demand_violations += demand_violation_change
                        best_solution = copy.deepcopy(solution)
                        log_data_point([demand_violations, color_changes])
                        if new_demand:
                            for nd in new_demand:
                                checked_demands[checked_demands.index(nd)] = (
                                    nd[0], nd[1], nd[2], nd[3], nd[4] - 1)
                        if old_demand:
                            for od in old_demand:
                                checked_demands[checked_demands.index(od)] = (
                                    od[0], od[1], od[2], od[3], od[4] + 1)

                        if demand_violations == init_demand_violations - 1 and color_changes == init_color_changes - 2:
                            return best_solution

                if not debug_delta_changes:
                    res = internal_validate(input_instance, solution)
                    if res[0] < best_res[0] or (res[0] == best_res[0] and res[1] < best_res[1]):
                        best_res = copy.deepcopy(res)
                        best_solution = copy.deepcopy(solution)

                    if best_res[0] == init_violations - 1 and best_res[1] == init_changes - 2:
                        return best_solution

                # check for time limit
                if time.perf_counter() - start_time > time_limit_seconds:
                    log_data_point([best_res[0],best_res[1]])
                    return best_solution

            idx += 1
            #solution = copy.deepcopy(best_solution)

        round_idx += 1

    if debug_delta_changes:
        log_data_point([demand_violations, color_changes])
    else:
        log_data_point([best_res[0], best_res[1]])
    return best_solution

def best_improver_delta(input_instance, solution, start_time, time_limit_seconds):
    return primitive_improver(input_instance, solution, start_time, time_limit_seconds, False, True)


def log_data_point(line):
    timestamp = datetime.now()
    #print(f"logged: {line}")
    logpoints.append([timestamp] + line)

def log_write():
    with open(filename, mode="a", newline="") as file:
        writer = csv.writer(file, delimiter=";")
        for line in logpoints:
            writer.writerow(line)
        file.flush()



def local_reorder(input_instance, solution):

    rounds = input_instance.rounds

    for round_idx,round_item in enumerate(solution.round_solutions):
        max_idx = len(round_item.selected_colors)

        c_first_carrier = []
        c_second_carrier = []

        temp_colors = []
        start_idx = -1
        for idx,sel_color in enumerate(round_item.selected_colors):

            temp_colors.append(sel_color)

            if (idx+1) < max_idx:
                if start_idx == -1:
                    start_idx = idx
                if rounds[round_idx].scheduled_carriers[idx+1] == rounds[round_idx].scheduled_carriers[idx]:
                    continue

            for col in sorted(temp_colors):
                solution.round_solutions[round_idx].selected_colors[start_idx] = col
                start_idx += 1

            start_idx = -1
            temp_colors = []

    return solution

def local_switch_groups(input_instance, solution):

    best_solution = copy.deepcopy(solution)
    best_result = internal_validate(input_instance, best_solution)

    rounds = input_instance.rounds
    run = 1
    max_color = input_instance.num_colors

    hist_col = input_instance.history_color
    for round_idx,round_item in enumerate(solution.round_solutions):
        max_idx = len(round_item.selected_colors)
        groups = []

        group_colors = []
        temp_colors = []
        last_col = -1
        for idx,sel_color in enumerate(round_item.selected_colors):

            if (idx+1) < max_idx and rounds[round_idx].scheduled_carriers[idx+1] == rounds[round_idx].scheduled_carriers[idx]:
                if last_col == sel_color:
                    temp_colors.append(sel_color)
                else:
                    if temp_colors:
                        group_colors.append(temp_colors)
                    temp_colors = [sel_color]
                last_col = sel_color
                continue

            if last_col == sel_color:
                temp_colors.append(sel_color)
            else:
                group_colors.append(temp_colors)
                temp_colors = [sel_color]
            group_colors.append(temp_colors)
            groups.append(group_colors)
            group_colors = []
            temp_colors = []

        grp_idx = 0
        while grp_idx < len(groups):
            curr_group = groups[grp_idx]

            # switch groups carrier-internal
            c_grp_idx = 0
            while c_grp_idx < len(curr_group):
                temp_col_grp = copy.deepcopy(curr_group[c_grp_idx])
                curr_group[c_grp_idx] = curr_group[(grp_idx + 1) % len(curr_group)]
                curr_group[(grp_idx + 1) % len(curr_group)] = temp_col_grp

                new_round_sol = []
                for sub_group in groups:
                    for carrier in sub_group:
                        for color in carrier:
                            new_round_sol.append(color)

                solution.round_solutions[round_idx] = RoundSolution(new_round_sol)

                run += 1
                res = internal_validate(input_instance, solution)
                if res[0] < best_result[0] or (res[0] == best_result[0] and res[1] < best_result[1]):
                    best_result = copy.deepcopy(res)
                    best_solution = copy.deepcopy(solution)
                    #print("New best solution: " + str(res[0]) + "_" + str(res[1]))
                    #print("run " + str(run) + ": " + str(res[0]) + "_" + str(res[1]))
                    #print(best_solution)
                    return best_solution
                c_grp_idx += 1
                solution = copy.deepcopy(best_solution)

            # change colors of whole groups
            c_grp_idx = 0
            while c_grp_idx < len(curr_group):

                for c in range(1, max_color + 1, 1):
                    temp_col_grp = copy.deepcopy(curr_group[c_grp_idx])
                    curr_group[c_grp_idx] = [((x + c) % max_color) + 1 for x in temp_col_grp]

                    new_round_sol = []
                    for sub_group in groups:
                        for carrier in sub_group:
                            for color in carrier:
                                new_round_sol.append(color)

                    solution.round_solutions[round_idx] = RoundSolution(new_round_sol)

                    run += 1
                    res = internal_validate(input_instance, solution)
                    if res[0] < best_result[0] or (res[0] == best_result[0] and res[1] < best_result[1]):
                        best_result = copy.deepcopy(res)
                        best_solution = copy.deepcopy(solution)
                        #print("New best solution with change: " + str(res[0]) + "_" + str(res[1]))
                        #print("run " + str(run) + ": " + str(res[0]) + "_" + str(res[1]))
                        #print(best_solution)
                        return best_solution
                    solution = copy.deepcopy(best_solution)

                c_grp_idx += 1
            grp_idx += 1

    return best_solution

def local_switch(input_instance, solution):

    solution = local_reorder(input_instance, solution)
    new_solutions = []

    rounds = input_instance.rounds

    hist_col = input_instance.history_color
    for round_idx,round_item in enumerate(solution.round_solutions):
        max_idx = len(round_item.selected_colors)
        groups = []

        temp_colors = []
        for idx,sel_color in enumerate(round_item.selected_colors):
            temp_colors.append(sel_color)

            if (idx+1) < max_idx and rounds[round_idx].scheduled_carriers[idx+1] == rounds[round_idx].scheduled_carriers[idx]:
                    continue

            groups.append((rounds[round_idx].scheduled_carriers[idx],temp_colors))
            temp_colors = []

        grp_idx = 1
        while (grp_idx+1) < len(groups):

            grp_before = list(groups[grp_idx-1][1])
            grp_now = list(groups[grp_idx][1])
            grp_after = list(groups[grp_idx+1][1])

            new_group_before = [-1 for _ in grp_before]
            new_group_now = [-1 for _ in grp_now]
            new_group_after = [-1 for _ in grp_after]

            first_color_before = -1
            last_color_before = -1
            first_color_now = -1
            last_color_now = -1
            first_color_after = -1
            last_color_after = -1

            for c in grp_before:
                if c in grp_now and last_color_before == -1:
                    last_color_before = c

            #problem: wenn before und after gleiches hätten
            # problem wenn nur ein element/grupppe drinnen
            for c in grp_now:
                if c in grp_before and first_color_now == -1:
                    first_color_now = c
                if c in grp_after and last_color_now == -1:
                    last_color_now = c

            for c in grp_after:
                if c in grp_now and first_color_after == -1:
                    first_color_after = c

            new_group_before = __merge(grp_before, new_group_before, first_color_before, last_color_before)
            new_group_now = __merge(grp_now, new_group_now, first_color_now, last_color_now)
            new_group_after = __merge(grp_after, new_group_after, first_color_after, last_color_after)

            temp_colors.extend(new_group_before)
            if (grp_idx+2) == len(groups):
                temp_colors.extend(new_group_now)
                temp_colors.extend(new_group_after)

            grp_idx += 1

        new_solutions.append(RoundSolution(temp_colors))

    return PSCP_Solution(new_solutions)

def __merge(orig_cols, new_cols, first, last):
    idx = 0
    for col in [x for x in orig_cols if x == first]:
        new_cols[idx] = col
        idx += 1
        orig_cols.remove(col)

    idx = len(new_cols) - 1
    for col in [x for x in orig_cols if x == last]:
        new_cols[idx] = col
        idx -= 1
        orig_cols.remove(col)

    idx = 0
    for indx in range(len(new_cols)):
        if new_cols[indx] == -1:
            new_cols[indx] = orig_cols[idx]
            idx += 1

    return new_cols