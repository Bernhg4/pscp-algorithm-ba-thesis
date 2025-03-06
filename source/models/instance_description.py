import json
import os


def process_file(file_path):
    """
    Reads a JSON file and prints the requested details.

    Args:
        file_path (str): Path to the JSON file.
    """
    try:
        # Read the JSON file
        with open(file_path, 'r') as file:
            data = json.load(file)

        # Extract the required details
        instance_name = os.path.basename(file_path)  # Use the file name as "instance"
        round_capacity = max(len(round_data["ScheduledCarriers"]) for round_data in data["Rounds"])
        colors = data["NumColors"]
        carrier_types = data["NumCarrierTypes"]
        demands_count = len(data["Demands"])

        # Print the details
        print(f"Instance: {instance_name}")
        print(f"Round Capacity: {round_capacity}")
        print(f"Colors: {colors}")
        print(f"Carrier Types: {carrier_types}")
        print(f"Demands: {demands_count}")
        print("")

    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading or parsing file: {e}")

if __name__ == "__main__":

    for x in range(1,12):
        process_file(f"instance{x}.json")
