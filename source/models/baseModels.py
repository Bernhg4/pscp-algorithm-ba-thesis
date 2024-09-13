import json

class Demand:
    def __init__(self, quantity, carrier_type, color, due_date):
        self.quantity = quantity
        self.carrier_type = carrier_type
        self.color = color
        self.due_date = due_date

    def __str__(self):
        carrier_letter = chr(self.carrier_type + 64)
        return f"{self.quantity}x {carrier_letter}[{["Rot","Blau","Grün"][self.color-1]}] bis R{self.due_date}"


class Round:
    def __init__(self, scheduled_carriers):
        self.scheduled_carriers = scheduled_carriers

    def __str__(self):
        return "".join([f"{chr(carrier + 64)}" for carrier in self.scheduled_carriers])


class DataModel:
    def __init__(self, num_carrier_types, num_colors, history_color, demands, rounds):
        self.num_carrier_types = num_carrier_types
        self.num_colors = num_colors
        self.history_color = history_color
        self.demands = demands
        self.rounds = rounds

    def __str__(self):
        demands_str = "".join([f"{str(demand)}, " for demand in self.demands]).rstrip(" ,")
        rounds_str = "".join([f"{str(round_)}|" for round_ in self.rounds])
        x = 1
        roundDesc = ""
        remOne = False
        for c in rounds_str:
            if c == "|":
                roundDesc += "R" + str(x)
                x += 1
                remOne = True
            elif not remOne:
                roundDesc += " "
            else:
                remOne = False

        return (f"Produktionsplan: {demands_str}\n"
                f"{roundDesc}\n"
                f"{rounds_str}\n"
        )


def from_json(json_data):
    demands = [Demand(d['Quantity'], d['CarrierType'], d['Color'], d['DueDate']) for d in json_data['Demands']]
    rounds = [Round(r['ScheduledCarriers']) for r in json_data['Rounds']]
    return DataModel(
        json_data['NumCarrierTypes'],
        json_data['NumColors'],
        json_data['HistoryColor'],
        demands,
        rounds
    )
