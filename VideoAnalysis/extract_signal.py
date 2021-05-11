import numpy as np
import pandas as pd
from matplotlib import pyplot as plt 
import cv2
from tqdm import tqdm

if __name__ == "__main__":
    input_file = r'C:\Users\svo0175\Documents\Work\Svetlomet\Hella_06_05_2021\Hrabova_test_long_nove_svetlo\Hrabova_test_long_nove_svetlo_cut.mp4'
    input_file_ts = r'C:\Users\svo0175\Documents\Work\Svetlomet\Hella_06_05_2021\Hrabova_test_long_nove_svetlo\timestamps_cut.txt'
    output_file = r'C:\Users\svo0175\Documents\Work\Svetlomet\Hella_06_05_2021\Hrabova_test_long_nove_svetlo\Hrabova_test_long_nove_svetlo_cut_{0}.{1}'

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
    thresholds_arr = [10, 50, 100, 115]
    out_arrs = {}
    for t in thresholds_arr:
        out_arrs[t] = np.zeros((length, height))

    while(cap.isOpened()):
        ret, frame = cap.read()
        key = cv2.waitKey(0)
        if key == ord('c') or first or free_run:
            if ret:
                first = False
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
                thresholds_frames = []
                
                for x in thresholds_arr:
                    ret, thresh_bin = cv2.threshold(frame, x, 255, cv2.THRESH_BINARY)
                    thresholds_frames.append(thresh_bin)
                    out_arrs[x][i, :] = np.argmax(thresh_bin, axis=1)
                
                if not free_run:
                    for i, frame in enumerate(thresholds_frames):
                        cv2.imshow(f'Frame - bin {thresholds_arr[i]}', frame)
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
    print('Save starting')

    pbar = tqdm(total=len(out_arrs), unit='ticks')
    ps_ts = pd.Series(pd.read_csv(input_file_ts, header=None).iloc[:, 0])
    for k,v in out_arrs.items():
        df = pd.DataFrame(v, columns=[f'Row_{x}' for x in range(height)])
        df['FrameTimestamp_us'] = ps_ts
        df.to_parquet(output_file.format(k, 'parquet.gzip'), compression='gzip', engine='pyarrow')
        pbar.update()
    pbar.close()