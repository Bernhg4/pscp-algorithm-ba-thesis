import sys
import json


def validate_solution(instance, solution):
    total_violations = 0

    # check that number of color assignments matches the rounds
    instances_rounds = instance['Rounds']
    solution_rounds = solution['Rounds']
    if len(instances_rounds) != len(solution_rounds):
        print("Solution is infeasible. Number of rounds does not match instance.")
        total_violations += 1
    for i in range(len(solution_rounds)):
        if len(solution_rounds[i]["SelectedColors"]) != len(instances_rounds[i]["ScheduledCarriers"]):
            print(f"Solution is infeasible. Number of values in round {i+1} does not match instance.")
            total_violations += 1

    # check if all demands are fulfilled in time
    demands = instance['Demands']
    demand_no = 0
    for d in demands:
        demand_no += 1
        due_round = d['DueDate']
        qty = d['Quantity']
        color = d['Color']
        carrier_type = d['CarrierType']

        assigned_count = 0
        for i in range(due_round):
            scheduled_carriers = instances_rounds[i]["ScheduledCarriers"]
            selected_colors = solution_rounds[i]["SelectedColors"]
            num_carriers = len(scheduled_carriers)
            for j in range(num_carriers):
                if scheduled_carriers[j] == carrier_type and selected_colors[j] == color:
                    assigned_count += 1

        if qty > assigned_count:
            print(f"Solution is infeasible. Demand {demand_no} is not fullfilled.")
            total_violations += 1

    # count color changes
    color_changes = 0
    list_of_all_colors = []
    for r in solution_rounds:
        list_of_all_colors += r["SelectedColors"]
    prev_color = instance['HistoryColor']
    for x in list_of_all_colors:
        if x != prev_color:
            color_changes += 1
        prev_color = x

    # print total number of violations
    if total_violations > 0:
        print("Solution is infeasible. Total number of constraint violations: " + str(total_violations))
    else:
        print("Solution is feasible")

    # print total number of changes
    print("Total number of color changes used in the solution: " + str(color_changes))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: <instance_file.json> <solution_file.json>")

    # Opening JSON files
    instance_file = open(sys.argv[1])
    solution_file = open(sys.argv[2])

    validate_solution(json.load(instance_file), json.load(solution_file))
