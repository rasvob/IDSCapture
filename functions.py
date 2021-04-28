import yaml
import os

def load_settings(confing_filename = 'config.yaml'):
    with open(confing_filename, 'r') as file:
        config_yml = yaml.safe_load(file)
    
    experiment_name = config_yml['experiment_name']
    root_directory = config_yml['root_directory']
    width = config_yml['width']
    height = config_yml['height']
    assert width % 4 == 0
    assert height % 4 == 0
    framerate = config_yml['framerate']
    exposuretime = config_yml['exposuretime']
    if config_yml['exposuretime'] == 0: # special case for auto setting of exposure time
        pass # get max exposure time from C function
    pixelclock = config_yml['pixelclock']
    capture_lenght_minutes = config_yml['capture_lenght_minutes']

    return experiment_name, root_directory, width, height, framerate, exposuretime, pixelclock, capture_lenght_minutes

def check_and_prepare_directories(experiment_name, root_directory, create_empty_folder=False):
    experiment_directory = os.path.join(root_directory, experiment_name)
    if not os.path.isdir(root_directory):
        raise Exception(f'Wrong root directory path {root_directory}.')
    
    if create_empty_folder:
        if os.path.isdir(experiment_directory):
            raise Exception(f'Experiment {experiment_name} already exists.')    
        else:
            os.mkdir(experiment_directory)
            print(f'Created new directory {experiment_directory} for experiment {experiment_name}.')
    else:
        if not os.path.isdir(experiment_directory):
            raise Exception(f'Wrong experiment directory path {experiment_directory}.')