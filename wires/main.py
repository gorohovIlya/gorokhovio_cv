import matplotlib.pyplot as plt
import numpy as np
from skimage.morphology import *
for j in range(1, 7):
    path = f"wires{j}npy.txt"
    data = np.load(path)
    labeled = label(data)
    count = np.max(labeled)
    print(f"Файл wires{j}npy.txt")
    print(f"Количество проводов: {count}")
    for i in range(1, count+1):
        result = binary_erosion(labeled == i, np.ones(3).reshape(3, 1))
        parts = np.max(label(result))
        if parts > 1:
            print(f"Провод {i} разрезан на {parts} частей")
        elif parts == 1:
            print(f"Провод {i} целый!")
        else:
            print(f"Провод {i} уничтожен!")
    print("\n")
# ch = np.load("tasks/wires6npy.txt")
# print(label(ch) == 3)
# plt.imshow(label(ch) == 3)
# plt.show()