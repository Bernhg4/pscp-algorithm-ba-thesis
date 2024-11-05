import copy
import csv
import itertools
import time
from datetime import datetime
from fileinput import filename
from random import randint

from source.models.baseModels import RoundSolution, PSCP_Solution
from source.validator.ownSolutionValidator import internal_validate

filename = ""
def init_logging(instance_name,algorithm):
    global filename
    filename = f"logging/ts_{instance_name}_{algorithm}_{datetime.now().strftime("%H_%M_%S")}.csv"
    # Initialize the CSV file with headers if it doesn't already exist
    with open(filename, mode="a", newline="") as file:
        writer = csv.writer(file, delimiter=";")
        # Check if the file is empty before writing the header
        if file.tell() == 0:
            #writer.writerow([f"Time series for {algorithm} with Instance {instance_name}"])
            writer.writerow(["Timestamp","Violations", "Changes"])  # headers

def run_improver(instance, solution, method, time_limit_seconds):
    old_res = internal_validate(instance, solution)
    #old_sol = copy.deepcopy(solution)

    start = time.perf_counter()
    while True:
        solution = method(instance, solution, start, time_limit_seconds)

        # check for time limit
        if time.perf_counter() - start > time_limit_seconds:
            return solution

        val_sol = internal_validate(instance, solution)
        if old_res[0] == val_sol[0] and old_res[1] == val_sol[1]:
            return solution
        else:
            old_res = copy.deepcopy(val_sol)



def primitive_first_improver(input_instance, solution, start_time, time_limit_seconds):
    max_color = input_instance.num_colors

    #best_solution = solution
    best_solution = copy.deepcopy(solution)
    best_res = internal_validate(input_instance, solution)
    run = 0
    num_idx_changes = 1

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
            for c in range(1, max_color + 1, 1):
                solution.round_solutions[round_idx].selected_colors[sel_col_idx % max_count] = ((sel_color + c) % max_color) + 1

                run += 1
                #check for time limit
                if time.perf_counter() - start_time > time_limit_seconds:
                    return best_solution

                res = internal_validate(input_instance, solution)
                if res[0] < best_res[0] or (res[0] == best_res[0] and res[1] < best_res[1]):
                    #best_res = res
                    best_res = copy.deepcopy(res)
                    #best_solution = solution
                    best_solution = copy.deepcopy(solution)
                    #print("New first solution: " + str(res[0]) + "_" + str(res[1]))
                    #print("run " + str(run) + ": " + str(res[0]) + "_" + str(res[1]))
                    #print(best_solution)
                    log_data_point([best_res[0],best_res[1]])

                    return best_solution
                    # break
                #else:
                #print("run " + str(run) + ": " + str(res[0]) + "_" + str(res[1]))
                #print(solution)
            idx += 1
            #solution.round_solutions = best_solution.round_solutions
            #solution = copy.deepcopy(best_solution)

        round_idx += 1

    log_data_point([best_res[0],best_res[1]])
    return best_solution

def primitive_best_improver(input_instance, solution, start_time, time_limit_seconds):
    max_color = input_instance.num_colors

    #best_solution = solution
    best_solution = copy.deepcopy(solution)
    best_res = internal_validate(input_instance, solution)
    #old_res = internal_validate(input_instance, solution)
    run = 0
    num_idx_changes = 1

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
            for c in range(1, max_color + 1, 1):
                solution.round_solutions[round_idx].selected_colors[sel_col_idx % max_count] = ((sel_color + c) % max_color) + 1

                run += 1
                # check for time limit
                if time.perf_counter() - start_time > time_limit_seconds:
                    log_data_point([best_res[0],best_res[1]])
                    return best_solution

                res = internal_validate(input_instance, solution)
                if res[0] < best_res[0] or (res[0] == best_res[0] and res[1] < best_res[1]):
                    #best_res = res
                    best_res = copy.deepcopy(res)
                    #best_solution = solution
                    best_solution = copy.deepcopy(solution)
                    #return best_solution
                    # break
                #else:
                #print("run " + str(run) + ": " + str(res[0]) + "_" + str(res[1]))
                #print(solution)
            idx += 1
            #solution = copy.deepcopy(best_solution)

        round_idx += 1

    #if best_res[0] < old_res[0] or (best_res[0] == old_res[0] and best_res[1] < old_res[1]):
        #print("New best solution: " + str(best_res[0]) + "_" + str(best_res[1]))
        #print(best_solution)
    log_data_point([best_res[0],best_res[1]])
    return best_solution


def log_data_point(line):
    timestamp = datetime.now()

    with open(filename, mode="a", newline="") as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerow([timestamp] + line)
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


def __build_solution(groups):
    pass


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