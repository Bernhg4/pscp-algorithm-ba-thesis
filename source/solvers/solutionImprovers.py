import copy
import csv
import math
import random
import statistics
import time

from datetime import datetime

from random import randint, choice

from source.validator.ownSolutionValidator import internal_validate, delta_color_changes, delta_validation_start


def init_logging(file_name, add_rows):
    # Initialize the CSV file with headers if it doesn't already exist
    with open(file_name, mode="w", newline="") as file:
        writer = csv.writer(file, delimiter=";")
        # Check if the file is empty before writing the header
        if file.tell() == 0:
            writer.writerow(["Timestamp","Violations", "Changes"] + (["Temperature", "CurrentChanges", "CurrentViolations","AcceptanceRate"] if add_rows else [])) # headers

def run_improver(instance, solution,log_info, method, time_limit_seconds):
    old_res = internal_validate(instance, solution)
    init_logging(log_info[0], log_info[1])
    logpoints = []

    start = time.perf_counter()
    while True:
        temp_solution = method(instance, solution, start, time_limit_seconds)
        solution = temp_solution[0]
        logpoints.append(temp_solution[1])

        # check for time limit
        if time.perf_counter() - start > time_limit_seconds:
            log_write(log_info[0], logpoints)
            return solution

        val_sol = internal_validate(instance, solution)
        if old_res[0] == val_sol[0] and old_res[1] == val_sol[1]:
            log_write(log_info[0], logpoints)
            return solution
        else:
            old_res = copy.deepcopy(val_sol)

def run_sim_annealing(instance, solution, log_info, time_limit_seconds, t_init, demand_bias, old_cool_rate, cutoff):

    init_logging(log_info[0],log_info[1])
    logpoints = []

    temperature = t_init
    stagnation_count = 0

    # delta
    init_res = delta_validation_start(instance, solution)
    checked_demands = init_res[0]
    init_color_changes = init_res[1]
    init_demand_violations = init_res[2]

    best_solution = (copy.deepcopy(solution),init_demand_violations,init_color_changes)
    curr_sol = (copy.deepcopy(solution),init_demand_violations,init_color_changes)

    start = time.perf_counter()
    iterations = 0

    while True:

        temp_solution = simulated_annealing(instance, best_solution, curr_sol, checked_demands, temperature, demand_bias, stagnation_count)

        best_solution = temp_solution[0]
        curr_sol = temp_solution[1]
        checked_demands = temp_solution[2]
        stagnation_count = temp_solution[3]

        timestamp = datetime.now()
        logpoints.append([timestamp] + temp_solution[4])

        # check for time limit
        if time.perf_counter() - start > time_limit_seconds:
            log_write(log_info[0], logpoints)
            return best_solution[0]

        end = time.perf_counter()
        total_execution_time = end - start
        iterations += 1

        remaining_time = time_limit_seconds - total_execution_time
        time_per_iteration = total_execution_time / max(iterations, 1)
        remaining_iterations = remaining_time / time_per_iteration

        # Safely compute log(cool_rate) using logarithms
        log_t_init = math.log(t_init)
        log_cutoff = math.log(cutoff)
        large_value_threshold = 700
        log_cool_rate = (log_cutoff - log_t_init) / remaining_iterations

        if abs(log_cool_rate) > large_value_threshold:
            # Gradually approach cutoff if iterations are small
            log_cool_rate = -large_value_threshold if log_cool_rate < 0 else large_value_threshold

        # Convert back to cooling rate using exp, with bounds
        if log_cool_rate < -700:  # Prevent underflow
            log_cool_rate = -700

            # Compute cooling rate safely
        cool_rate = math.exp(log_cool_rate)

        temperature = temperature * cool_rate

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
    datapoints = []

    # check for time limit
    if time.perf_counter() - start_time > time_limit_seconds:
        return best_solution, datapoints

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
                    new_demand = [x for x in checked_demands if x[0] == carrier and x[1] == new_color and x[2] > round_idx]

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
                            datapoints.append(datetime.now())
                            datapoints.append(demand_violations)
                            datapoints.append(color_changes)
                            if new_demand:
                                for nd in new_demand:
                                    checked_demands[checked_demands.index(nd)] = (
                                        nd[0], nd[1], nd[2], nd[3], nd[4] - 1)
                            if old_demand:
                                for od in old_demand:
                                    checked_demands[checked_demands.index(od)] = (
                                        od[0], od[1], od[2], od[3], od[4] + 1)
                            return best_solution, datapoints
                        else:
                            best_solution = copy.deepcopy(solution)
                            if (((demand_violations+demand_violation_change) == init_demand_violations - 1 or demand_violations == 0)
                                    and (color_changes+delta_cc) == init_color_changes - 2):
                                color_changes += delta_cc
                                demand_violations += demand_violation_change
                                datapoints.append(datetime.now())
                                datapoints.append(demand_violations)
                                datapoints.append(color_changes)
                                return best_solution,datapoints

                if not debug_delta_changes:
                    res = internal_validate(input_instance, solution)

                    if res[0] < best_res[0] or (res[0] == best_res[0] and res[1] < best_res[1]):
                        best_res = copy.deepcopy(res)
                        best_solution = copy.deepcopy(solution)
                        datapoints.append(datetime.now())
                        datapoints.append(best_res[0])
                        datapoints.append(best_res[1])

                        if first_improvement or (best_res[0] == init_violations - 1 and best_res[1] == init_changes - 2):
                            return best_solution,datapoints

                # check for time limit
                if time.perf_counter() - start_time > time_limit_seconds:
                    return best_solution,datapoints

            idx += 1
        round_idx += 1

    if debug_delta_changes:
        datapoints.append(datetime.now())
        datapoints.append(demand_violations)
        datapoints.append(color_changes)
    else:
        datapoints.append(datetime.now())
        datapoints.append(best_res[0])
        datapoints.append(best_res[1])
    return best_solution, datapoints

def simulated_annealing(instance, best_sol, curr_sol, checked_demands, temperature, demand_bias, stagnation_count):

    #initializations
    new_solution = curr_sol[0]
    original_solution = curr_sol[0].copy()

    # select round and index to change color
    selected_round = randint(0,len(new_solution.round_solutions)-1)
    selected_index = randint(0,len(instance.rounds[selected_round].scheduled_carriers)-1)

    # select new color which is not current one
    current_color = new_solution.round_solutions[selected_round].selected_colors[selected_index]
    current_carrier = instance.rounds[selected_round].scheduled_carriers[selected_index]
    colors = [i for i in range(1, instance.num_colors + 1) if i != current_color]
    new_color = choice(colors)

    # assign new color and validate
    new_solution.round_solutions[selected_round].selected_colors[selected_index] = new_color

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
    delta_cc = delta_color_changes(instance, original_solution, new_solution, selected_round, selected_index)

    delta_cost = delta_demand_violation * demand_bias + delta_cc

    accept = False
    accept_prob = 1

    # accept always if less demand violations or same demand violations and less color changes
    if delta_demand_violation < 0 or (delta_demand_violation == 0 and delta_cc < 0):
        accept = True
    else:
        scaled_value = -delta_cost / max(temperature, 1e-10)
        try:
            accept_prob = math.exp(scaled_value)
        except OverflowError:
            accept_prob = 0  # If overflow occurs, set acceptance probability to 0

        do_accept = random.uniform(0, 1)
        if do_accept < accept_prob:
            accept = True

        if random.uniform(0, 1) < 0.25:
            pass

    if accept:
        curr_sol = (new_solution,curr_sol[1] + delta_demand_violation, curr_sol[2] + delta_cc)
        if delta_cc != 0 or delta_demand_violation != 0:
            stagnation_count = 0
        # Update checked_demands based on old_demand and new_demand
        for od in old_demand:
            # Locate the tuple in checked_demands
            index = checked_demands.index(od)
            # Convert to list, modify, and replace back
            updated = list(checked_demands[index])
            updated[4] += 1  # Increase the 4th element
            checked_demands[index] = tuple(updated)

        for nd in new_demand:
            # Locate the tuple in checked_demands
            index = checked_demands.index(nd)
            # Convert to list, modify, and replace back
            updated = list(checked_demands[index])
            updated[4] -= 1  # Decrease the 4th element
            checked_demands[index] = tuple(updated)

    else:
        curr_sol = (original_solution,curr_sol[1] , curr_sol[2])
        stagnation_count += 1

    if (curr_sol[1] < best_sol[1]) or (curr_sol[1] <= best_sol[1] and curr_sol[2] < best_sol[2]):
        best_sol = (curr_sol[0].copy(), curr_sol[1], curr_sol[2])

    dp = [best_sol[1], best_sol[2], f"{temperature}", curr_sol[2], curr_sol[1], accept_prob]

    return best_sol, curr_sol, checked_demands, stagnation_count, dp

def first_improver_delta(input_instance, solution, start_time, time_limit_seconds):
    return primitive_improver(input_instance, solution, start_time, time_limit_seconds, True, True)

def sample_stand_dev(instance, solution, demand_bias):

    samples = []

    # delta
    init_res = delta_validation_start(instance, solution)
    checked_demands = init_res[0]

    for i in range(500):
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

def best_improver_delta(input_instance, solution, start_time, time_limit_seconds):
    return primitive_improver(input_instance, solution, start_time, time_limit_seconds, False, True)

def log_write(file_name, logpoints):

    logpoints = reduce_lines(logpoints)

    with open(file_name, mode="a", newline="") as file:
        writer = csv.writer(file, delimiter=";")
        for line in logpoints:
            writer.writerow(line)
        file.flush()

def reduce_lines(data):

    #Filters rows, keeping only the first row for each unique combination of values
    #in all columns except the 4th column and groups rows by timestamps up to the
    #second digit after the comma in the seconds part

    seen = set()
    filtered = []

    for row in data:
        if not row:
            continue
        # Round the timestamp to the second digit after the comma
        timestamp = row[0]
        rounded_timestamp = timestamp.replace(microsecond=int(timestamp.microsecond / 10000) * 10000)

        # Create a tuple of values excluding the 4th column (index 3), using the adjusted timestamp
        unique_key = tuple([rounded_timestamp] + row[1:3] + row[4:])

        # If the unique combination hasn't been seen, add it to the result
        if unique_key not in seen:
            seen.add(unique_key)
            filtered.append(row)

    return filtered
