import numpy as np

image = np.load('stars.npy')
image2 = np.array([[1,0,0,0,1],
                   [0,1,0,1,0],
                   [0,0,1,0,0],
                   [0,1,0,1,0],
                   [1,0,0,0,1]
                   ])
image3 = np.array([[0,0,1,0,0],
                   [0,0,1,0,0],
                   [1,1,1,1,1],
                   [0,0,1,0,0],
                   [0,0,1,0,0]])

def count_stars(image):
    cnt = 0
    for y in range(0, image.shape[0]-5):
        for x in range(0, image.shape[1]-5):
            sub = np.array(image[y:y+5, x:x+5], dtype="uint8")
            if np.array_equal(sub, image2) or np.array_equal(sub, image3):
                cnt += 1
    return cnt

print(count_stars(image))
