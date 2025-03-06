import copy
import os
import random
import sys
import time
from datetime import datetime, timedelta
from random import randint

import openpyxl
from openpyxl.styles import Alignment, Font

from source.jsonIO.json_rw import load_json_file, instance_from_json
from source.models.result_models import ResultSto, ResultDet
from source.solvers.solutionGenerators import random_solution, demands_first, demands_reverse, demand_lookahead_heuristic
from source.solvers.solutionImprovers import run_improver, first_improver, best_improver, \
    first_improver_delta, best_improver_delta, run_sim_annealing
from source.validator.ownSolutionValidator import internal_validate


def test_performance():

    start_time = datetime.now()

    instance_files = [
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
                      '../../data/instance11.json'
                      ]

    algorithms_det = [
        ("Heur DL50", heur_sol_50),
        ("DF oc", df_oc_sol),
        ("DF oc,prio", df_oc_prio_sol),
        ("DF oc,prio,dd", df_oc_prio_dd_sol),
        ("DR", dr_sol)
    ]

    algorithms_sto = [
        ("Random", rand_sol),
        ("SA",sim_ann),
        ("DF", df_sol)
    ]

    algorithms_impro = [
        ("FirImp_delta",first_imp_delta),
        ("BesImp_delta",best_imp_delta)
    ]

    instances = []
    for idx, instance_file in enumerate(instance_files):
        instance_data = load_json_file(instance_file)
        instances.append((os.path.splitext(os.path.basename(instance_file))[0], instance_from_json(instance_data)))

    # any other than SA
    max_run_time_minutes = 60
    rand_seed_list = []

    results = []
    wb_last_name = ""
    for instance in instances:
        print("")
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

        for algo in [i for i in algorithms_sto if "SA" not in i[0]]:
            print(f"    Running 10x algo {algo[0]} {datetime.now()}")
            result = ResultSto(algo[0], instance[0], "stochastic")
            seeds = []

            for i in range(1):
                used_seed = randint(1, 100000)
                random.seed(used_seed)
                seeds.append(used_seed)

                start = time.perf_counter()
                solution = algo[1](instance[1], max_run_time_minutes)
                end = time.perf_counter()

                res = internal_validate(instance[1], solution)
                execution_time = end - start
                result.add_result((res[0], res[1], execution_time))

            results.append(result)
            rand_seed_list.append((instance[0], algo[0], seeds))

        for algo in [i for i in algorithms_sto if "SA" in i[0]]:

            init_solution = df_oc_prio_dd_sol(instance[1], max_run_time_minutes)
            seeds = []

            t_inits = [4.5]
            max_times = [60]
            cutoff_values = [1e-300]
            demand_biases = [2]

            rand_iter = 10

            max_iterations = len(t_inits) * len(max_times) * len(cutoff_values) * len(demand_biases)
            curr_iteration = 0
            print(f"    Running {max_iterations} algo {algo[0]} {datetime.now()} until max ~ {datetime.now() + timedelta(minutes=(max_iterations/len(max_times))*sum(max_times)*rand_iter)}")

            for t_init in t_inits:
                for m_time in max_times:
                    for bias in demand_biases:
                        for cutoff in cutoff_values:

                            temp_name = f"{algo[0]}-T{t_init}-MT{m_time}-CV{cutoff}-DB{bias}"
                            result = ResultSto(temp_name, instance[0], "stochastic")
                            print(f"        SA run {curr_iteration+1}/{max_iterations} {datetime.now()}")
                            curr_iteration += 1
                            for i in range(rand_iter):
                                print(f"            iteration {i + 1}/{rand_iter} {datetime.now()}")
                                filename = f'logging/ts_{instance[0]}_{temp_name}-R{i}_{datetime.now().strftime("%H_%M_%S")}.csv'
                                log_info = (filename, True, temp_name)

                                used_seed = randint(1, 100000)
                                random.seed(used_seed)
                                seeds.append(used_seed)

                                start = time.perf_counter()
                                solution = algo[1](instance[1], copy.deepcopy(init_solution),log_info, m_time, t_init,bias, 0, cutoff)
                                end = time.perf_counter()

                                res = internal_validate(instance[1], solution)

                                execution_time = end - start
                                result.add_result((res[0], res[1], execution_time))

                            results.append(result)
                            rand_seed_list.append((instance[0], algo[0], seeds))

        for algo in algorithms_impro:
            print(f"    Running algo {algo[0]} {datetime.now()}")

            temp_name = f"{algo[0]}"
            filename = f'logging/ts_{instance[0]}_{temp_name}_{datetime.now().strftime("%H_%M_%S")}.csv'
            log_info = (filename, False, temp_name)

            start = time.perf_counter()
            solution = df_oc_prio_dd_sol(instance[1], max_run_time_minutes)
            solution = algo[1](instance[1],solution,log_info, max_run_time_minutes)
            end = time.perf_counter()

            res = internal_validate(instance[1], solution)
            execution_time = end - start

            result = ResultDet((res[0],res[1],execution_time),algo[0],instance[0],"deterministic")

            results.append(result)

        # save the data
        workbook = openpyxl.Workbook()
        first_sheet = workbook.active

        export_results_avg(workbook, results, max_run_time_minutes, True)
        export_results_avg(workbook, results, max_run_time_minutes, False)
        export_results_best(workbook, results, max_run_time_minutes, True)
        export_results_best(workbook, results, max_run_time_minutes, False)
        export_seeds(workbook, rand_seed_list)

        workbook.remove(first_sheet)

        if os.path.exists(wb_last_name):
            os.remove(wb_last_name)
        wb_last_name = f'{len(results)}_results_{start_time.strftime("%d-%m")}_{start_time.strftime("%H-%M-%S")}.xlsx'
        workbook.save(wb_last_name)

def export_results_avg(wb, results, time_limit_min, quality):

    mode = "Cost" if quality else "Time[m]"
    sheet = wb.create_sheet(title=f'results_avg_{mode.replace("[m]", "").lower()}')

    unique_instances = sorted({result.instance for result in results})
    deterministic_algorithms = list({result.algorithm for result in results if result.method == "deterministic"})
    stochastic_algorithms = list({result.algorithm for result in results if result.method == "stochastic"})
    unique_algorithms = deterministic_algorithms + stochastic_algorithms
    str_algos = [""] + [str(x) for x in deterministic_algorithms]

    str_algos.extend([item for alg in stochastic_algorithms for item in [alg, ""]])


    data = [
        ["",f"Maximum runtime: {time_limit_min} min",],
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

def export_results_best(wb, results, time_limit_min, quality):

    mode = "Cost" if quality else "Time[m]"
    sheet = wb.create_sheet(title=f'results_best_{mode.replace("[m]", "").lower()}')

    unique_instances = sorted({result.instance for result in results})
    deterministic_algorithms = list({result.algorithm for result in results if result.method == "deterministic"})
    stochastic_algorithms = list({result.algorithm for result in results if result.method == "stochastic"})
    str_algos = [""] + [str(x) for x in deterministic_algorithms]
    str_algos.extend(stochastic_algorithms)

    data = [
        ["",f"Maximum runtime: {time_limit_min} min",],
        ["","Deterministic"] + ["" for _ in range(len(deterministic_algorithms)-1)] + ["Stochastic"],
        str_algos ,
        ["Instances"] + [mode for _ in deterministic_algorithms] + [f"Best {mode}" for _ in stochastic_algorithms]
    ]

    for row in data:
        sheet.append(row)

    sheet.merge_cells(start_row=1, start_column=2, end_row=1, end_column=len(deterministic_algorithms) + len(stochastic_algorithms)+1)
    sheet.merge_cells(start_row=2, start_column=2, end_row=2, end_column=len(deterministic_algorithms)+1)
    sheet.merge_cells(start_row=2, start_column=len(deterministic_algorithms) + 2, end_row=2, end_column=len(deterministic_algorithms) + len(stochastic_algorithms)+1)

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

def export_seeds(wb, seed_list):

    sheet = wb.create_sheet(title='used_seeds')

    data = [ ["Instance", "Algorithm"] + [str(seed_list[0][2].index(x)+1) + ". run" for x in seed_list[0][2]]]
    for (instance,algo,seeds) in seed_list:
        data.append([instance, algo] + [str(x) for x in seeds])
    for row in data:
        sheet.append(row)

# Define a function for the work in each iteration
def run_single_combination(algo, t_init, cool_rate, bias, cutoff, instance, max_run_time_minutes, rand_iter):
    temp_name = f"{algo[0]}-T{t_init}-CR{cool_rate}-CV{cutoff}-DB{bias}"
    result = ResultSto(temp_name, instance[0], "stochastic")
    seeds = []
    init_solution = df_oc_sol(instance[1], max_run_time_minutes)

    for i in range(rand_iter):
        #init_logging(instance[0], f"{temp_name}-R{i}", True)
        filename = f'logging/ts_{instance[0]}_{temp_name}-R{i}_{datetime.now().strftime("%H_%M_%S")}.csv'
        log_info = (filename, True, temp_name)

        used_seed = randint(1, 100000)
        random.seed(used_seed)
        seeds.append(used_seed)

        start = time.perf_counter()
        solution = algo[1](
            instance[1], copy.deepcopy(init_solution), log_info,
            max_run_time_minutes, t_init, bias, cool_rate, cutoff
        )
        end = time.perf_counter()

        res = internal_validate(instance[1], solution)
        execution_time = end - start
        result.add_result((res[0], res[1], execution_time))

    return result, seeds

def rand_sol(instance_file, time_limit_min):
    return random_solution(instance_file,time_limit_min*60)

def sim_ann(instance_file, solution,log_info, time_limit_min, temperature,bias, cool_rate, cutoff):
    return run_sim_annealing(instance_file, solution, log_info, time_limit_min * 60, temperature, bias, cool_rate, cutoff)

def df_sol(instance_file, time_limit_min):
    return demands_first(instance_file,time_limit_min*60)

def heur_sol_50(instance_file, time_limit_min):
    return demand_lookahead_heuristic(instance_file, time_limit_min * 60, 50)

def df_oc_sol(instance_file, time_limit_min):
    return demands_first(instance_file,time_limit_min*60, True)


def df_oc_prio_sol(instance_file, time_limit_min):
    return demands_first(instance_file,time_limit_min*60, True, True)


def df_oc_prio_dd_sol(instance_file, time_limit_min):
    return demands_first(instance_file,time_limit_min*60, True, True, True)


def dr_sol(instance_file, time_limit_min):
    return demands_reverse(instance_file,time_limit_min*60)

def first_imp(instance_file,solution,log_info, run_time_minutes):
    return run_improver(instance_file, solution,log_info, first_improver, run_time_minutes * 60)

def first_imp_delta(instance_file,solution,log_info, run_time_minutes):
    return run_improver(instance_file, solution,log_info, first_improver_delta, run_time_minutes * 60)


def best_imp(instance_file,solution,log_info, run_time_minutes):
    return run_improver(instance_file, solution,log_info, best_improver, run_time_minutes * 60)

def best_imp_delta(instance_file,solution,log_info, run_time_minutes):
    return run_improver(instance_file, solution,log_info, best_improver_delta, run_time_minutes * 60)


if __name__ == "__main__":
    test_performance()