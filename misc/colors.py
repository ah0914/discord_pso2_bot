import cv2
import numpy as np
import random

def pcolor():
    height= 100
    width = 100

    r = random.randint(0,255)
    g = random.randint(0,255)
    b = random.randint(0,255)

    blank = np.zeros((height, width, 3))
    blank += [r,g,b][::-1]

    cv2.imwrite('color.png',blank)
