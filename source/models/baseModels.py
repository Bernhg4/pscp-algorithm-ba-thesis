import json

class Demand:
    def __init__(self, quantity, carrier_type, color, due_date):
        self.quantity = quantity
        self.carrier_type = carrier_type
        self.color = color
        self.due_date = due_date

    def __str__(self):
        # Define a letter instead of the number and return it with a color instead of a number
        carrier_letter = chr(self.carrier_type + 64)
        return f"{self.quantity}x {carrier_letter}[{["Red","Blue","Green"][self.color-1]}] until R{self.due_date}"

class RoundInstance:
    def __init__(self, scheduled_carriers):
        self.scheduled_carriers = scheduled_carriers

    def __str__(self):
        #return the rounds as letters instead of numbers
        return "".join([f"{chr(carrier + 64)}" for carrier in self.scheduled_carriers])

class RoundSolution:
    def __init__(self, selected_colors):
        self.selected_colors = selected_colors

    def __str__(self):
        # return the rounds as letters instead of numbers
        return "".join([f"{["Red","Blue","Green"][color-1]}" for color in self.selected_colors])

    def to_dict(self):
        return {"SelectedColors": self.selected_colors}

class DataModel:
    def __init__(self, num_carrier_types, num_colors, history_color, demands, rounds):
        self.num_carrier_types = num_carrier_types
        self.num_colors = num_colors
        self.history_color = history_color
        self.demands = demands
        self.rounds = rounds

    def __str__(self):
        #return the rounds formatted like in the description of the problem
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

        return (f"Production plan: {demands_str}\n"
                f"{roundDesc}\n"
                f"{rounds_str}\n"
        )
