import json

import numpy as np
import cv2


def capture(multi_data):
    # multi_data[:]  img , s , read , write
    multi_data[:] = [False, None, {}, {}]
    cap = cv2.VideoCapture(0)
    text_write = {'w': cap.get(3),
                  'h': cap.get(4)}
    while True:
        s, frame = cap.read()
        if s:
            pass
        else:
            frame = np.zeros((3, 3, 3), dtype=np.uint8)
        text_read = multi_data[2]
        if text_read:
            for k, v in text_read.items():
                if k == 'reconnect':
                    cap = cv2.VideoCapture(0)
                    cap.set(3, v['w'])
                    cap.set(4, v['h'])
                    text_write = {'w': cap.get(3),
                                  'h': cap.get(4)}
            text_read = {}

        else:
            text_write = '><'
        multi_data[:] = [s, frame, text_read, text_write]
