#-*- coding: UTF-8 -*-#
import cv2
import numpy as np
import maya.cmds as cmds
def mergeImageOpacity(img, imgOpacity, imgFormat):
    imgPath = img.split(".")[0]
    img = cv2.imread(img)
    imgOpacity = cv2.imread(imgOpacity, 0)
    b_chanel,g_chanel,r_chanel = cv2.split(img)
    alpha_chanel = cv2.split(imgOpacity)[0]
    img = cv2.merge((b_chanel,g_chanel,r_chanel,alpha_chanel))
    cv2.imwrite(imgPath+'.'+ imgFormat,img)

# imgPath = r"E:\WORK\PycharmProjects\ErBaDao_Tool_Maya\images\xxx.jpg"
#imgFormat = 'jpg'or 'png' or 'exr'...
#支持的格式有 exr,hdr,pbm,pxm,pam,jpg,png,webp
def ConverterFormat(imgPath,imgFormat):
    img = cv2.imread(imgPath,cv2.IMREAD_UNCHANGED)
    if  imgFormat == 'exr' or imgFormat == 'hdr':
        imgZeroDeph = np.float32
    elif '16' in imgFormat:
        imgZeroDeph = np.uint16
    else:
        imgZeroDeph = np.uint8

    if img.dtype == 'float32':
        if imgZeroDeph == np.float32:
            imgZero = img
        elif imgZeroDeph == np.uint16:
            imgZero = np.clip((img * 65535),0,65535).astype(np.uint16)
        elif imgZeroDeph == np.uint8:
            imgZero = np.clip((img * 255),0,255).astype(np.uint8)
        else:
            print imgPath + '：的通道异常，请手动处理'
            pass
    if img.dtype == 'uint16':
        if imgZeroDeph == np.float32:
            imgZero = np.clip((img*1.0/65535),0,1).astype(np.float32)
        elif imgZeroDeph == np.uint16:
            imgZero = img
        elif imgZeroDeph == np.uint8:
            imgZero = np.clip((img / 255), 0, 255).astype(np.uint8)
        else:
            cmds.warning( imgPath + '：的通道异常，请手动处理')
            pass
    if img.dtype == 'uint8':
        if imgZeroDeph == np.float32:
            imgZero = (np.clip((img*1.0/255),0,1)**2.2).astype(np.float32)
        elif imgZeroDeph == np.uint16:
            imgZero = img.astype(np.uint16) * 255
        elif imgZeroDeph == np.uint8:
            imgZero = img
        else:
            cmds.warning( imgPath + '：的通道异常，请手动处理')
            pass
    #判断用户输入的是16位图吗
    if '16' in imgFormat:
        imgZeroFormat = imgFormat[0:-2]
    else:
        imgZeroFormat = imgFormat

    imgFile =  imgPath[:len(imgPath.split(".")[-1])*(-1)]+imgZeroFormat
    cv2.imwrite(imgFile,imgZero)
