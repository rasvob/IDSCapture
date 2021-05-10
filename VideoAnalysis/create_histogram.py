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
    end = 400*10
    first = True
    free_run = True
    histogram_values = np.zeros(256)
    while(cap.isOpened()):
        ret, frame = cap.read()
        # key = cv2.waitKey(0)
        key = None
        if key == ord('c') or first or free_run:
            if ret:
                first = False
                i += 1
                pbar.update()
                if i > end:
                    break
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
                rv = frame.ravel()
                for x in rv:
                    histogram_values[x] += 1
        elif key == ord('q'):
            break
    
    plt.bar(x=np.arange(0, 256), height=histogram_values)
    plt.show()
    cap.release()
    cv2.destroyAllWindows()