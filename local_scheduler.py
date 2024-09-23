import json
import psutil  # https://pypi.org/project/psutil/
import threading
import time
import os
import subprocess

from datetime import datetime, timedelta
from itertools import product
from concurrent.futures import ThreadPoolExecutor

# Experiment details and parameters to be set before execution
# Full paths are used for better clarity and to allow running the executable
# from a different directory
EXECUTABLE_WORKING_DIRECTORY = "executable"
EXECUTABLE_PATH = "/home/sam/Documents/Estudios/Doctorado/retreats/1/examples/experiments_example/executable/executable.py"

EXPERIMENT_ID = f"{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}"  # Or something else

EXPERIMENT_DESCRIPTION = """
**Initial version**
    ...
    ...
    ...
"""

EXPERIMENT_PATH = f"/home/sam/Documents/Estudios/Doctorado/retreats/1/examples/experiments_example/experiments/{EXPERIMENT_ID}/"

# We could also write it manually and avoid doing it from here
# if it is too complex. In that case, the script would look for
# it and keep a copy
FIXED_CONFIGURATION = {
    "fixed_parameter_1": 1,
    "fixed_parameter_2": 2,
    # ...
    "fixed_parameter_n": 3,
}

PARAMETER_1_VALUES = ["technique1", "technique2", "technique3"]
PARAMETER_2_VALUES = ["technique1", "technique2", "technique3"]
# ...
PARAMETER_N_VALUES = [1, 2, 3]

PARAMETER_COMBINATIONS = [
    PARAMETER_1_VALUES,
    PARAMETER_2_VALUES,
    # ...
    PARAMETER_N_VALUES
]

def run_and_log_executable(input_parameters, output_dir):
    # Runs the executable. It will log the maximum memory usage
    # and elapsed time in a .json file

    def memory_usage_tracker(pid, stop_event):
        # Simple memory tracking thread using the psutil library
        #
        # It could also be used to create a histogram of resource
        # consumption across time
        process = psutil.Process(pid)

        max_memory = 0
        while not stop_event.is_set():
            # It can also be used to measure CPU usage, etc
            current_memory = process.memory_info().rss
            max_memory = max(max_memory, current_memory)
            time.sleep(0.1)

        return max_memory

    # Start the memory usage thread
    with ThreadPoolExecutor() as executor:
        stop_event = threading.Event()

        # Run the executable and get the elapsed time
        time_start = time.perf_counter()
        
        # Turn all params into strings so that we can call the executable via CLI
        input_parameters = [str(param) for param in input_parameters]
        # Call the process asynchronously so that we can grab its PID
        process = subprocess.Popen(["python", EXECUTABLE_PATH] + list(input_parameters) + [output_dir + "/raw_output/"], 
                                   cwd=EXECUTABLE_WORKING_DIRECTORY) # Execute it form its directory, keeps everything cleaner
        # Track it
        future = executor.submit(memory_usage_tracker, process.pid, stop_event)
        # And wait for it
        stdout, stderr = process.communicate()

        time_end = time.perf_counter()
        time_delta = timedelta(seconds=time_end - time_start)

        # Stop the memory usage thread
        stop_event.set()
        max_memory = future.result()

        # Create the logfile
        log = {
            "input_parameters": input_parameters,
            "time_elapsed_seconds": time_delta.seconds,
            "time_elapsed_str": str(time_delta),
            "max_memory_usage_bytes": max_memory
        }

        # Useful to create not-yet-existing directories in the way
        os.makedirs(os.path.dirname(output_dir), exist_ok=True)
        with open(os.path.join(output_dir, "log.json"), "w") as f:
            json.dump(log, f, indent=4)


# Useful to create not-yet-existing directories in the way
os.makedirs(os.path.dirname(EXPERIMENT_PATH), exist_ok=True)
with open(os.path.join(EXPERIMENT_PATH, "experiment_description.md"), "w") as f:
    f.write(EXPERIMENT_DESCRIPTION)

# Prepare the fixed configuration file
#
# Place it wherever the executable needs it, and also save it
# to the experiment's folder
with open('executable/fixed_configuration.json', 'w') as f:
    json.dump(FIXED_CONFIGURATION, f, indent=4)

with open(os.path.join(EXPERIMENT_PATH, "fixed_configuration.json"), "w") as f:
    json.dump(FIXED_CONFIGURATION, f, indent=4)

# Run the loop
for execution_count, input_parameters in enumerate(list(product(*PARAMETER_COMBINATIONS))):
    path_for_run = os.path.join(EXPERIMENT_PATH, f"parameter_combination_{execution_count}")
    run_and_log_executable(input_parameters, path_for_run)

# Now we have the results, so we can evaluate them, create tables, diagrams, etc.
for run_path in [f.path for f in os.scandir(EXPERIMENT_PATH) if f.is_dir()]:
    # Run the evaluation on os.path.join(run_path, "raw_output"), 'rb')
    # ...
    # All of this is to be saved in an evaluation directory or similar within run_path
    continue  # To not make python explode

# Now we can choose the best result, create tables again, etc.
