import json

from source.models.baseModels import Demand, RoundInstance, DataModel


def from_json(json_data):
    demands = [Demand(d['Quantity'], d['CarrierType'], d['Color'], d['DueDate']) for d in json_data['Demands']]
    rounds = [RoundInstance(r['ScheduledCarriers']) for r in json_data['Rounds']]
    return DataModel(
        json_data['NumCarrierTypes'],
        json_data['NumColors'],
        json_data['HistoryColor'],
        demands,
        rounds
    )

def to_json(round_solutions):

    # list for the solutions
    rounds_data = {"Rounds": [round_solution.to_dict() for round_solution in round_solutions]}

    # convert to json
    json_string = json.dumps(rounds_data, indent=1)

    # writing the results to the file
    with open('../data/ToySolution.json', 'w') as f:
        f.write(json_string)

    return json_string