import glob
import os
from datetime import datetime

from matplotlib import pyplot as plt
import matplotlib.dates as mdates

from source.models.logging_model import ProgLogfile

# Function to read filenames and parse attributes
def parse_log_files(log_dir="./logging"):
    prog_logs = []

    # Get all CSV files from the directory
    files = glob.glob(os.path.join(log_dir, "*.csv"))
    for filepath in files:
        filename = os.path.basename(filepath)
        # Split the filename by "_"
        parts = filename.split("_")

        # Extract the required elements
        start = f"{parts[-3]}-{parts[-2]}-{parts[-1].split('.')[0]}"
        algorithm = parts[-4]
        instance = "_".join(parts[1:-4])

        # Create ProgLogfile instance
        log = ProgLogfile(start=start, instance=instance, algorithm=algorithm)
        read_log_file(filepath, log)  # Read and parse the file content
        prog_logs.append(log)

    return prog_logs

def read_log_file(filepath, log):
    with open(filepath, "r") as file:
        # Skip the header line
        next(file)
        # Read each line, extract values, and add them as points
        for line in file:
            timestamp_str, violations_str, changes_str = line.strip().split(";")
            timestamp = datetime.fromisoformat(timestamp_str)  # Convert string to datetime
            violations = int(violations_str)
            changes = int(changes_str)
            log.add_point(timestamp, violations, changes)


def create_plots(logfiles):
    # Ensure the "plots" directory exists
    os.makedirs("plots", exist_ok=True)

    for log in logfiles:
        fig, ax1 = plt.subplots(figsize=(12, 6))

        # Plot Changes on the primary y-axis (left side)
        ax1.plot(log.all_timestamps, log.all_changes, label="Changes", color="orange", marker="x")
        ax1.set_xlabel("Timestamp")
        ax1.set_ylabel("Changes", color="orange")
        ax1.tick_params(axis="y", labelcolor="orange")

        # Format the x-axis for datetime with milliseconds
        ax1.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S.%f"))
        ax1.xaxis.set_major_locator(mdates.AutoDateLocator())
        fig.autofmt_xdate()  # Rotate date labels for clarity

        # Create a secondary y-axis for Violations (right side)
        ax2 = ax1.twinx()
        ax2.plot(log.all_timestamps, log.all_violations, label="Violations", color="cornflowerblue", marker="o")
        ax2.set_ylabel("Violations", color="cornflowerblue")
        ax2.tick_params(axis="y", labelcolor="cornflowerblue")

        # Title
        plt.title(f"Log Data for {log.instance} ({log.algorithm}) - Start: {log.start}")

        # Save the plot to the "plots" folder
        plot_filename = f"plots/{log.instance}_{log.algorithm}_plot.png"
        plt.savefig(plot_filename)
        plt.close()  # Close the figure to free memory


if __name__ == "__main__":

    logfiles = parse_log_files()
    create_plots(logfiles)