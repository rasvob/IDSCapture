import numpy as np
from matplotlib import pyplot as plt 
import cv2
from numpy.lib.histograms import histogram
from tqdm import tqdm

if __name__ == "__main__":
    input_file = r'C:\Users\svo0175\Documents\Work\Svetlomet\Hella_06_05_2021\Hrabova_test_long_nove_svetlo\Hrabova_test_long_nove_svetlo_cut.mp4'
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
    free_run = False
    while(cap.isOpened()):
        ret, frame = cap.read()
        key = cv2.waitKey(0)
        key = None
        if key == ord('c') or first or free_run:
            if ret:
                first = False
                i += 1
                pbar.update()
                if i > end:
                    break
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
                ret, thresh_bin = cv2.threshold(frame, 50, 255, cv2.THRESH_BINARY)
                cv2.imshow('Frame - bin', thresh_bin)
        elif key == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()