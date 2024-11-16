import sys
import json
from itertools import chain

from source.jsonIO.json_rw import instance_from_json, solution_from_json


def internal_validate_pos(instance, solution):
    demand_violations = 0
    color_changes = 0

    # Track last color outside of rounds
    last_color = instance.history_color

    # Precompute each demand's carrier and color to reduce inner loop work
    carrier_demands = {}
    for demand in instance.demands:
        if demand.carrier_type not in carrier_demands:
            carrier_demands[demand.carrier_type] = []
        carrier_demands[demand.carrier_type].append(demand)

    # Check demand violations by iterating over demands by carrier type
    for carrier, demands in carrier_demands.items():
        for demand in demands:
            left_quantity = demand.quantity
            for rnd_index, rnd in enumerate(solution.round_solutions):
                if rnd_index + 1 > demand.due_date:
                    break  # Skip rounds past the due date

                # Check if the carrier and color match in this round
                for col_index, color in enumerate(rnd.selected_colors):
                    if instance.rounds[rnd_index].scheduled_carriers[col_index] == carrier:
                        if color == demand.color:
                            left_quantity -= 1
                            if left_quantity == 0:
                                break  # Demand met, exit early
                if left_quantity == 0:
                    break  # No further rounds needed for this demand

            # Count demand violations if unmet
            demand_violations += max(left_quantity, 0)

    # Count color changes by comparing adjacent colors across rounds
    for rnd in solution.round_solutions:
        for color in rnd.selected_colors:
            if color != last_color:
                color_changes += 1
                last_color = color

    return demand_violations, color_changes

def internal_validate(instance, solution):
    demand_violations = 0
    color_changes = 0
    last_color = instance.history_color

    # Preprocess rounds to create a lookup for scheduled carriers by round and color index
    scheduled_carriers = [
        rnd.scheduled_carriers for rnd in instance.rounds
    ]
    # Iterate over demands and check fulfillment status
    for demand in instance.demands:
        left_quantity = demand.quantity
        due_date = demand.due_date
        demand_color = demand.color
        carrier_type = demand.carrier_type

        # Only iterate up to the demand's due date
        for rnd_index, rnd in enumerate(solution.round_solutions[:due_date]):
            round_carriers = scheduled_carriers[rnd_index]

            # Check each color for the demand’s carrier type
            for col_index, color in enumerate(rnd.selected_colors):
                if round_carriers[col_index] == carrier_type:
                    # If color matches, decrement left_quantity
                    if color == demand_color:
                        left_quantity -= 1
                        # Exit if demand is fully met
                        if left_quantity == 0:
                            break
            if left_quantity == 0:
                break  # Exit early for this demand if it has been met

        #if left_quantity > 0:
            #print(f"Demand Carr:{demand.carrier_type},Col:{demand.color},Due:{demand.due_date},Qty:{demand.quantity} violated")

        # Count unmet demands as violations
        demand_violations += max(left_quantity, 0)

    '''
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
                        if left_quantity == 0:
                            break
            if left_quantity == 0:
                break

            demand_violations += left_quantity if left_quantity > 0 else 0
    '''

    #loop through the colors to get color changes
    for color in chain.from_iterable(rnd.selected_colors for rnd in solution.round_solutions):
        if color != last_color:
            color_changes += 1
            last_color = color

    return demand_violations, color_changes

def delta_validation_start(instance, solution):

    demand_violations = 0
    color_changes = 0
    last_color = instance.history_color

    # Preprocess rounds to create a lookup for scheduled carriers by round and color index
    scheduled_carriers = [
        rnd.scheduled_carriers for rnd in instance.rounds
    ]

    all_demands = []
    for demand in instance.demands:
        all_demands.append((demand.carrier_type, demand.color, demand.due_date, demand.quantity, 0))  # Append each tuple

    checked_demands = []

    # Iterate over demands and check fulfillment status
    for demand in all_demands:
        left_quantity = demand[3]
        due_date = demand[2]
        demand_color = demand[1]
        carrier_type = demand[0]
        # Only iterate up to the demand's due date
        for rnd_index, rnd in enumerate(solution.round_solutions[:due_date]):
            round_carriers = scheduled_carriers[rnd_index]
            # Check each color for the demand’s carrier type
            for col_index, color in enumerate(rnd.selected_colors):
                if round_carriers[col_index] == carrier_type:
                    # If color matches, decrement left_quantity
                    if color == demand_color:
                        left_quantity -= 1

        demand_violations += max(left_quantity, 0)
        checked_demands.append((demand[0], demand[1], demand[2], demand[3], left_quantity))

    # loop through the colors to get color changes
    for color in chain.from_iterable(rnd.selected_colors for rnd in solution.round_solutions):
        if color != last_color:
            color_changes += 1
            last_color = color

    return checked_demands, color_changes, demand_violations

def delta_color_changes(instance, old_solution, new_solution, round_index, color_index):

    hist_color = instance.history_color

    new_color = new_solution.round_solutions[round_index].selected_colors[color_index]
    old_color = old_solution.round_solutions[round_index].selected_colors[color_index]

    max_item_index = len(new_solution.round_solutions[round_index].selected_colors)-1
    max_round_index = len(new_solution.round_solutions)-1

    old_changes = 0
    new_changes = 0

    if round_index == max_round_index and color_index == max_item_index:
        old_changes = 1 if old_solution.round_solutions[round_index].selected_colors[color_index - 1] != old_color else 0
        new_changes = 1 if new_solution.round_solutions[round_index].selected_colors[color_index - 1] != new_color else 0
    elif color_index == max_item_index:
        old_changes = 1 if old_solution.round_solutions[round_index].selected_colors[color_index - 1] != old_color else 0
        new_changes = 1 if new_solution.round_solutions[round_index].selected_colors[color_index - 1] != new_color else 0

        old_changes += 1 if old_solution.round_solutions[round_index + 1].selected_colors[0] != old_color else 0
        new_changes += 1 if new_solution.round_solutions[round_index + 1].selected_colors[0] != new_color else 0

    if round_index == 0 and color_index == 0:
        old_changes = 1 if old_solution.round_solutions[round_index].selected_colors[color_index + 1] != old_color else 0
        new_changes = 1 if new_solution.round_solutions[round_index].selected_colors[color_index + 1] != new_color else 0

        old_changes += 1 if hist_color != old_color else 0
        new_changes += 1 if hist_color != new_color else 0
    elif color_index == 0:
        old_changes = 1 if old_solution.round_solutions[round_index].selected_colors[color_index + 1] != old_color else 0
        new_changes = 1 if new_solution.round_solutions[round_index].selected_colors[color_index + 1] != new_color else 0

        old_changes += 1 if old_solution.round_solutions[round_index - 1].selected_colors[
                                len(old_solution.round_solutions[round_index - 1].selected_colors) - 1] != old_color else 0
        new_changes += 1 if new_solution.round_solutions[round_index - 1].selected_colors[
                                len(new_solution.round_solutions[round_index - 1].selected_colors) - 1] != new_color else 0

    if color_index != 0 and color_index != max_item_index:
        old_changes = 1 if old_solution.round_solutions[round_index].selected_colors[color_index - 1] != old_color else 0
        new_changes = 1 if new_solution.round_solutions[round_index].selected_colors[color_index - 1] != new_color else 0

        old_changes += 1 if old_solution.round_solutions[round_index].selected_colors[color_index + 1] != old_color else 0
        new_changes += 1 if new_solution.round_solutions[round_index].selected_colors[color_index + 1] != new_color else 0

    return new_changes-old_changes


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
        #if left_quantity > 0:
            #print(f"Demand {dem_index+1} is not fulfilled by {left_quantity}")
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