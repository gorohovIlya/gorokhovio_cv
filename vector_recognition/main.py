import matplotlib.pyplot as plt
import numpy as np
from skimage.measure import label, regionprops

def count_holes(region):
    shape = region.image.shape
    new_image = np.zeros((shape[0] + 2, shape[1] + 2))
    new_image[1:-1, 1:-1] = region.image
    new_image = np.logical_not(new_image)
    labeled = label(new_image)
    return np.max(labeled) - 1


def extractor(region):
    image = region.image
    area = region.area / image.size
    cy, cx = region.centroid_local
    cy /= image.shape[0]
    cx /= image.shape[1]
    perimeter = region.perimeter / image.size
    eccentricity = region.eccentricity
    vlines = (np.sum(image, 0) == image.shape[0])
    vlines = np.sum(vlines)
    hlines = (np.sum(image, 1) == image.shape[1])
    hlines = np.sum(hlines)
    aspect_ratio = image.shape[0] / image.shape[1]
    holes = count_holes(region)
    compactness = (perimeter ** 2) / (4 * np.pi * area) if area > 0 else 0

    return np.array([
        area,
        cy,
        cx,
        perimeter,
        eccentricity,
        vlines,
        hlines,
        aspect_ratio,
        holes,
        compactness
    ])


def norm_l1(v1, v2):
    return ((v1 - v2) ** 2).sum() ** 0.5


def classificator(v, templates):
    result = "_"
    min_dist = 10 ** 10
    for key in templates:
        d = norm_l1(v, templates[key])
        if d < min_dist:
            result = key
            min_dist = d
    return result

image = plt.imread("alphabet-small.png")
gray = image.mean(axis=2)
binary = gray < 1
labeled = label(binary)
regions = regionprops(labeled)

temps = {
    "A": extractor(regions[2]),
    "B": extractor(regions[3]),
    "8": extractor(regions[0]),
    "0": extractor(regions[1]),
    "1": extractor(regions[4]),
    "W": extractor(regions[5]),
    "X": extractor(regions[6]),
    "*": extractor(regions[7]),
    "-": extractor(regions[9]),
    "/": extractor(regions[8])
}

symbols = plt.imread("alphabet.png")[:, :, :-1]
gray = symbols.mean(axis=2)
binary = gray > 0
labeled = label(binary)
regions_to_test = regionprops(labeled)

plt.figure(figsize=(15, 10))
for i, reg in enumerate(regions_to_test):
    if i >= 15:
        break
    v = extractor(reg)
    plt.subplot(3, 5, i + 1)
    plt.title(classificator(v, temps))
    plt.imshow(reg.image)
plt.tight_layout()
plt.show()