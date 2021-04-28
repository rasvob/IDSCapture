import yaml

def load_settings(confing_filename = 'config.yaml'):
    with open(confing_filename, 'r') as file:
        config_yml = yaml.safe_load(file)
    
    experiment_name = config_yml['experiment_name']
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

    return experiment_name, width, height, framerate, exposuretime, pixelclock, capture_lenght_minutes
