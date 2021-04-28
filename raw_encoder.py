import numpy as np
from matplotlib import pyplot as plt 
import cv2
import os
import functions

experiment_name, root_directory, p_width, p_height, fps, exposuretime, pixelclock, capture_lenght_minutes = functions.load_settings()
functions.check_and_prepare_directories(experiment_name, root_directory, create_empty_folder=True)
play = False


if __name__ == "__main__":
    cap = None
    try:
        cap = open(os.path.join(root_directory, experiment_name, f'{experiment_name}.mono'), 'rb')
    except IOError:
        print('Error opening video stream or file')
        exit(1)

    if play:
        first = True
        i = 0
        while(True):
            key = cv2.waitKey(0)
            if key == ord('c') or first:
                array = cap.read(p_width*p_height)
                if array:
                    array = np.frombuffer(array, dtype=np.uint8)
                    frame = np.reshape(array,(p_height, p_width, 1))
                    i += 1
                    print(i)
                    cv2.imshow('Frame', frame)
                    first = False
            elif key == ord('q'):
                break

    else:
        i = 0
        out = cv2.VideoWriter(os.path.join(root_directory, experiment_name, f'{experiment_name}_enc.mono'), cv2.VideoWriter_fourcc(*'mp4v'), 400, (p_width, p_height), False)
        while(True):
            array = cap.read(p_width*p_height)

            if not array:
                print(f'Encoded: {i} frames')
                break

            array = np.frombuffer(array, dtype=np.uint8)
            frame = np.reshape(array,(p_height, p_width, 1))

            i += 1
            out.write(frame[:,:,0])
            if i % 400 == 0:
                print(i)
            
        out.release()

    cap.close()
    cv2.destroyAllWindows()