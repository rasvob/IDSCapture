import numpy as np
from matplotlib import pyplot as plt 
import cv2

p_width = 800
p_height = 256
fps = 400
play = False



if __name__ == "__main__":
    cap = None
    try:
        cap = open(r'D:\\Hella\\10s.mono', 'rb')
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
        out = cv2.VideoWriter(r'D:\\Hella\\10s_enc.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 400, (p_width, p_height), False)
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