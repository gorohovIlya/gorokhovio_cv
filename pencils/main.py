import numpy as np
from skimage.measure import regionprops
import cv2
from skimage.morphology import label

lower = np.array([5,120,110])
upper = np.array([120,260,220])

cnt = 0

for i in range(1, 13):
    img = cv2.imread(f"images/img ({i}).jpg")
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, lower, upper)
    mask = cv2.dilate(mask, np.ones((9,9)))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((9,9)), iterations=3)

    labeled = label(mask)
    regions = regionprops(labeled)

    pencils = [reg for reg in regions if (reg.area > 85000 and 1 - reg.eccentricity < 0.02)]
    quantity = len(pencils)
    cnt += quantity
    print(f"Image {i} Pencils:", quantity)

print("Total pencils in the pictures:", cnt)