import numpy as np
from matplotlib import pyplot as plt 
import cv2
from tqdm import tqdm

if __name__ == "__main__":
    input_file = r'C:\Users\svo0175\Documents\Work\Svetlomet\Hella_06_05_2021\Hrabova_test_long_spatne_svetlo\Hrabova_test_long_spatne_svetlo.mp4'
    output_file = r'C:\Users\svo0175\Documents\Work\Svetlomet\Hella_06_05_2021\Hrabova_test_long_spatne_svetlo\Hrabova_test_long_spatne_svetlo_cut.mp4'
    input_time_csv = r'C:\Users\svo0175\Documents\Work\Svetlomet\Hella_06_05_2021\Hrabova_test_long_spatne_svetlo\timestamps.txt'
    output_time_csv = r'C:\Users\svo0175\Documents\Work\Svetlomet\Hella_06_05_2021\Hrabova_test_long_spatne_svetlo\timestamps_cut.txt'

    cap = cv2.VideoCapture(input_file)
    if (cap.isOpened() == False): 
        print("Error opening video stream or file")
        exit(1)

    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps    = cap.get(cv2.CAP_PROP_FPS)
    print(f"Lenth: {length}, Width: {width}, Height: {height}, Fps: {fps}")

    


    out = cv2.VideoWriter(output_file, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height), False)
    i = 0
    start, end = 316, 258454

    with open(input_time_csv, 'r') as in_file:
        times = in_file.readlines()
        times = times[start:end+1]
        with open(output_time_csv, 'w') as out_file:
            out_file.write(''.join(times))

    pbar = tqdm(total=length, unit='ticks')
    while(cap.isOpened()):
        ret, frame = cap.read()

        if ret:
            i += 1ě
            pbar.update()
            if i >= start and i <= end:
                out.write(frame[:, :, 0])
            elif i > end:
                break

    out.release()
    cap.release()