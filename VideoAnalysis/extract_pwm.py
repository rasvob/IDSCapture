import numpy as np
import pandas as pd
from matplotlib import pyplot as plt 
import cv2
from tqdm import tqdm

if __name__ == "__main__":
    order = 7

    input_file = f'D:\Hella\HARD\VSB_Hard_9_8_Mereni0{order}.avi'
    output_file = f'D:\Hella\HARD\VSB_Hard_9_8_Mereni0{order}.csv'

    cap = cv2.VideoCapture(input_file)
    if (cap.isOpened() == False): 
        print("Error opening video stream or file")
        exit(1)

    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps    = cap.get(cv2.CAP_PROP_FPS)
    print(f"Lenth: {length}, Width: {width}, Height: {height}, Fps: {fps}")

    i = 0
    pbar = tqdm(total=length, unit='ticks')
    end = length
    first = True
    free_run = True
    frame_sum = np.zeros(length, dtype=np.int32)
    frame_avg = np.zeros(length, dtype=np.int32)

    while(cap.isOpened()):
        ret, frame = cap.read()
        key = cv2.waitKey(0)
        if key == ord('c') or first or free_run:
            if ret:
                first = False
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
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
                ret, frame = cap.read()
                if ret:
                    i += 1
                    pbar.update()
                else:
                    break
        elif key == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    pbar.close()

    print('Extraction done')

    if free_run:
        print('Save starting')
        df = pd.DataFrame({'FrameSum': frame_sum, 'FrameAvg': frame_avg})
        df.to_csv(output_file, ';')