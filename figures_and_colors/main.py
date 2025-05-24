import numpy as np
import matplotlib.pyplot as plt
from skimage.morphology import label
from collections import defaultdict
from skimage.measure import regionprops


def truncate(values, decimals):
    factor = 10 ** decimals
    return np.floor(values * factor) / factor


image = plt.imread("balls_and_rects.png")

rounded_image = truncate(image, 1)

colors = np.unique(rounded_image.reshape(-1, rounded_image.shape[-1]), axis=0)

c = defaultdict(lambda: 0)
r = defaultdict(lambda: 0)

for i in colors[1:]:
    key = ", ".join([str(j) for j in i])
    mask = np.all(rounded_image == i, axis=-1)
    labeled = label(mask)
    regions = regionprops(labeled)

    for reg in regions:
        if reg.eccentricity == 0:
            c[key] += 1
        else:
            r[key] += 1

print("Circles:", "\n", dict(c))
print("Rectangles:", "\n", dict(r))
print(f"Total circles: {sum(c.values())}, total rectangles: {sum(r.values())}, total: {sum(c.values()) + sum(r.values())}")
print(f"Total colors: {len(colors)}")