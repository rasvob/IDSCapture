import numpy as np
from numpy.core.numerictypes import obj2sctype
import pandas as pd
from matplotlib import pyplot as plt 
import cv2
from tqdm import tqdm
import os
import functions

def ns_to_us(start, end):
    return (end - start) /  1000

experiment_name, root_directory, p_width, p_height, fps, exposuretime, pixelclock, capture_lenght_minutes = functions.load_settings()
functions.check_and_prepare_directories(experiment_name, root_directory, create_empty_folder=False)

if __name__ == "__main__":
    order = 9

    input_file = f'D:\Hella\Hella_Cervenec_Mereni_Audi_PWM\Hella_Cervenec_Mereni_Audi_PWM.mono'
    output_file = f'D:\Hella\Hella_Cervenec_Mereni_Audi_PWM\Hella_Cervenec_Mereni_Audi_PWM.csv'

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
    free_run = True
    frame_sum = np.zeros(length, dtype=np.int32)
    frame_avg = np.zeros(length, dtype=np.int32)

    while(True):
        array = cap.read(p_width*p_height)
        key = cv2.waitKey(0)
        if key == ord('c') or first or free_run:
            if array:
                first = False
                array = np.frombuffer(array, dtype=np.uint8)
                frame = np.reshape(array, (p_height, p_width))
                frame_sum[i] = np.sum(frame)
                frame_avg[i] = np.sum(frame)/(frame.shape[0] * frame.shape[1])

                if not free_run:
                    cv2.putText(frame, str(frame_sum[i]), (15, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 0, 255), 1)
                    cv2.putText(frame, str(int(frame_sum[i]/(frame.shape[0] * frame.shape[1]))), (15, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 0, 255), 1)
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

    if free_run:
        print('Save starting')
        df = pd.DataFrame({'FrameSum': frame_sum, 'FrameAvg': frame_avg})
        df.to_csv(output_file, ';')