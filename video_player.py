import numpy as np
from matplotlib import pyplot as plt 
import cv2

def pixelVal(pix, r1, s1, r2, s2): 
    if (0 <= pix and pix <= r1): 
        return (s1 / r1)*pix 
    elif (r1 < pix and pix <= r2): 
        return ((s2 - s1)/(r2 - r1)) * (pix - r1) + s1 
    else: 
        return ((255 - s2)/(255 - r2)) * (pix - r2) + s2 

if __name__ == "__main__":
    cap = cv2.VideoCapture(r'D:\\Hella\\10s.mp4')
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
    while(cap.isOpened()):
        # Capture frame-by-frame
        key = cv2.waitKey(0)
        if key == ord('c') or first:
            ret, frame = cap.read()

            if ret == True:
                i += 1
                print(i)
                cv2.imshow('Frame', frame)
                first = False
        elif key == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()