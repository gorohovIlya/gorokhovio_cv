from operator import truediv

import numpy as np
import matplotlib.pyplot as plt

external = np.array([
    [[0, 0], [0, 1]],
    [[0, 0], [1, 0]],
    [[0, 1], [0, 0]],
    [[1, 0], [0, 0]]
])

internal = np.logical_not(external)

collide = np.array([
    [[0, 1],[1, 0]],
    [[1, 0], [0, 1]]
])

# np.diag([1, 1, 1, 1]).reshape(4, 2, 2)

def match(sub, masks):
    for mask in masks:
        if np.all(sub == mask):
            return True
    return False


def count_object(image):
    E = 0
    I = 0
    C = 0
    for y in range(0, image.shape[0]-1):
        for x in range(1, image.shape[1]-1):
            sub = image[y:y+2, x:x+2]
            if match(sub, external):
                E += 1
            elif match(sub, internal):
                I += 1
            elif match(sub, collide):
                C += 1
    return (E - I) / 4 + (C / 2)

image = np.load("tasks/example1.npy")
image[image != 0] = 1

if image.shape[-1] == 3:
    print(np.sum([count_object(image[:, :, i])
               for i in range(image.shape[-1])]))
else:
    print(np.sum(count_object(image)))

plt.imshow(image)
plt.show()