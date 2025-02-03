import json
import os
import glob
import shutil
from tqdm import tqdm

# Paths
executed_code_dir = "../executed_code/deepseek-coder-1.3b-instruct"
passed_code_dir = os.path.join(executed_code_dir, "passed")
failed_code_dir = os.path.join(executed_code_dir, "failure")

# Create directories if they don't exist
os.makedirs(executed_code_dir, exist_ok=True)
os.makedirs(passed_code_dir, exist_ok=True)
os.makedirs(failed_code_dir, exist_ok=True)

def calculate_memory_usage(dat_file_path):
    with open(dat_file_path, 'r') as file:
        prev_time, prev_mem_mb, mem_time_mb_s = 0, 0, 0
        next(file)  # Skip header
        for line in file:
            if "__main__." in line:
                continue
            parts = line.split()
            mem_in_mb = float(parts[1])
            timestamp = float(parts[2])
            if prev_time > 0:
                time_interval_s = timestamp - prev_time
                mem_time_mb_s += (prev_mem_mb + mem_in_mb) / 2 * time_interval_s
            prev_time, prev_mem_mb = timestamp, mem_in_mb
        return mem_time_mb_s

def calculate_runtime(dat_file_path):
    with open(dat_file_path, 'r') as file:
        start_time, end_time = float("inf"), float("-inf")
        next(file)  # Skip header
        for line in file:
            if "__main__." in line:
                continue
            timestamp = float(line.split()[2])
            start_time, end_time = min(start_time, timestamp), max(end_time, timestamp)
        return max(end_time - start_time, 0)

def report_max_memory_usage(dat_file_path):
    max_memory_usage = 0
    with open(dat_file_path, 'r') as file:
        next(file)  # Skip header
        for line in file:
            if "__main__." in line:
                continue
            mem_in_mb = float(line.split()[1])
            max_memory_usage = max(max_memory_usage, mem_in_mb)
        return max_memory_usage

model_list = ["deepseek-coder-1.3b-instruct"]
canonical_solution_directory = "../dat_results/canonical_solution"
canonical_solution_memory_usage, canonical_solution_execution_time, canonical_solution_max_memory_usage = {}, {}, {}

# Load canonical solution performance
for dat_file in glob.glob(os.path.join(canonical_solution_directory, "*.dat")):
    try:
        problem_idx = int(os.path.basename(dat_file).split('.')[0])
        canonical_solution_memory_usage[problem_idx] = calculate_memory_usage(dat_file)
        canonical_solution_execution_time[problem_idx] = calculate_runtime(dat_file)
        canonical_solution_max_memory_usage[problem_idx] = report_max_memory_usage(dat_file)
    except:
        pass

global_result = {}

for model in model_list:
    if "/" in model:
        model = model.split("/")[1]

    completion_memory_usage, execution_time, max_memory_usage, task_idx = {}, {}, {}, {}
    executed_files, passed_files = 0, 0

    dat_directory = f"../dat_results/{model}"

    for dat_file in glob.glob(os.path.join(dat_directory, "*.dat")):
        try:
            problem_idx = int(os.path.basename(dat_file).split('.')[0])
            completion_memory_usage[problem_idx] = calculate_memory_usage(dat_file)
            execution_time[problem_idx] = calculate_runtime(dat_file)
            max_memory_usage[problem_idx] = report_max_memory_usage(dat_file)
            task_idx[problem_idx] = dat_file
            executed_files += 1  # Count executed files

            # Check if test cases passed
            with open(dat_file, "r") as f:
                if "All test cases passed" in f.read():
                    passed_files += 1  # Count passed test cases
                    dest_folder = passed_code_dir
                else:
                    dest_folder = failed_code_dir

            # Move executed scripts to passed or failed folder
            script_path = f"../dat_results/{model}/{problem_idx}.py"
            if os.path.exists(script_path):
                shutil.copy(script_path, os.path.join(dest_folder, f"{problem_idx}.py"))

        except Exception as e:
            print(f"Error processing {dat_file}: {e}")

    global_result[model] = {
        "completion_memory_usage": completion_memory_usage,
        "execution_time": execution_time,
        "max_memory_usage": max_memory_usage,
        "task_idx": task_idx,
        "executed_files": executed_files,
        "passed_files": passed_files
    }

for model in global_result.keys():
    completion_memory_usage = global_result[model]["completion_memory_usage"]
    execution_time = global_result[model]["execution_time"]
    max_memory_usage = global_result[model]["max_memory_usage"]
    executed_files = global_result[model]["executed_files"]
    passed_files = global_result[model]["passed_files"]

    total_execution_time, total_max_memory_usage, total_memory_usage = 0, 0, 0
    total_canonical_solution_execution_time, total_canonical_solution_max_memory_usage, total_canonical_solution_memory_usage = 0, 0, 0
    normalized_execution_time_list, normalized_max_memory_usage_list, normalized_memory_usage_list = [], [], []

    max_net, max_nmu, max_tmu = 0, 0, 0
    net_gt_5, nmu_gt_5, tmu_gt_5 = 0, 0, 0

    for idx in completion_memory_usage.keys():
        if idx not in canonical_solution_memory_usage.keys():
            continue

        total_memory_usage += completion_memory_usage[idx]
        total_execution_time += execution_time[idx]
        total_max_memory_usage += max_memory_usage[idx]
        total_canonical_solution_max_memory_usage += canonical_solution_max_memory_usage[idx]
        total_canonical_solution_memory_usage += canonical_solution_memory_usage[idx]
        total_canonical_solution_execution_time += canonical_solution_execution_time[idx]

        net = execution_time[idx] / canonical_solution_execution_time[idx]
        normalized_execution_time_list.append(net)
        max_net = max(max_net, net)
        if net > 5:
            net_gt_5 += 1

        nmu = max_memory_usage[idx] / canonical_solution_max_memory_usage[idx]
        normalized_max_memory_usage_list.append(nmu)
        max_nmu = max(max_nmu, nmu)
        if nmu > 5:
            nmu_gt_5 += 1

        tmu = completion_memory_usage[idx] / canonical_solution_memory_usage[idx]
        normalized_memory_usage_list.append(tmu)
        max_tmu = max(max_tmu, tmu)
        if tmu > 5:
            tmu_gt_5 += 1

    if len(normalized_execution_time_list) == 0:
        print(model)
        continue

    normalized_execution_time = sum(normalized_execution_time_list) / len(normalized_execution_time_list)
    normalized_max_memory_usage = sum(normalized_max_memory_usage_list) / len(normalized_max_memory_usage_list)
    normalized_memory_usage = total_memory_usage / total_canonical_solution_memory_usage
    total_execution_time /= len(normalized_execution_time_list)
    total_memory_usage /= len(normalized_execution_time_list)
    total_max_memory_usage /= len(normalized_execution_time_list)

    pass1 = (executed_files / 1000) * 100
    pass_at_1 = (passed_files / executed_files) * 100  # **✅ Corrected Pass@1 Calculation**

    # Print all metrics
    print(f"{model}&"
          f"{total_execution_time:.2f}&{normalized_execution_time:.2f}&{max_net:.2f}&{net_gt_5}&"
          f"{total_max_memory_usage:.2f}&{normalized_max_memory_usage:.2f}&{max_nmu:.2f}&{nmu_gt_5}&"
          f"{total_memory_usage:.2f}&{normalized_memory_usage:.2f}&{max_tmu:.2f}&{tmu_gt_5}&"
          f"{pass1:.2f}&{pass_at_1:.2f}\\\\")
