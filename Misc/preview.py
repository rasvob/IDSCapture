import numpy as np
import cv2
from time import perf_counter, perf_counter_ns



cap = cv2.VideoCapture(1)

if not cap.isOpened():
    print("Camera is not connected")

ret, frame = cap.read()

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 256)
# # cap.set(cv2.CAP_PROP_FPS, 400)
# cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
# cap.set(cv2.CAP_PROP_EXPOSURE, -9)
# cap.set(cv2.CAP_PROP_XI_EXPOSURE, -9)


# print('cv2.CAP_PROP_FRAME_WIDTH :', cv2.CAP_PROP_FRAME_WIDTH)   # 3
# print('cv2.CAP_PROP_FRAME_HEIGHT:', cv2.CAP_PROP_FRAME_HEIGHT)  # 4
# print('cv2.CAP_PROP_FPS         :', cv2.CAP_PROP_FPS)           # 5
# print('cv2.CAP_PROP_FRAME_COUNT :', cv2.CAP_PROP_FRAME_COUNT)   # 7



print(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
print(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(cap.get(cv2.CAP_PROP_FPS))

print(cap.get(cv2.CAP_PROP_FRAME_COUNT))
print(cap.get(cv2.CAP_PROP_EXPOSURE))
print(cap.get(cv2.CAP_PROP_AUTO_EXPOSURE))
print(cap.get(cv2.CAP_PROP_XI_SENSOR_CLOCK_FREQ_HZ))

while(True):
    # Capture frame-by-frame

    start_time = perf_counter_ns()
    ret, frame = cap.read()

    if not ret:
        print("Frame was not read")
        continue

    # gray = cv2.cvtColor(frame, cv2.COLOR_GRAY2GRAY)

    stop_time = perf_counter_ns()
    diff_us = (stop_time - start_time)/1000
    print(f'Time difference: {diff_us}')

    # Display the resulting frame
    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()