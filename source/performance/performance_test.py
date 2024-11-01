import time
from hashlib import algorithms_available
import pandas as pd

from openpyxl.styles import PatternFill
from openpyxl.workbook import Workbook

from source.jsonIO.json_rw import load_json_file, instance_from_json
from source.solvers.solutionGenerators import random_solution, demands_first, demands_reverse
from source.validator.ownSolutionValidator import internal_validate

def test_performance():
    instance_files = ['../../data/PSCCP_Instance1.json',
                      '../../data/PSCCP_Instance2.json',
                      '../../data/PSCCP_Instance3.json',
                      '../../data/PSCCP_Instance4.json',
                      '../../data/PSCCP_Instance5.json',
                      '../../data/PSCCP_Instance6.json',
                      '../../data/PSCCP_Instance7.json',
                      '../../data/ToyInstance_ok.json']

    algorithms = [("Random", rand_sol),
                  ("DF", df_sol),
                  ("DF oc", df_oc_sol),
                  ("DF oc,prio", df_oc_prio_sol),
                  ("DF oc,prio,dd", df_oc_prio_dd_sol),
                  ("DR", dr_sol)]
    instances = []
    for idx, instance_file in enumerate(instance_files):
        instance_data = load_json_file(instance_file)
        instances.append((idx + 1, instance_from_json(instance_data)))

    results = []
    for instance in instances:

        for algo in algorithms:
            start = time.perf_counter()
            solution = algo[1](instance[1])
            end = time.perf_counter()

            res = internal_validate(instance[1], solution)
            execution_time = end - start

            results.append({
                "Algorithm": algo[0],
                "Execution Time (s)": execution_time,
                "Result": str(res[0]) + "/" + str(res[1]),
                "Instance": instance[0],
            })

    df = pd.DataFrame(results)

    pivot_time = df.pivot(index='Instance', columns='Algorithm', values='Execution Time (s)')
    pivot_result = df.pivot(index='Instance', columns='Algorithm', values='Result')
    # pivot_result = df.pivot_table(index='Instance', columns='Algorithm', values='Result',  aggfunc='first')

    combined_df = pd.concat([pivot_time, pivot_result], axis=1, keys=['ET', 'RE'])
    combined_df.columns = [f'{col[0]}_{col[1]}' for col in combined_df.columns]

    wb = Workbook()
    ws = wb.active


    headers = ['Instance'] + list(combined_df.columns)
    ws.append(headers)  # Append the header row


    for r_idx, (index, row) in enumerate(combined_df.iterrows(), 2):
        ws.cell(row=r_idx, column=1, value=index)  # Instance column
        for c_idx, value in enumerate(row, start=2):
            ws.cell(row=r_idx, column=c_idx, value=value)


    # for cell in ws[1]:
    #    cell.fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")  # Highlight header


    for r_idx in range(2, len(combined_df) + 2):
        max_time = min(
            ws.cell(row=r_idx, column=c_idx).value for c_idx in range(2, len(combined_df.columns) // 2 + 2))
        for c_idx in range(2, len(combined_df.columns) // 2 + 2):  # Adjust range to only the Execution Time columns
            if ws.cell(row=r_idx, column=c_idx).value == max_time:
                ws.cell(row=r_idx, column=c_idx).fill = PatternFill(start_color="FF0000", end_color="FF0000",
                                                                    fill_type="solid")  # Highlight in red


    wb.save('algorithm_performance_results_formatted.xlsx')


    '''
    pivot_time.reset_index(inplace=True)
    pivot_result.reset_index(inplace=True)

    # Function to highlight the maximum value in each row
    def highlight_max(s):
        is_min = s == s.min()
        return ['background-color: green' if v else '' for v in is_min]

    # Apply the highlight_max function row-wise
    styled_df = pivot_time.style.apply(highlight_max, axis=1)
    styled_df_res = pivot_result.style.apply(highlight_max, axis=1)

    combined_df = pd.concat([styled_df, styled_df_res], axis=1, keys=['Execution Time', 'Result'])

    # Optionally, flatten the column MultiIndex
    combined_df.columns = [f'{col[0]}_{col[1]}' for col in combined_df.columns]

    # Save the combined DataFrame to an Excel file
    combined_df.to_excel('algorithm_performance_results.xlsx', engine='openpyxl', index=True)

    # Export to an Excel file with formatting
    #styled_df.to_excel('highlighted_results.xlsx', engine='openpyxl', index=False)
    # Export the DataFrame to a CSV file
    #df.to_csv('algorithm_performance.csv', sep=";", index=False)

    '''


def rand_sol(instance_file):
    return random_solution(instance_file)


def df_sol(instance_file):
    return demands_first(instance_file)


def df_oc_sol(instance_file):
    return demands_first(instance_file, True)


def df_oc_prio_sol(instance_file):
    return demands_first(instance_file, True, True)


def df_oc_prio_dd_sol(instance_file):
    return demands_first(instance_file, True, True, True)


def dr_sol(instance_file):
    return demands_reverse(instance_file)


if __name__ == "__main__":
    test_performance()