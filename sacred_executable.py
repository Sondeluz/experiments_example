import random
import os
import time 
import threading
import psutil

from datetime import datetime 
from itertools import product
from concurrent.futures import ThreadPoolExecutor

from sacred import Experiment
from sacred.observers import FileStorageObserver 

EXPERIMENT_ID = f"{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}"  # Or something else
EXPERIMENT_PATH = f"/home/sam/Documents/Estudios/Doctorado/retreats/1/examples/experiments_example/sacred_example/experiments/{EXPERIMENT_ID}/"
    
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

ex = Experiment(EXPERIMENT_ID) # Initialize the experiment
ex.observers.append(FileStorageObserver(EXPERIMENT_PATH)) # Where to save results (files, a DB, cloud...)

# Fixed parameters
ex.add_config('fixed_configuration.json')

# Variable parameters, we just need to initialize them
@ex.config
def my_config():
    parameter_1 = None
    parameter_2 = None
    # ...
    parameter_n = None

# A function whose arguments match config variables declared in @ex.config functions, 
# which can be overriden when calling it
@ex.capture
def run(parameter_1, 
        parameter_2, 
        parameter_n, 
        # _log is the one provided by sacred instead of the one from python's libs
        _log): 
    _log.debug('Pommi is debugging')
    _log.info('Pommi wants to inform you of something')
    _log.warning('Pommi wants to warn you about something')
    _log.error('Pommi needs your help!')        

    time.sleep(random.uniform(0.0, 0.05))

    with open('output.txt', 'w') as output_file:
        output_file.write(str(random.uniform(0.0, 1.0)))

    # Tells sacred to save the output file, also allows adding metadata, a descriptive name, etc.
    ex.add_artifact('output.txt') 

# The main function to which sacred hooks into
@ex.main
def main():
    # Open the fixed config as a Resource and save it. It can be used for datasets, 
    # DBs, etc., which will be saved deduplicated if they didn't change across runs
    ex.open_resource('fixed_configuration.json')
    # All added configs get saved anyways to a common .json file

    # Now the executable logs itself
    def memory_usage_tracker(pid, ex, stop_event):
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
        future = executor.submit(memory_usage_tracker, os.getpid(), ex, stop_event)

        # Run without parameters! sacred will feed them from the variables spawned by @ex.config functions
        run()

        stop_event.set()
        max_memory = future.result()
        # Save it as a metric in a separate file
        ex.log_scalar("max_memory_usage", max_memory)

for execution_count, input_parameters in enumerate(list(product(*PARAMETER_COMBINATIONS))):
    ex.run(options={'--loglevel': 'DEBUG'},
           config_updates={'parameter_1': input_parameters[0], 
                           'parameter_2': input_parameters[1], 
                           'parameter_n': input_parameters[2]})