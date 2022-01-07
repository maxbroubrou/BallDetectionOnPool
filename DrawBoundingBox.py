#SOURCE : https://stackoverflow.com/questions/64096953/how-to-convert-yolo-format-bounding-box-coordinates-into-opencv-format/64097592

import cv2
import matplotlib.pyplot as plt

dataset =  input("Which folder? (train - valid - test)         > ")
filename = input("Which filename number? (example : 0064)      > ")

try:
    img = cv2.imread("dataset/train/images/%s.jpeg" % filename)

    fl = open("dataset/train/labels/%s.txt" % filename, 'r')
    data = fl.readlines()
    fl.close()
except:
    print("The input folder or filename number may not exist")

dh, dw, _ = img.shape

for dt in data:

    # Split string to float
    _, x, y, w, h = map(float, dt.split(' '))

    # Taken from https://github.com/pjreddie/darknet/blob/810d7f797bdb2f021dbe65d2524c2ff6b8ab5c8b/src/image.c#L283-L291
    # via https://stackoverflow.com/questions/44544471/how-to-get-the-coordinates-of-the-bounding-box-in-yolo-object-detection#comment102178409_44592380
    l = int((x - w / 2) * dw)
    r = int((x + w / 2) * dw)
    t = int((y - h / 2) * dh)
    b = int((y + h / 2) * dh)
    
    if l < 0:
        l = 0
    if r > dw - 1:
        r = dw - 1
    if t < 0:
        t = 0
    if b > dh - 1:
        b = dh - 1

    cv2.rectangle(img, (l, t), (r, b), (255, 255, 255), 1)

plt.imshow(img)
plt.show()