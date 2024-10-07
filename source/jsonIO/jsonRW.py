import json

from source.models.baseModels import Demand, RoundInstance, PSCP_Instance, RoundSolution, PSCP_Solution

#function for reading a json file
def load_json_file(filepath):
    with open(filepath, 'r') as file:
        return json.load(file)

def write_json_file(json_string,filepath):
    # writing the results to the file
    with open(f'{filepath}', 'w') as f:
        f.write(json_string)

def instance_from_json(json_data):
    demands = [Demand(d['Quantity'], d['CarrierType'], d['Color'], d['DueDate']) for d in json_data['Demands']]
    rounds = [RoundInstance(r['ScheduledCarriers']) for r in json_data['Rounds']]
    return PSCP_Instance(
        json_data['NumCarrierTypes'],
        json_data['NumColors'],
        json_data['HistoryColor'],
        demands,
        rounds
    )

def solution_from_json(json_data):
    rounds = [RoundSolution(r['SelectedColors']) for r in json_data['Rounds']]
    return PSCP_Solution(rounds)

def solution_to_json(solution):

    # list for the solutions
    rounds_data = {"Rounds": [round_solution.to_dict() for round_solution in solution.round_solutions]}

    # convert to json
    json_string = json.dumps(rounds_data, indent=2)

    return json_string

def instance_to_json(instance):
    # Convert the PSCP_Instance object to a dictionary
    instance_data = instance.to_dict()

    # Convert the dictionary to a JSON string with indentation
    json_string = json.dumps(instance_data, indent=2)

    return json_string