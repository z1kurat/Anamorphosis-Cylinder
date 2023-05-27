import math

import numpy as np

import cv2

import tkinter as tk
from tkinter import filedialog

import sys

import os

root = tk.Tk()
root.withdraw()

file_path = filedialog.askopenfilename(title="Выберите видеофайл",
                                       filetypes=(("Video files", "*.mp4 *.avi *.mkv"), ("all files", "*.*")))

if not file_path:
    sys.exit()

save_dictionary = filedialog.askdirectory(title="Сохранить файл")

if not save_dictionary:
    sys.exit()

filename = os.path.splitext(os.path.basename(file_path))[0]

cap = cv2.VideoCapture(file_path)

cv2.namedWindow('Hologram', cv2.WINDOW_NORMAL)
cv2.setWindowProperty('Hologram', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

screen_width = cv2.getWindowImageRect('Hologram')[2]
screen_height = cv2.getWindowImageRect('Hologram')[3]

output_file_path = os.path.join(save_dictionary, filename + "_anamorphosis" + '.mp4')

fps = int(cap.get(cv2.CAP_PROP_FPS))
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_file_path, fourcc, fps, (screen_width, screen_height))

completion = 0.85
small_radius = 200

extended = math.trunc(math.sqrt(2 * math.pow(small_radius, 2)))

big_radius = int(screen_height * completion)

while cap.isOpened():
    ret, frame = cap.read()

    if not ret:
        break

    resized_frame = cv2.resize(frame, (screen_width, screen_height))
    result_frame = np.zeros([screen_height + extended, screen_width + extended, 3], dtype=np.uint8)

    for i in range(0, screen_width):
        for j in range(0, screen_height):
            shift_i = i - math.trunc((extended + screen_width) / 2)
            shift_j = screen_height - j

            angle = math.atan2(shift_i, shift_j)

            new_i = math.trunc(i - math.trunc((extended + screen_width) / 2) + small_radius * math.sin(angle))
            new_j = math.trunc(screen_height - j + small_radius * math.cos(angle))

            if new_i > math.trunc((extended + screen_width) / 2):
                new_i -= math.trunc((extended + screen_width) / 2)
            else:
                new_i += math.trunc((extended + screen_width) / 2)

            x = math.trunc(math.sqrt(math.pow(shift_i, 2) + math.pow(shift_j, 2)))
            y = math.trunc((angle + math.pi * 1.05) * big_radius / math.pi)

            if x < big_radius + 100:
                result_frame[screen_height + extended - new_j, new_i] = resized_frame[x, y]

    resized_frame = cv2.resize(result_frame, (screen_width, screen_height))

    cv2.imshow('Hologram', resized_frame)
    out.write(result_frame)

    key = cv2.waitKey(25)
    if key == 27:
        break

cap.release()
out.release()

cv2.destroyAllWindows()
