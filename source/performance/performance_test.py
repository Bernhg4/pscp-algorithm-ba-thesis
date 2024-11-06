import copy
import os
import random
import sys
import time
from datetime import datetime
from hashlib import algorithms_available
from random import randint

import openpyxl
import pandas as pd
from openpyxl.descriptors import Integer

from openpyxl.styles import PatternFill, Alignment, Font
from openpyxl.workbook import Workbook

from source.jsonIO.json_rw import load_json_file, instance_from_json
from source.models.result_models import ResultSto, ResultDet
from source.solvers.solutionGenerators import random_solution, demands_first, demands_reverse, heuristic_solution
from source.solvers.solutionImprovers import run_improver, primitive_first_improver, primitive_best_improver, \
    init_logging
from source.validator.ownSolutionValidator import internal_validate

def test_performance():
    instance_files = ['../../data/PSCCP_Instance1.json',
                      '../../data/PSCCP_Instance2.json',
                      '../../data/PSCCP_Instance3.json',
                      '../../data/PSCCP_Instance4.json',
                      '../../data/PSCCP_Instance5.json',
                      '../../data/PSCCP_Instance6.json',
                      '../../data/PSCCP_Instance7.json',
                      '../../data/instance1.json',
                      '../../data/instance2.json',
                      '../../data/instance3.json',
                      '../../data/instance4.json',
                      '../../data/instance5.json',
                      '../../data/instance6.json',
                      '../../data/instance7.json',
                      '../../data/instance8.json',
                      '../../data/instance9.json',
                      '../../data/instance10.json',
                      '../../data/instance11.json',
                      '../../data/ToyInstance_ok.json'
                      ]

    algorithms_det = [
        ("Heuristic", heur_sol),
        ("DF oc", df_oc_sol),
        ("DF oc,prio", df_oc_prio_sol),
        ("DF oc,prio,dd", df_oc_prio_dd_sol),
        ("DR", dr_sol)
    ]

    algorithms_sto = [
        ("Random", rand_sol),
        ("DF", df_sol)
    ]

    algorithms_impro = [
        ("FirstImp",first_imp),
        ("BestImp",best_imp)
    ]

    instances = []
    for idx, instance_file in enumerate(instance_files):
        instance_data = load_json_file(instance_file)
        instances.append((os.path.splitext(os.path.basename(instance_file))[0], instance_from_json(instance_data)))
        #instances.append(("I" + str(idx + 1), instance_from_json(instance_data)))

    max_run_time_minutes = 10
    used_seed = randint(1000,10000)
    random.seed(used_seed)

    results = []
    for instance in instances:

        print(f"Running instance {instance[0]} {datetime.now()}")

        for algo in algorithms_det:

            print(f"    Running algo {algo[0]} {datetime.now()}")
            start = time.perf_counter()
            solution = algo[1](instance[1], max_run_time_minutes)
            end = time.perf_counter()

            res = internal_validate(instance[1], solution)
            execution_time = end - start

            result = ResultDet((res[0],res[1],execution_time),algo[0],instance[0],"deterministic")

            results.append(result)

        for algo in algorithms_sto:
            print(f"    Running 10x algo {algo[0]} {datetime.now()}")
            result = ResultSto(algo[0],instance[0],"stochastic")

            for i in range(10):
                start = time.perf_counter()
                solution = algo[1](instance[1], max_run_time_minutes)
                end = time.perf_counter()

                res = internal_validate(instance[1], solution)
                execution_time = end - start
                result.add_result((res[0],res[1],execution_time))

            results.append(result)

        for algo in algorithms_impro:
            print(f"    Running algo {algo[0]} {datetime.now()}")

            init_logging(instance[0],algo[0])
            start = time.perf_counter()
            solution = df_sol(instance[1], max_run_time_minutes)
            solution = algo[1](instance[1],solution,max_run_time_minutes)
            end = time.perf_counter()

            res = internal_validate(instance[1], solution)
            execution_time = end - start

            result = ResultDet((res[0],res[1],execution_time),algo[0],instance[0],"deterministic")

            results.append(result)

    export_results_avg(results, max_run_time_minutes,used_seed,True)
    export_results_avg(results, max_run_time_minutes,used_seed, False)
    export_results_best(results, max_run_time_minutes,used_seed, True)
    export_results_best(results, max_run_time_minutes,used_seed, False)

    '''
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

def export_results_avg(results, time_limit_min, seed, quality):

    workbook = openpyxl.Workbook()
    sheet = workbook.active
    mode = "Cost" if quality else "Time[m]"

    unique_instances = sorted({result.instance for result in results})
    deterministic_algorithms = list({result.algorithm for result in results if result.method == "deterministic"})
    stochastic_algorithms = list({result.algorithm for result in results if result.method == "stochastic"})
    unique_algorithms = deterministic_algorithms + stochastic_algorithms
    str_algos = [""] + [str(x) for x in deterministic_algorithms]

    str_algos.extend([item for alg in stochastic_algorithms for item in [alg, ""]])


    data = [
        ["",f"Maximum runtime: {time_limit_min} min - Randseed: {seed}",],
        ["","Deterministic"] + ["" for _ in range(len(deterministic_algorithms)-1)] + ["Stochastic"],
        str_algos ,
        ["Instances"] + [mode for _ in deterministic_algorithms] + [item for _ in stochastic_algorithms for item in [f"Avg {mode}","SD"]]
    ]

    for row in data:
        sheet.append(row)

    sheet.merge_cells(start_row=1, start_column=2, end_row=1, end_column=len(deterministic_algorithms) + 2 * len(stochastic_algorithms)+1)
    sheet.merge_cells(start_row=2, start_column=2, end_row=2, end_column=len(deterministic_algorithms)+1)
    sheet.merge_cells(start_row=2, start_column=len(deterministic_algorithms) + 2, end_row=2, end_column=len(deterministic_algorithms) + 2 * len(stochastic_algorithms)+1)

    start_col = 2 + len(deterministic_algorithms)
    for _ in stochastic_algorithms:
        sheet.merge_cells(start_row=3, start_column=start_col, end_row=3, end_column=start_col+1)
        sheet.cell(row=3, column=start_col).alignment = Alignment(horizontal="center")
        start_col += 2

    sheet.cell(row=1, column=2).alignment = Alignment(horizontal="center")
    sheet.cell(row=2, column=2).alignment = Alignment(horizontal="center")
    sheet.cell(row=2, column=len(deterministic_algorithms) + 2).alignment = Alignment(horizontal="center")

    row_index = 5
    for ui in unique_instances:
        output = [ui] + [""] * (len(str_algos)-1)
        best_res = (sys.maxsize,sys.maxsize, sys.maxsize)
        col_indexes = []

        for r in sorted([x for x in results if x.instance == ui],key=lambda x: x.method != "deterministic"):
            re = r.get_result()
            position = str_algos.index(r.algorithm)

            if quality:
                if re[0] == best_res[0] and re[1] == best_res[1]:
                    best_res = (re[0], re[1], re[2])
                    col_indexes += [position + 1]
                if re[0] < best_res[0] or (re[0] == best_res[0] and re[1] < best_res[1]):
                    best_res = (re[0], re[1], re[2])
                    col_indexes = [position + 1]

                if r.method == "deterministic":
                    output[position] = f"{re[0]}/{re[1]}"
                elif r.method == "stochastic":
                    sd = r.get_stand_dev()
                    output[position] = f"{re[0]}/{re[1]}"
                    output[position + 1] = f"{sd[0]}/{sd[1]}"
            else:
                if re[2] == best_res[2]:
                    best_res = (re[0], re[1], re[2])
                    col_indexes += [position + 1]
                if re[2] < best_res[2]:
                    best_res = (re[0], re[1], re[2])
                    col_indexes = [position + 1]

                if r.method == "deterministic":
                    output[position] = f"{round(re[2]/60,2)}"
                elif r.method == "stochastic":
                    sd = r.get_stand_dev()
                    output[position] = f"{round(re[2]/60,2)}"
                    output[position + 1] = f"{round(sd[2]/60,2)}"

        sheet.append(output)
        for x in col_indexes:
            sheet.cell(row=row_index, column=x).font = Font(bold=True)

        row_index += 1

    workbook.save(f"results_avg_{mode.replace("[m]","").lower()}.xlsx")

def export_results_best(results, time_limit_min, seed,quality):

    workbook = openpyxl.Workbook()
    sheet = workbook.active
    mode = "Cost" if quality else "Time[m]"

    unique_instances = sorted({result.instance for result in results})
    deterministic_algorithms = list({result.algorithm for result in results if result.method == "deterministic"})
    stochastic_algorithms = list({result.algorithm for result in results if result.method == "stochastic"})
    str_algos = [""] + [str(x) for x in deterministic_algorithms]
    str_algos.extend(stochastic_algorithms)

    data = [
        ["",f"Maximum runtime: {time_limit_min} min - Randseed: {seed}",],
        ["","Deterministic"] + ["" for _ in range(len(deterministic_algorithms)-1)] + ["Stochastic"],
        str_algos ,
        ["Instances"] + [mode for _ in deterministic_algorithms] + [f"Best {mode}" for _ in stochastic_algorithms]
    ]

    for row in data:
        sheet.append(row)

    sheet.merge_cells(start_row=1, start_column=2, end_row=1, end_column=len(deterministic_algorithms) + len(stochastic_algorithms)+1)
    sheet.merge_cells(start_row=2, start_column=2, end_row=2, end_column=len(deterministic_algorithms)+1)
    sheet.merge_cells(start_row=2, start_column=len(deterministic_algorithms) + 2, end_row=2, end_column=len(deterministic_algorithms) + len(stochastic_algorithms)+1)

    #start_col = 2 + len(deterministic_algorithms)
    #for _ in stochastic_algorithms:
    #    sheet.merge_cells(start_row=3, start_column=start_col, end_row=3, end_column=start_col+1)
    #    sheet.cell(row=3, column=start_col).alignment = Alignment(horizontal="center")
    #    start_col += 2

    sheet.cell(row=1, column=2).alignment = Alignment(horizontal="center")
    sheet.cell(row=2, column=2).alignment = Alignment(horizontal="center")
    sheet.cell(row=2, column=len(deterministic_algorithms) + 2).alignment = Alignment(horizontal="center")

    row_index = 5
    for ui in unique_instances:
        output = [ui] + [""] * (len(str_algos)-1)
        best_res = (sys.maxsize,sys.maxsize, sys.maxsize)
        col_indexes = []

        for r in sorted([x for x in results if x.instance == ui],key=lambda x: x.method != "deterministic"):
            re = r.get_best_result()
            position = str_algos.index(r.algorithm)

            if quality:
                if re[0] == best_res[0] and re[1] == best_res[1]:
                    best_res = (re[0], re[1], re[2])
                    col_indexes += [position + 1]
                if re[0] < best_res[0] or (re[0] == best_res[0] and re[1] < best_res[1]):
                    best_res = (re[0], re[1], re[2])
                    col_indexes = [position + 1]
                output[position] = f"{re[0]}/{re[1]}"
            else:
                if re[2] == best_res[2]:
                    best_res = (re[0], re[1], re[2])
                    col_indexes += [position + 1]
                if re[2] < best_res[2]:
                    best_res = (re[0], re[1], re[2])
                    col_indexes = [position + 1]
                output[position] = f"{round(re[2]/60,2)}"



        sheet.append(output)
        for x in col_indexes:
            sheet.cell(row=row_index, column=x).font = Font(bold=True)

        row_index += 1

    workbook.save(f"results_best_{mode.replace("[m]","").lower()}.xlsx")

def rand_sol(instance_file, time_limit_min):
    return random_solution(instance_file,time_limit_min*60)

def df_sol(instance_file, time_limit_min):
    return demands_first(instance_file,time_limit_min*60)

def heur_sol(instance_file, time_limit_min):
    return heuristic_solution(instance_file,time_limit_min*60,20)


def df_oc_sol(instance_file, time_limit_min):
    return demands_first(instance_file,time_limit_min*60, True)


def df_oc_prio_sol(instance_file, time_limit_min):
    return demands_first(instance_file,time_limit_min*60, True, True)


def df_oc_prio_dd_sol(instance_file, time_limit_min):
    return demands_first(instance_file,time_limit_min*60, True, True, True)


def dr_sol(instance_file, time_limit_min):
    return demands_reverse(instance_file,time_limit_min*60)

def first_imp(instance_file,solution, run_time_minutes):
    return run_improver(instance_file,solution, primitive_first_improver , run_time_minutes * 60)

def best_imp(instance_file,solution, run_time_minutes):
    return run_improver(instance_file,solution, primitive_best_improver , run_time_minutes * 60)


if __name__ == "__main__":
    test_performance()