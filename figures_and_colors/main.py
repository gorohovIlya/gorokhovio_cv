import numpy as np
import matplotlib.pyplot as plt
from skimage.morphology import label
from collections import defaultdict
from skimage.measure import regionprops
image = plt.imread("balls_and_rects.png")
colors = np.unique(image.reshape(-1, image.shape[-1]), axis=0)
c = defaultdict(lambda: 0)
r = defaultdict(lambda: 0)
t_image = image.copy()
for i in colors[1:]:
    key = ", ".join([str(j) for j in i])
    mask = np.all(t_image == i,axis=-1)
    labeled = label(mask)
    regions = regionprops(labeled)
    for reg in regions:
        if reg.eccentricity == 0:
            c[key] += 1
        else:
            r[key] += 1
print("Circles:", "\n", c)
c_sum = sum(c.values())
print("Rectangles:", "\n", r)
r_sum = sum(r.values())
print(f"Total circles: {c_sum}, total rectangles: {r_sum}, total: {c_sum+r_sum}")
