
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