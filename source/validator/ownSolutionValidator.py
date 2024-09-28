
def validate(instance, solution):
    demand_violations = 0
    time_violations = 0
    color_changes = 0

    last_color = instance.history_color
    #loop over the demands
    for dem_index,demand in enumerate(instance.demands):
        left_quantity = demand.quantity

        #loop over each color in each rouund
        for rnd_index,rnd in enumerate(solution.round_solutions):
            for col_index,color in enumerate(rnd.selected_colors):
                #check if current carrier is the carrier of the demand
                if instance.rounds[rnd_index].scheduled_carriers[col_index] == demand.carrier_type:
                    #if the color matches, one demand less
                    if color == demand.color:
                        left_quantity -= 1
                        #if color is right but round too late
                        if (rnd_index+1) > demand.due_date and left_quantity > 0:
                            time_violations += 1
        #if some demands not (fully) fullfilled
        if left_quantity > 0:
            print(f"Demand {dem_index+1} is not fulfilled by {left_quantity}")
        demand_violations += 1 if left_quantity > 0 else 0

    #loop through the colors to get color changes
    for rnd_index, rnd in enumerate(solution.round_solutions):
        for col_index, color in enumerate(rnd.selected_colors):
            if color != last_color:
                color_changes += 1
                last_color = color

    if (demand_violations+time_violations) == 0:
        print("Solution is feasible!")
    else:
        print("Solution is infeasible!")
        print(f"Demand violations: {demand_violations}")
        print(f"Time violations: {time_violations}")
    print(f"Color changes: {color_changes}")
