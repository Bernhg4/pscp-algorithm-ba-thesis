import glob
import os
from datetime import datetime

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

from source.models.logging_model import ProgLogfile

# Function to read filenames and parse attributes
def parse_log_files(log_dir="./logging"):
    prog_logs = []

    # Get all CSV files from the directory
    files = glob.glob(os.path.join(log_dir, "*.csv"))
    for filepath in files:

        if "-R0_" not in filepath and "Imp" not in filepath:
            continue

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
        print(f"{datetime.now()} - Read logfile {filepath}")
        prog_logs.append(log)

    return prog_logs

def read_log_file(filepath, log):
    with open(filepath, "r") as file:
        # Skip the header line
        sa = False
        if "Temperature" in next(file):
            sa = True
            log.set_sa()
        # Read each line, extract values, and add them as points
        for line in file:
            if not ";" in line:
                continue

            if not sa:
                timestamp_str, violations_str, changes_str = line.strip().split(";")
                timestamp = datetime.fromisoformat(timestamp_str)  # Convert string to datetime
                violations = int(violations_str)
                changes = int(changes_str)
                log.add_point(timestamp, violations, changes)
            else:
                timestamp_str, violations_str, changes_str, temperature_str, curr_changes_str, curr_viol_str, acc_rate = line.strip().split(";")
                timestamp = datetime.fromisoformat(timestamp_str)  # Convert string to datetime
                violations = int(violations_str)
                changes = int(changes_str)
                temperature = float(temperature_str)
                curr_changes = int(curr_changes_str)
                curr_viol = int(curr_viol_str)
                log.add_point(timestamp, violations, changes)
                log.add_additional_values(temperature, curr_changes,curr_viol)

    log.reduce_points()


def create_plots(logfiles):
    # Ensure the "plots" directory exists
    os.makedirs("plots", exist_ok=True)

    # Normalize a dataset to the range [0, 1]
    def normalize(data):
        return (data - np.min(data)) / (np.max(data) - np.min(data))

    # Loop through log files
    for log in logfiles:

        # Normalize each dataset
        #changes_data = normalize(log.all_changes)
        changes_data = log.all_changes
        #violations_data = normalize(log.all_violations)
        violations_data = log.all_violations
        if log.all_temperatures:
            temperatures_data = normalize(log.all_temperatures)
            temperatures_data = log.all_temperatures
            #current_changes_data = normalize(log.all_current_changes)
            current_changes_data = log.all_current_changes
            current_viol_data = log.all_current_violations

        # Convert datetime objects to ISO format for JSON serialization
        timestamps = [dt.isoformat() for dt in log.all_timestamps]

        # Create a figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        figTemp = make_subplots()

        # Add Changes or Temperatures trace (primary y-axis)
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=changes_data,
                mode="lines+markers",
                name="Best color changes",
                line=dict(color="orange"),
                marker=dict(symbol="x"),
            ),
            secondary_y=False
        )

        if log.all_temperatures:
            fig.add_trace(
                go.Scatter(
                    x=timestamps,
                    y=current_changes_data,
                    mode="lines+markers",
                    name="Current color changes",
                    line=dict(color="orangered"),
                    marker=dict(symbol="x"),
                ),
                secondary_y=False
            )
            fig.add_trace(
                go.Scatter(
                    x=timestamps,
                    y=current_viol_data,
                    mode="lines+markers",
                    name="Current demand violations",
                    line=dict(color="darkblue"),
                    marker=dict(symbol="circle"),
                ),
                secondary_y=True
            )

            figTemp.add_trace(
                go.Scatter(
                    x=timestamps,
                    y=temperatures_data,
                    mode="lines+markers",
                    name="Temperature",
                    line=dict(color="orangered"),
                    marker=dict(symbol="x"),
                ),
                secondary_y=False
            )
            # Update x-axis for datetime format
            figTemp.update_xaxes(
                tickformat="%H:%M:%S.%f",
                tickangle=45,  # Rotate labels for clarity
            )

        # Add Violations or acceptance rate trace (secondary y-axis)
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=violations_data,
                mode="lines+markers",
                name="Best demand violations",
                line=dict(color="cornflowerblue"),
                marker=dict(symbol="circle"),
            ),
            secondary_y=True
        )

        # Update layout for titles and axes
        fig.update_layout(
            #title=f"Log for first improvement - instance 10",
            title=f"Log for {log.instance} ({log.algorithm})",
            title_font=dict(size=24),  # Bigger title font
            xaxis=dict(
                title="Timestamps",
                title_font=dict(size=22),  # Bigger x-axis title
                tickfont=dict(size=20)  # Bigger x-axis tick labels
            ),
            yaxis=dict(
                title="Changes",
                titlefont=dict(size=22, color="orange"),  # Bigger y-axis title
                tickfont=dict(size=20)  # Bigger y-axis tick labels
            ),
            yaxis2=dict(
                title="Violations",
                titlefont=dict(size=22, color="cornflowerblue"),  # Bigger secondary y-axis title
                tickfont=dict(size=20)  # Bigger secondary y-axis tick labels
            ),
            legend=dict(
                font=dict(size=18),  # Bigger legend text
                x=0.9,  # Moves legend inside (0 = left, 1 = right)
                y=0.9,  # Moves legend inside (0 = bottom, 1 = top)
                xanchor="right",  # Aligns legend box to the right
                yanchor="top",  # Aligns legend box to the top
                bgcolor="rgba(255,255,255,0.7)"  # Optional: Adds a semi-transparent white background
            )
        )

        # Update x-axis for datetime format
        fig.update_xaxes(
            tickformat="%H:%M:%S.%f",
            tickangle=45,  # Rotate labels for clarity
        )


        # Save the plot as an HTML file
        #plot_filename = f"plots/{log.instance}_{log.algorithm}_plot.html"
        #fig.write_html(plot_filename)

        # Save the plot as a PNG file
        plot_filename = f"plots/{log.instance}_{log.algorithm}_plot.pdf"
        print(f"{datetime.now()} - Plotting {plot_filename}")
        #fig.write_image(plot_filename, format="png", width=1920, height=1080)
        fig.write_image(plot_filename, format="pdf", width=1080, height=720)
        if log.all_temperatures:
            plot_filename = f"plots/{log.instance}_{log.algorithm}_temp_plot.pdf"
            #figTemp.write_image(plot_filename, format="png", width=1920, height=1080)
            figTemp.write_image(plot_filename, format="pdf", width=1920, height=1080)


if __name__ == "__main__":

    logfiles = parse_log_files()
    create_plots(logfiles)