import ctypes
import enum
import cv2
import numpy as np
from time import perf_counter, perf_counter_ns
from pyueye import ueye
from queue import Queue
from threading import Thread, Lock
import functions
from checkerboard import detect_checkerboard


def ns_sleep(duration, get_now=perf_counter_ns):
    now = get_now()
    end = now + duration
    while now < end:
        now = get_now()

def compute_distances(points, cb_size):
    num_x_points = cb_size[0]
    num_y_points = cb_size[1]

    x_distances = list()
    for y_coord in range(num_y_points):
        points_index = y_coord * num_x_points
        for point_1, point_2 in zip(points[points_index:points_index+num_x_points-1], points[points_index+1:points_index+num_x_points]):
            x_distance = abs(point_1[0][0] - point_2[0][0])
            x_distances.append(x_distance)

    y_distances = list()
    for x_coord in range(num_x_points):
        for row_index in range(0, num_y_points-1):
            index1 = x_coord + row_index * num_x_points
            index2 = x_coord + (row_index+1) * num_x_points
            point_1 = points[index1]
            point_2 = points[index2]
            y_distance = abs(point_1[0][1] - point_2[0][1])
            y_distances.append(y_distance)

    point_1 = points[0][0]
    point_2 = points[num_x_points-1][0]
    x_distance = abs(point_1[0] - point_2[0])
    y_distance = abs(point_1[1] - point_2[1])
    
    v_angle = np.degrees(np.arctan(y_distance/x_distance))
    return x_distances, y_distances, v_angle

def overlay_frame(orig_frame, alpha=0.2, overlay_width=100):
    frame = cv2.cvtColor(orig_frame, cv2.COLOR_GRAY2RGB)
    overlay = np.zeros_like(frame, np.uint8)
    h, w = frame.shape[0], frame.shape[1]
    cv2.rectangle(overlay, (w - overlay_width, 0), (w - 1, h - 1), (0, 200, 0), cv2.FILLED)        
    frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
    return frame

experiment_name, root_directory, p_width, p_height, framerate, exposuretime, pixelclock, capture_lenght_minutes, sqr_size_mm, chessboard_rows, chessboard_cols = functions.load_settings_calibration()
p_height = 300


nBitsPerPixel = ueye.INT(8)
bytes_per_pixel = 1
pitch = ueye.INT()

rectAOI = ueye.IS_RECT()
rectAOI.s32X = ueye.int(0)
rectAOI.s32Y = ueye.int(0)
rectAOI.s32Width = ueye.int(p_width)
rectAOI.s32Height = ueye.int(p_height)

width = rectAOI.s32Width
height = rectAOI.s32Height

hCam = ueye.HIDS(0)
ret = ueye.is_InitCamera(hCam, None)

if ret != ueye.IS_SUCCESS:
    print('ERR Camera access')

nRet = ueye.is_AOI(hCam, ueye.IS_AOI_IMAGE_SET_AOI, rectAOI, ueye.sizeof(rectAOI))

ms = ueye.DOUBLE(exposuretime)
ret = ueye.is_Exposure(hCam, ueye.IS_EXPOSURE_CMD_SET_EXPOSURE, ms, ueye.sizeof(ms));

clk_setter = ueye.c_uint(pixelclock)
nRet = ueye.is_PixelClock(hCam, ueye.IS_PIXELCLOCK_CMD_SET, clk_setter, 4)
if nRet != ueye.IS_SUCCESS:
    print("is_PixelClock SET ERROR")

fpsEye = ueye.c_double(framerate)
fpsNewEye = ueye.c_double()
nRet = ueye.is_SetFrameRate(hCam, fpsEye, fpsNewEye)
if nRet != ueye.IS_SUCCESS:
    print("is_SetFrameRate ERROR")


rectAOIget = ueye.IS_RECT()
nRet = ueye.is_AOI(hCam, ueye.IS_AOI_IMAGE_GET_AOI, rectAOIget, ueye.sizeof(rectAOI))
if nRet != ueye.IS_SUCCESS:
    print("is_AOI ERROR")

print("Maximum image width:\t", rectAOIget.s32Width)
print("Maximum image height:\t", rectAOIget.s32Height)


msG = ueye.DOUBLE(0)
ret = ueye.is_Exposure(hCam, ueye.IS_EXPOSURE_CMD_GET_EXPOSURE, msG, ueye.sizeof(msG));
print('EXP:',ret, msG)

PCrange = (ctypes.c_uint * 3)()
ret = ueye.is_PixelClock(hCam, ueye.IS_PIXELCLOCK_CMD_GET_RANGE, PCrange, 3*ueye.sizeof(ueye.UINT()))
print('PxCLK range:', ret, PCrange[0], PCrange[1], PCrange[2])

clk = ueye.UINT()
nRet = ueye.is_PixelClock(hCam, ueye.IS_PIXELCLOCK_CMD_GET, clk, ueye.sizeof(clk))
if nRet != ueye.IS_SUCCESS:
    print("is_PixelClock GET ERROR")
print("PixelClock:\t", nRet, clk)

print("is_SetFrameRate:\t", nRet, fpsNewEye)

pcImageMemory = ueye.c_mem_p()
MemID = ueye.int()

nRet = ueye.is_AllocImageMem(hCam, width, height, nBitsPerPixel, pcImageMemory, MemID)
if nRet != ueye.IS_SUCCESS:
    print("is_AllocImageMem ERROR")

nRet = ueye.is_SetImageMem(hCam, pcImageMemory, MemID)
if nRet != ueye.IS_SUCCESS:
    print("is_SetImageMem ERROR")

m_nColorMode = ueye.IS_CM_MONO8
nRet = ueye.is_SetColorMode(hCam, m_nColorMode)
if nRet != ueye.IS_SUCCESS:
    print("is_SetColorMode ERROR")

nRet = ueye.is_CaptureVideo(hCam, ueye.IS_DONT_WAIT)
if nRet != ueye.IS_SUCCESS:
    print("is_CaptureVideo ERROR")

nRet = ueye.is_InquireImageMem(hCam, pcImageMemory, MemID, width, height, nBitsPerPixel, pitch)
if nRet != ueye.IS_SUCCESS:
    print("is_InquireImageMem ERROR")

frame_counter = 0
max_frames_cnt = framerate*60*120
diff_arr = np.zeros(max_frames_cnt)
timestamp_arr = np.zeros(max_frames_cnt)
frame_delay = 1000000000 // 25

cb_size = (chessboard_cols - 1, chessboard_rows - 1)

while(nRet == ueye.IS_SUCCESS):
    start_time = perf_counter_ns()
    array = ueye.get_data(pcImageMemory, width, height, nBitsPerPixel, pitch, copy=False)
    timestamp_arr[frame_counter] = perf_counter_ns()/1000
    frame = np.reshape(array,(height.value, width.value, bytes_per_pixel))
    stop_time = perf_counter_ns()
    diff_us = (stop_time - start_time)/1000
    diff_ns = (stop_time - start_time)
    wait_time = frame_delay - diff_ns
    ns_sleep(wait_time)
    stop_time = perf_counter_ns()
    diff_us = (stop_time - start_time)/1000
    diff_arr[frame_counter] = diff_us
    frame_counter += 1

    frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    ret, corners = cv2.findChessboardCorners(frame, cb_size, flags=cv2.CALIB_CB_FAST_CHECK)
    frame = overlay_frame(frame)

    if ret:
        for k, v in enumerate(corners):
            v = v[0]
            frame = cv2.circle(frame, (v[0], v[1]), radius=2, color=(255, 0, 255), thickness=1)
            cv2.putText(frame, str(k), (int(v[0]) + 10, int(v[1]) + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 0, 255), 1)

        x_distances, y_distances, v_angle = compute_distances(corners, cb_size)
        y_ratio = sqr_size_mm / np.mean(y_distances)

        cv2.putText(frame, f'X: {"{:.2f}".format(np.mean(x_distances))} +- {"{:.3f}".format(np.std(x_distances))} px', (5, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)
        cv2.putText(frame, f'Y: {"{:.2f}".format(np.mean(y_distances))} +- {"{:.3f}".format(np.std(y_distances))} px', (5, 38), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)
        cv2.putText(frame, f'V-Angle: {"{:.2f}".format(v_angle)} deg', (5, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)
        cv2.putText(frame, f'Y-ratio: 1 px ~ {"{:.2f}".format(y_ratio)} mm', (5, 82), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)

    cv2.imshow("Preview", frame)

    key = cv2.waitKey(1)
    # Press q if you want to end the loop
    if key == ord('q'):
        break
    elif key == ord('s'):
        print(f'Save ratio - {float(round(y_ratio, 2))}')
        functions.save_ratio(float(round(y_ratio, 2)))


print(f'Avg: {np.mean(diff_arr)}, Std: {np.std(diff_arr)}, Min: {np.min(diff_arr)}, Max: {np.max(diff_arr)}')
ueye.is_FreeImageMem(hCam, pcImageMemory, MemID)
ueye.is_ExitCamera(hCam)