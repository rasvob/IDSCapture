import numpy as np
from matplotlib import pyplot as plt 
import cv2
from tqdm import tqdm

def pixelVal(pix, r1, s1, r2, s2): 
    if (0 <= pix and pix <= r1): 
        return (s1 / r1)*pix 
    elif (r1 < pix and pix <= r2): 
        return ((s2 - s1)/(r2 - r1)) * (pix - r1) + s1 
    else: 
        return ((255 - s2)/(255 - r2)) * (pix - r2) + s2 

if __name__ == "__main__":
    cap = cv2.VideoCapture(r'C:\Users\svo0175\Documents\Work\Svetlomet\Hella_06_05_2021\Hrabova_test_long_spatne_svetlo\Hrabova_test_long_spatne_svetlo.mp4')
    if (cap.isOpened() == False): 
        print("Error opening video stream or file")
        exit(1)

    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps    = cap.get(cv2.CAP_PROP_FPS)
    print(f"Lenth: {length}, Width: {width}, Height: {height}, Fps: {fps}")

    first = True
    i = 0
    # while(cap.isOpened()):
    #     # Capture frame-by-frame
    #     key = cv2.waitKey(0)
    #     if key == ord('c') or first:
    #         ret, frame = cap.read()

    #         if ret == True:
    #             i += 1
    #             cv2.imshow('Frame', frame)
    #             first = False
    #     elif key == ord('s'):
    #         for x in range(0, 400):
    #             ret, frame = cap.read()
    #             if ret:
    #                 i += 1
    #                 cv2.imshow('Frame', frame)
    #             else:
    #                 break
    #     elif key == ord('f'):
    #         print(i)
    #     elif key == ord('q'):
    #         break

    found_start, found_end = False, False
    pbar = tqdm(total=length, unit='ticks')
    while(cap.isOpened()):
        ret, frame = cap.read()

        if ret:
            i += 1
            pbar.update()
            if frame[0, 0, 0] < 10 and not found_start:
                print(i)
                found_start = True
            elif frame[0, 0, 0] > 50 and not found_end and found_start:
                print(i)
                found_end = True

    cap.release()
    cv2.destroyAllWindows()