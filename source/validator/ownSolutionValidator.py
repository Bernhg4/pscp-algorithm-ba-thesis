import json
from copy import copy

from source.jsonIO.jsonRW import from_json


def validate(instance, solution):
    color_changes = 0
    demand_violations = 0

    temp_solution = copy(solution)

    for demand in instance.demands:
        left_quantity = demand.quantity
        dem_fullfilled = False

        for rnd_index,rnd in enumerate(temp_solution.round_solutions):
            for col_index,color in enumerate(rnd.selected_colors):
                if rnd_index < demand.due_date:
                    if color == demand.color and instance.rounds[rnd_index].scheduled_carriers[col_index] == demand.carrier_type:
                        print(f"R{rnd_index+1} C{color} valid for CT{demand.carrier_type} C{demand.color} DD{demand.due_date}")
                        color = 0
                        break
                else:
                    demand_violations += 1

    print(f"Demand violations: {demand_violations}")
