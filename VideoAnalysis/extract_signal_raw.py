import numpy as np
import pandas as pd
from matplotlib import pyplot as plt 
import cv2
from tqdm import tqdm
from time import perf_counter, perf_counter_ns
import functions
import os

experiment_name, root_directory, p_width, p_height, fps, exposuretime, pixelclock, capture_lenght_minutes = functions.load_settings()
functions.check_and_prepare_directories(experiment_name, root_directory, create_empty_folder=False)

threshold = 55
free_run = True

def ns_to_us(start, end):
    return (end - start) /  1000

if __name__ == "__main__":
    input_file = os.path.join(root_directory, experiment_name, f'{experiment_name}.mono')
    input_file_ts = os.path.join(root_directory, experiment_name, 'timestamps.txt')
    output_file = os.path.join(root_directory, experiment_name, f'{experiment_name}.') + '{0}'

    cap = open(input_file, 'rb')
    if (not cap): 
        print("Error opening video stream or file")
        exit(1)

    length = os.stat(input_file).st_size // (p_width*p_height)
    print(f"Lenth: {length}, Width: {p_width}, Height: {p_height}, Fps: {fps}")

    i = 0
    pbar = tqdm(total=length, unit='ticks')
    end = length
    first = True
    signal = np.zeros(length)
    process_time_arr = np.zeros(length)
    read_time_arr = np.zeros(length)

    while(True):
        start_time = perf_counter_ns()
        array = cap.read(p_width*p_height)
        end_time = perf_counter_ns()
        read_time_arr[i] = ns_to_us(start_time, end_time)

        key = cv2.waitKey(0)
        if key == ord('c') or first or free_run:
            if array:
                first = False
                start_time = perf_counter_ns()
                array = np.frombuffer(array, dtype=np.uint8)
                frame = np.reshape(array, (p_height, p_width))
                avg_for_line = int(np.mean(np.argmax((frame > threshold), axis=1)))
                signal[i] = avg_for_line
                end_time = perf_counter_ns()
                process_time_arr[i] = ns_to_us(start_time, end_time)
                
                if not free_run:
                    frame = np.reshape(array, (p_height, p_width, 1))
                    ret, thresh_bin = cv2.threshold(frame, threshold, 255, cv2.THRESH_BINARY)
                    frame_b_color = cv2.cvtColor(thresh_bin, cv2.COLOR_GRAY2RGB)
                    image_b = cv2.line(frame_b_color, (int(avg_for_line), 0), (int(avg_for_line), p_height-1), (0, 0, 255), 2)
                    cv2.imshow(f'Frame - bin', image_b)
                    cv2.imshow('Frame - orig', frame)

                i += 1
                pbar.update()
                
                if i >= end:
                    break
            else:
                break
        elif key == ord('s'):
            for x in range(0, 400):
                ret = cap.read(p_width*p_height)
                if ret:
                    i += 1
                    pbar.update()
                else:
                    break
        elif key == ord('q'):
            break
    
    cap.close()
    cv2.destroyAllWindows()
    pbar.close()

    print('Extraction done')
    print(f'Total s: {np.sum(process_time_arr)/1000000}, avg us: {np.mean(process_time_arr)}, std us: {np.std(process_time_arr)}, max us: {np.max(process_time_arr)}')
    print('Read stats')
    print(f'Total s: {np.sum(read_time_arr)/1000000}, avg us: {np.mean(read_time_arr)}, std us: {np.std(read_time_arr)}, max us: {np.max(read_time_arr)}')

    if free_run:
        print('Save starting')
        ps_ts = pd.Series(pd.read_csv(input_file_ts, header=None).iloc[:, 0])
        df = pd.DataFrame(signal, columns=['Edge_Avg'])
        df['FrameTimestamp_us'] = ps_ts
        df.to_parquet(output_file.format('parquet.gzip'), compression='gzip', engine='pyarrow', )