import numpy as np
from matplotlib import pyplot as plt 
import cv2
import os
from tqdm import tqdm
import functions

experiment_name, root_directory, p_width, p_height, fps, exposuretime, pixelclock, capture_lenght_minutes = functions.load_settings()
functions.check_and_prepare_directories(experiment_name, root_directory, create_empty_folder=False)

if __name__ == "__main__":
    cap = None
    try:
        cap = open(os.path.join(root_directory, experiment_name, f'{experiment_name}.mono'), 'rb')
    except IOError:
        print('Error opening video stream or file')
        exit(1)

    frame_count = os.stat(os.path.join(root_directory, experiment_name, f'{experiment_name}.mono')).st_size / (p_width*p_height)
    pbar = tqdm(total=frame_count, unit='ticks')

    i = 0
    out = open(os.path.join(root_directory, experiment_name, f'{experiment_name}_crop_128.mono'), 'wb')
    while(True):
        array = cap.read(p_width*p_height)

        if not array:
            print(f'Encoded: {i} frames')
            break

        array = array[p_width*64: p_width*(64+128)]
        i += 1
        pbar.update(1)
        out.write(array)
        
    pbar.close()
    cap.close()
    out.close()
    cv2.destroyAllWindows()