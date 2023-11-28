import json
import time
from capture import capture


def main(multi_data):
    import cv2
    multi_data[:] = [False, 'img', 'write', 'read']
    multi_data[:] = [False, None, {}, {}]
    while True:
        if multi_data[0]:
            img_form_cam = multi_data[1]
            cv2.imshow('img_form_cam', img_form_cam)
            key = cv2.waitKey(1)
            if key == ord('0'):
                print('reconnect')
                multi_data[2] = {"reconnect": {"w": 1000,
                                               "h": 900
                                               }
                                 }
        else:
            print(0)
            time.sleep(1)


if __name__ == '__main__':
    import cv2
    import numpy as np
    import multiprocessing

    manager = multiprocessing.Manager()
    img = manager.list()

    capture_process = multiprocessing.Process(target=capture, args=(img,))
    main_process = multiprocessing.Process(target=main, args=(img,))

    capture_process.start()
    main_process.start()

    capture_process.join()
    main_process.join()
