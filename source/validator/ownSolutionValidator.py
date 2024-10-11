import sys
import json

from source.jsonIO.json_rw import instance_from_json, solution_from_json

def internal_validate(instance, solution):
    demand_violations = 0
    color_changes = 0

    last_color = instance.history_color
    #loop over the demands
    for dem_index,demand in enumerate(instance.demands):
        left_quantity = demand.quantity

        #loop over each color in each round
        for rnd_index,rnd in enumerate(solution.round_solutions):
            for col_index,color in enumerate(rnd.selected_colors):
                #check if current carrier is the carrier of the demand
                if instance.rounds[rnd_index].scheduled_carriers[col_index] == demand.carrier_type:
                    #if the color matches, one demand less
                    if color == demand.color and (rnd_index+1) <= demand.due_date:
                        left_quantity -= 1
        demand_violations += left_quantity if left_quantity > 0 else 0

    #loop through the colors to get color changes
    for rnd in solution.round_solutions:
        for color in rnd.selected_colors:
            if color != last_color:
                color_changes += 1
                last_color = color

    return demand_violations, color_changes

def validate(instance, solution):
    demand_violations = 0
    color_changes = 0

    last_color = instance.history_color
    #loop over the demands
    for dem_index,demand in enumerate(instance.demands):
        left_quantity = demand.quantity

        #loop over each color in each round
        for rnd_index,rnd in enumerate(solution.round_solutions):
            for col_index,color in enumerate(rnd.selected_colors):
                #check if current carrier is the carrier of the demand
                if instance.rounds[rnd_index].scheduled_carriers[col_index] == demand.carrier_type:
                    #if the color matches, one demand less
                    if color == demand.color and (rnd_index+1) <= demand.due_date:
                        left_quantity -= 1
        #if some demands not (fully) fulfilled
        if left_quantity > 0:
            print(f"Demand {dem_index+1} is not fulfilled by {left_quantity}")
        demand_violations += 1 if left_quantity > 0 else 0

    #loop through the colors to get color changes
    for rnd in solution.round_solutions:
        for color in rnd.selected_colors:
            if color != last_color:
                color_changes += 1
                last_color = color

    if demand_violations == 0:
        print("Solution is feasible")
    else:
        print(f"Solution is infeasible. Total number of constraint violations: {demand_violations}")
    print(f"Total number of color changes used in the solution: {color_changes}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: <instance_file.json> <solution_file.json>")

    # Opening JSON files
    instance_file = open(sys.argv[1])
    solution_file = open(sys.argv[2])

    validate(instance_from_json(json.load(instance_file)), solution_from_json(json.load(solution_file)))