from pyueye import ueye
import ctypes

rectAOI = ueye.IS_RECT()
rectAOI.s32X = ueye.int(0)
rectAOI.s32Y = ueye.int(0)
rectAOI.s32Width = ueye.int(800)
rectAOI.s32Height = ueye.int(250)

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
