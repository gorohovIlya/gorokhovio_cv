import socket
import numpy as np
import matplotlib.pyplot as plt
from skimage.measure import regionprops
from skimage.morphology import label
from math import sqrt

host = "84.237.21.36"
port = 5152


def recvall(sock, n):
    data = bytearray()
    while len(data) < n:
        pack = sock.recv(n - len(data))
        if not pack:
            return None
        data.extend(pack)
    return data


def calc_rnd_dist(y1, x1, y2, x2):
    res = sqrt((x2-x1) ** 2 + (y2-y1) ** 2)
    return round(res, 1)


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((host, port))
    beat = b"nope"

    plt.ion()
    plt.figure()

    image_count = 0

    while beat != b"yep" and image_count < 10:
        sock.send(b"get")
        bts = recvall(sock, 40002)
        img1 = np.frombuffer(bts[2:40002], dtype="uint8").reshape(bts[0], bts[1])
        img1[img1 != 0] = 1
        labeled = label(img1)
        regions = regionprops(labeled)
        if len(regions) == 2:
            y1, x1 = regions[0].centroid
            y2, x2 = regions[1].centroid
            result = calc_rnd_dist(y1,x1,y2,x2)
            sock.send(str(result).encode())
            print(sock.recv(10), len(regions), result)
            plt.clf()
            plt.subplot(121)
            plt.imshow(img1)
                # plt.subplot(122)
                # plt.imshow(img2)
            plt.pause(1)
            # sock.send(b"beat")
            image_count += 1
    sock.close()