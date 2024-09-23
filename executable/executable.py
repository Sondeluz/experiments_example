import json
import argparse
import pickle
import random
import os
import logging

def run(parameter_1, parameter_2, parameter_n, output_dir):
    with open("fixed_configuration.json") as f:
        fixed_config = json.load(f)

    with open(os.path.join(output_dir, 'output.txt'), 'w') as output_file:
        logger.debug('Pommi is debugging')
        logger.info('Pommi wants to inform you of something')
        logger.warning('Pommi wants to warn you about something')
        logger.error('Pommi needs your help!')

        output_file.write(str(random.uniform(0.0, 1.0)))

if __name__ == "__main__":
    parser = argparse.ArgumentParser("executable")
    parser.add_argument("parameter_1", type=str)
    parser.add_argument("parameter_2", type=str)
    # ...
    parser.add_argument("parameter_n", type=int)
    parser.add_argument("output_dir", type=str)

    args = parser.parse_args()

    # Useful to create not-yet-existing directories in the way
    os.makedirs(args.output_dir, exist_ok=True)

    # Log to a file, not the terminal. It will be part of the executable's output
    logger = logging.getLogger(__name__)
    logging.basicConfig(filename=os.path.join(args.output_dir, 'logger_output.log'),
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        encoding='utf-8', 
                        level=logging.DEBUG)

    run(args.parameter_1,
        args.parameter_2,
        args.parameter_n,
        args.output_dir)
