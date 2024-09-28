
def validate(instance, solution):
    demand_violations = 0
    constraint_violations = 0
    color_changes = 0

    last_color = instance.history_color
    # check demands
    for demand in instance.demands:
        left_quantity = demand.quantity

        for rnd_index,rnd in enumerate(solution.round_solutions):
            for col_index,color in enumerate(rnd.selected_colors):
                if instance.rounds[rnd_index].scheduled_carriers[col_index] == demand.carrier_type:
                    if color == demand.color:
                        left_quantity -= 1
                        if (rnd_index+1) > demand.due_date:
                            constraint_violations += 1
        if left_quantity > 0:
            print(f"Demand {demand.carrier_type} is not fulfilled by {left_quantity}")
        demand_violations += max(left_quantity,0)

    for rnd_index, rnd in enumerate(solution.round_solutions):
        for col_index, color in enumerate(rnd.selected_colors):
            if color != last_color:
                color_changes += 1
                last_color = color

    print(f"Demand violations: {demand_violations}")
    print(f"Constraint violations: {constraint_violations}")
    print(f"Color changes: {color_changes}")
