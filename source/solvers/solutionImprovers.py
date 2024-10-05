
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
                if rounds[round_idx].scheduled_carriers[idx+1] == rounds[round_idx].scheduled_carriers[idx]:
                    start_idx = idx if start_idx==-1 else start_idx
                    continue

            for col in sorted(temp_colors):
                solution.round_solutions[round_idx].selected_colors[start_idx] = col
                start_idx += 1

            start_idx = -1
            temp_colors = []

    return solution

def local_switch(input_instance, solution):

    #jetzt schauen ob color zuvor zu einer der von dem carrier passt, dann reordern
    # gruppen erstellen pro carrier: ein array mit indizes je pro color, evnetuell tupel

    solution = local_reorder(input_instance, solution)

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

            grp_before = list(groups[grp_idx-1])
            grp_now = list(groups[grp_idx])
            grp_after = list(groups[grp_idx+1])

            new_group_before = [-1 for _ in grp_before]
            new_group_now = [-1 for _ in grp_now]
            new_group_after = [-1 for _ in grp_after]

            last_color = -1
            for c in grp_before:
                if c in [grp_now] and last_color == -1:
                    last_color = c





    return solution