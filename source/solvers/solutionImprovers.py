from source.models.baseModels import RoundSolution, PSCP_Solution


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