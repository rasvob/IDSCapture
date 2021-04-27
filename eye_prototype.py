from pyueye import ueye
import ctypes
import cv2
import numpy as np

p_width = 800
p_height = 256
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

ms = ueye.DOUBLE(2.328)
ret = ueye.is_Exposure(hCam, ueye.IS_EXPOSURE_CMD_SET_EXPOSURE, ms, ueye.sizeof(ms));
# print('EXP:',ret, ms)

clk_setter = ueye.c_uint(160)
nRet = ueye.is_PixelClock(hCam, ueye.IS_PIXELCLOCK_CMD_SET, clk_setter, 4)
if nRet != ueye.IS_SUCCESS:
    print("is_PixelClock SET ERROR")

fpsEye = ueye.c_double(400)
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


while(nRet == ueye.IS_SUCCESS):
    # In order to display the image in an OpenCV window we need to...
    # ...extract the data of our image memory
    array = ueye.get_data(pcImageMemory, width, height, nBitsPerPixel, pitch, copy=False)
    frame = np.reshape(array,(height.value, width.value, bytes_per_pixel))    
    cv2.imshow("Preview", frame)

    # Press q if you want to end the loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

ueye.is_FreeImageMem(hCam, pcImageMemory, MemID)
ueye.is_ExitCamera(hCam)