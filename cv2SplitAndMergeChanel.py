# -*- coding: UTF-8 -*-#
import cv2
import numpy as np

def mergeRGBA(imgR, imgG, imgB, imgA, imgRGBA):
    for i in [imgG,imgB,imgA,imgR]:
        if type(i) != int or type(i) != float:
            img = cv2.imread(i,cv2.IMREAD_UNCHANGED)
            break
        else:
            img = np.zeros([32,32,1],np.uint8)

    if type(imgG) != str and (type(imgG) == int or type(imgG) == float):
        g_chanel = (np.zeros([img.shape[0],img.shape[1],1],np.uint8)+imgG*255).astype('uint8')
    else:
        g_chanel = cv2.imread(imgG,cv2.IMREAD_UNCHANGED)

    if type(imgB) != str and (type(imgB) == int or type(imgB) == float):
        b_chanel = (np.zeros([img.shape[0],img.shape[1],1],np.uint8)+imgB*255).astype('uint8')
    else:
        b_chanel = cv2.imread(imgB,cv2.IMREAD_UNCHANGED)

    if type(imgR) != str and (type(imgR) == int or type(imgR) == float):
        r_chanel = (np.zeros([img.shape[0],img.shape[1],1],np.uint8)+imgR*255).astype('uint8')
    else:
        r_chanel = cv2.imread(imgR,cv2.IMREAD_UNCHANGED)
    if type(imgA) != str and (type(imgA) == int or type(imgA) == float):
        a_chanel = (np.zeros([img.shape[0],img.shape[1],1],np.uint8)+imgA*255).astype('uint8')
    else:
        a_chanel = cv2.imread(imgA,cv2.IMREAD_UNCHANGED)

    rgba_chanel = cv2.merge((b_chanel, g_chanel, r_chanel, a_chanel))
    cv2.imwrite(imgRGBA,rgba_chanel)


# def splitRGBA(imgRGBA, imgR, imgG, imgB,imgA):
#     img = cv2.imread(imgRGBA, cv2.IMREAD_UNCHANGED)
#     rgba_chanel = cv2.split(img)
#     b_chanel = rgba_chanel[0]
#     g_chanel = rgba_chanel[1]
#     r_chanel = rgba_chanel[2]
#     if img.shape[-1] == 3L:
#         chanelNum = 3
#         pass
#     else:
#         chanelNum = 4
#         a_chanel = rgba_chanel[3]
#         cv2.imwrite(imgA, a_chanel)
#     cv2.imwrite(imgR, r_chanel)
#     cv2.imwrite(imgG, g_chanel)
#     cv2.imwrite(imgB, b_chanel)

