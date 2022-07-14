import yaml
import os

def float_representer(dumper, value):
    text = '{0:.3f}'.format(value)
    return dumper.represent_scalar(u'tag:yaml.org,2002:float', text)

def load_settings(config_filename = 'config.yaml'):
    with open(config_filename, 'r') as file:
        config_yml = yaml.safe_load(file)
    
    experiment_name = config_yml['experiment_name']
    root_directory = config_yml['root_directory']
    width = config_yml['width']
    height = config_yml['height']
    assert width % 4 == 0
    assert height % 4 == 0
    framerate = config_yml['framerate']
    exposuretime = config_yml['exposuretime']
    pixelclock = config_yml['pixelclock']
    capture_lenght_minutes = config_yml['capture_lenght_minutes']
    hardware_gain = config_yml['hardware_gain']
    hardware_gamma = config_yml['hardware_gamma']

    return experiment_name, root_directory, width, height, framerate, exposuretime, pixelclock, capture_lenght_minutes, hardware_gain, hardware_gamma

def load_settings_calibration(config_filename = 'config.yaml'):
    experiment_name, root_directory, width, height, framerate, exposuretime, pixelclock, capture_lenght_minutes, hardware_gain, hardware_gamma = load_settings()

    with open(config_filename, 'r') as file:
        config_yml = yaml.safe_load(file)

    sqr_size_mm = config_yml['sqr_size_mm']
    chessboard_rows = config_yml['chessboard_rows']
    chessboard_cols = config_yml['chessboard_cols']

    return experiment_name, root_directory, width, height, framerate, exposuretime, pixelclock, capture_lenght_minutes, sqr_size_mm, chessboard_rows, chessboard_cols, hardware_gain, hardware_gamma

def load_ratio(config_filename = 'config.yaml'):
    with open(config_filename, 'r') as file:
        config_yml = yaml.safe_load(file)

    return config_yml['pixel_to_mm_ratio']

def save_ratio(ratio, config_filename = 'config.yaml'):
    with open(config_filename, 'r') as file:
        config_yml = yaml.safe_load(file)

    config_yml['pixel_to_mm_ratio'] = ratio

    with open(config_filename, 'w') as file:
        yaml.dump(config_yml, file)

def copy_config_file(config_filename = 'config.yaml'):
    experiment_name, root_directory, width, height, framerate, exposuretime, pixelclock, capture_lenght_minutes, hardware_gain, hardware_gamma = load_settings(config_filename)
    dest_conf_filename = os.path.join(root_directory, experiment_name, 'backuped_config.yaml')    
    os.system(f'copy {config_filename} {dest_conf_filename}')    


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