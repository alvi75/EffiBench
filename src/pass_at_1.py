import os
import shutil
import subprocess
from tqdm import tqdm

# Define paths
executed_code_dir = "../executed_code/gpt-3.5-turbo/"  # Directory where your Python files are located
passed_code_dir = os.path.join(executed_code_dir, "passed")
failed_code_dir = os.path.join(executed_code_dir, "failed")

# Create directories if they don't exist
os.makedirs(passed_code_dir, exist_ok=True)
os.makedirs(failed_code_dir, exist_ok=True)

# Get all Python files in the executed code directory
python_files = [f for f in os.listdir(executed_code_dir) if f.endswith(".py")]

print(f"Found {len(python_files)} Python files for execution.")

# Initialize counters
passed_files = 0
executed_files = 0

# Process each file
for py_file in tqdm(python_files, desc="Processing Python files"):
    py_file_path = os.path.join(executed_code_dir, py_file)
    
    try:
        # 🏃 Execute the Python file and check for assertion errors
        result = subprocess.run(
            ["python3", py_file_path], capture_output=True, text=True, timeout=10
        )

        executed_files += 1  # Count executed files

        # If no assertion errors or exceptions, move to "passed"
        if result.returncode == 0:
            shutil.move(py_file_path, os.path.join(passed_code_dir, py_file))
            passed_files += 1  # Count passed test cases
        else:
            shutil.move(py_file_path, os.path.join(failed_code_dir, py_file))

    except subprocess.TimeoutExpired:
        print(f"⚠️ Timeout: {py_file} took too long to execute.")
        shutil.move(py_file_path, os.path.join(failed_code_dir, py_file))
        executed_files += 1  # Count timeouts as executed files

    except Exception as e:
        print(f"Error in {py_file}: {e}")
        shutil.move(py_file_path, os.path.join(failed_code_dir, py_file))
        executed_files += 1  # Count failed scripts as executed files

# Correctly calculate failed scripts
failed_files = executed_files - passed_files

# Calculate Pass@1 (Using fixed total of 1000 generated scripts)
pass_at_1 = (passed_files / 1000) * 100  

# Print Summary
print("\nProcessing complete!")
print(f"Total scripts executed: {executed_files}")
print(f"passed scripts: {passed_files}")
print(f"Failed scripts: {failed_files}")  # Now correctly calculated
print(f"Pass@1: {pass_at_1:.2f}%")
