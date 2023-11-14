import numpy


def capture(img, stop_event, reconnect_cam):
    import cv2

    cap = cv2.VideoCapture(0)
    cap.set(3, 3264)
    cap.set(4, 2448)
    while not stop_event.is_set():
        s, frame = cap.read()
        if s:
            img[:] = [frame]
        if reconnect_cam.is_set():
            cap = cv2.VideoCapture(0)
            cap.set(3, 3264)
            cap.set(4, 2448)
            reconnect_cam.clear()


def main(img, stop_event, reconnect_cam):
    import cv2
    import numpy as np
    def show(text=None):
        if text:
            cv2.putText(loading_windows, text, (240, 160), 1, 3, (255, 255, 255), 3, -1)
        cv2.imshow('auto inspection', loading_windows)
        cv2.waitKey(1)

    loading_windows = np.full((200, 700, 3), (150, 140, 150), np.uint8)
    cv2.putText(loading_windows, 'Auto Inspection', (20, 90), 1, 5, (255, 255, 255), 5, -1)
    show()
    import os
    import sys
    show('Loading.')
    import pygame
    import statistics
    import json
    show('Loading..')
    from datetime import datetime
    import requests
    import time
    from CV_UI import Button, Display, Exit, TextInput, Select, Setting, Wait, Confirm
    show('Loading...')
    from func.about_image import putTextRect, putTextRect_center, overlay, adj_image, rotate
    from Frames import Frame, Frames, predict
    from Frames import BLACK, FAIL, GREEN, WARNING, BLUE, PINK, CYAN, ENDC, BOLD, ITALICIZED, UNDERLINE
    cv2.destroyWindow('auto inspection')
    url = "http://192.168.225.198:8080"

    def cvimage_to_pygame(image):
        """Convert cvimage into a pygame image"""
        if type(None) == type(image):
            image = np.full((1008, 1344, 3), (30, 50, 25), np.uint8)
        else:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return pygame.image.frombuffer(image.tobytes(), image.shape[1::-1], "RGB")

    def show(surfacenp):
        surface = cvimage_to_pygame(surfacenp)
        display.blit(surface, (0, 0))
        pygame.display.update()
        clock.tick(60)

    pygame.init()
    display = pygame.display.set_mode((1920, 1080))
    pygame.display.set_caption('Auto Inspection')
    clock = pygame.time.Clock()

    esetting = Setting()
    img_form_cam = cv2.imread('ui/no image.png')
    dis = Display()
    fps = []
    pcb_model_name = ''
    autocap = False
    while not stop_event.is_set():
        t1 = datetime.now()
        mouse_pos = pygame.mouse.get_pos()
        keys = pygame.key.get_pressed()
        events = pygame.event.get()
        surfacenp, res_dis = dis.update(mouse_pos, events)  # _______________________________ layer 0 ฉากหลัง
        if pcb_model_name:
            if dis.mode == 'debug':
                dict_data = {}
                dict_data.update(esetting.check_box)
                dict_data.update({'mode_debug': True})
                img_form_cam_and_frame = framesmodel.draw_frame(img_form_cam.copy(), dict_data)
            else:
                img_form_cam_and_frame = framesmodel.draw_frame(img_form_cam.copy(), esetting.check_box)
        else:
            img_form_cam_and_frame = img_form_cam.copy()
        img_form_cam_and_frame = cv2.resize(img_form_cam_and_frame, (1344, 1008))  # ___ layer 1
        surfacenp = overlay(surfacenp, img_form_cam_and_frame, (41, 41))  # _____________ layer 0+1
        if dis.mode == 'debug' and pcb_model_name:
            x, y = mouse_pos
            for event in events:
                if event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                    for name, frame in framesmodel.frames.items():
                        if frame.x1 < (x - 41) / 1344 < frame.x2 and frame.y1 < (y - 41) / 1008 < frame.y2:
                            e = Select(surfacenp.copy())
                            status_list = framesmodel.models[f'{frame.model_used}'].status_list
                            e.add_data(*[f'{frame.name} => {status}' for status in ['-'] + status_list])
                            e.x_shift = x
                            e.y_shift = y
                            while True:
                                mouse_pos = pygame.mouse.get_pos()
                                res = e.update(mouse_pos, pygame.event.get())
                                show(e.img_BG)

                                if res:
                                    if 'break' in res:
                                        break
                                    print(res)

                                    frame.debug_res_name = res.split(' ')[-1]
                                    break
                            break
                    else:
                        e = Select(surfacenp.copy())
                        e.add_data(*[f'All => {i}' for i in ('-', 'ok', 'nopart', 'wrongpart', 'wrongpolarity')])
                        e.x_shift = x
                        e.y_shift = y
                        while True:
                            mouse_pos = pygame.mouse.get_pos()
                            res = e.update(mouse_pos, pygame.event.get())
                            show(e.img_BG)

                            if res:
                                if 'break' in res:
                                    break
                                print(res)
                                status = res.split(' ')[-1]
                                for name, frame in framesmodel.frames.items():
                                    status_list = framesmodel.models[f'{frame.model_used}'].status_list
                                    if status in status_list:
                                        frame.debug_res_name = status
                                    else:
                                        frame.debug_res_name = '-'

                                break
                        break
        if dis.mode == 'run' and pcb_model_name:
            if res_dis == 'mode_menu-run':
                try:
                    res = requests.get(f'{url}/run/0', timeout=0.1)
                    res = requests.get(f'{url}/run/1', timeout=0.1)
                    print(f'{GREEN}status {res.status_code} ping to {url} run IO Raspberrypi')
                except requests.exceptions.Timeout:
                    print(f'{FAIL}Request timed out. The request took longer than 0.1 second to complete.')
                except requests.exceptions.RequestException as e:
                    print(f'{FAIL}An error occurred: {e}')
                print(f'{ENDC}')

            ''' read data "ให้ ถ่ายภาพ --> predict "'''
            error_text = ''
            try:
                res = requests.get(f'{url}/data/read', timeout=0.1)
                if res.status_code == 200:
                    if res.text == 'capture and predict':
                        dis.predict_auto = True
                        dis.predict_res = None
                        requests.get(f'{url}/data/write/predicting', timeout=0.1)
                    elif res.text == 'predicting' and dis.predict_res == 'ok':
                        dis.predict_res = 'ok already_read'
                        requests.get(f'{url}/data/write/ok', timeout=0.1)
                    elif res.text == 'predicting' and dis.predict_res == 'ng':
                        dis.predict_res = 'ng already_read'
                        requests.get(f'{url}/data/write/ng', timeout=0.1)

            except requests.exceptions.Timeout:
                error_text = f"Request timed out. The request took longer than 0.1 second to complete."
            except requests.exceptions.RequestException as e:
                error_text = f"An error occurred: {e}"
            if error_text:
                putTextRect(surfacenp, error_text, (80, 160), 1.05, 2, (0, 0, 255), 5, cv2.LINE_AA)

        if res_dis or dis.predict_auto or autocap:
            if res_dis == 'autocap':
                if autocap:
                    autocap = False
                else:
                    autocap = True

            if res_dis == 'New Project':
                e = TextInput(surfacenp.copy())
                e.x_shift = 200
                e.y_shift = 200
                e.textinput = ''
                while True:
                    time.sleep(0.1)
                    mouse_pos = pygame.mouse.get_pos()
                    res = e.update(mouse_pos, pygame.event.get())
                    show(e.img_BG)
                    if res:
                        print(res)
                    if res in ['Cancel', 'x']:
                        break
                    if res == 'OK':
                        output = e.textinput
                        if not os.path.exists('data'):
                            os.mkdir('data')
                        if not os.path.exists(f'data/{output}'):
                            os.mkdir(f'data/{output}')
                            break

            if res_dis == 'select model':
                e = Select(surfacenp.copy())
                e.add_data(*os.listdir('data'))
                e.x_shift = 43
                e.y_shift = 40
                while True:
                    mouse_pos = pygame.mouse.get_pos()
                    res = e.update(mouse_pos, pygame.event.get())
                    show(e.img_BG)

                    if res:
                        if 'break' in res:
                            break
                        print(res)
                        pcb_model_name = res
                        if pcb_model_name in ['QM7-3473_v2', 'QM7-3473', 'D07']:
                            have_frames_pos_file = False
                            listdir = os.listdir(f'data/{pcb_model_name}')
                            print(listdir)
                            if 'frames pos.json' in listdir:
                                have_frames_pos_file = True
                                framesmodel = Frames(f"{pcb_model_name}")
                                print(framesmodel)

                            if 'mark pos.json' in listdir:
                                have_mark_pos = True

                            e = Wait(surfacenp.copy())
                            e.set_val('Wait', '')
                            e.x_shift = 700
                            e.y_shift = 300
                            for i, (name, model) in enumerate(framesmodel.models.items()):
                                print(model)
                                # try:
                                model.load_model(pcb_model_name)
                                # except:
                                #     print('name have_model = False')
                                have_model = False

                                mouse_pos = pygame.mouse.get_pos()
                                res = e.update(mouse_pos, pygame.event.get())
                                show(e.img_BG)
                                if res:
                                    print(res)
                                if res == 'x':
                                    pcb_model_name = ''
                                    break
                                if i + 1 == len(framesmodel.frames):
                                    img_form_cam_and_frame = framesmodel.draw_frame(img_form_cam.copy())
                                    surface_img = cv2.resize(img_form_cam_and_frame, (1344, 1008))
                                    surfacenp = overlay(surfacenp, surface_img, (41, 41))
                            break
            if res_dis == 'm3:mode_menu-debug':
                e = Select(surfacenp.copy())
                e.add_data('save mark')
                e.x_shift, e.y_shift = mouse_pos
                while True:
                    mouse_pos = pygame.mouse.get_pos()
                    res = e.update(mouse_pos, pygame.event.get())
                    show(e.img_BG)

                    if res:
                        if 'save mark' in res:
                            framesmodel.save_mark(img_form_cam)
                            break
                        break
            if res_dis == 'Take a photo' or autocap or dis.predict_auto:
                print(len(img))
                print(type(img))
                print((img))
                if len(img) == 0:
                    e = Wait(surfacenp.copy())
                    e.set_val('Wait', '')
                    e.x_shift = 700
                    e.y_shift = 300
                    while len(img) == 0:
                        mouse_pos = pygame.mouse.get_pos()
                        res = e.update(mouse_pos, pygame.event.get())
                        show(e.img_BG)
                        if res:
                            print(res)
                        if res in ['OK', 'Cancel', 'x']:
                            break
                if len(img) == 1:
                    img_form_cam = img[0].copy()
                    print(img_form_cam)

                    # img_form_cam = cv2.imread('Save Image/231016 191324.png')

            if res_dis == 'adj image' or res_dis == 'perdict' or dis.predict_auto:
                # img_for_ref = cv2.imread('m.png')
                e = Wait(surfacenp.copy())
                e.set_val('Wait', 'Adjusting image')
                e.x_shift = 700
                e.y_shift = 300
                mouse_pos = pygame.mouse.get_pos()
                res = e.update(mouse_pos, pygame.event.get(), count_time=False)
                show(e.img_BG)

                res = adj_image(img_form_cam, framesmodel)
                if res is not None:
                    img_form_cam = res
                else:
                    e = Confirm(surfacenp.copy())
                    e.set_val('Error', "don't have mark")
                    e.x_shift = 700
                    e.y_shift = 300
                    while True:
                        mouse_pos = pygame.mouse.get_pos()
                        res = e.update(mouse_pos, pygame.event.get())
                        show(e.img_BG)
                        if res:
                            print(res)
                        if res in ['OK', 'Cancel', 'x']:
                            break

            if res_dis == 'perdict' or dis.predict_auto:
                dis.predict_auto = False
                img_form_cam_bgr = cv2.cvtColor(img_form_cam, cv2.COLOR_RGB2BGR)
                if pcb_model_name:
                    framesmodel.crop_img(img_form_cam_bgr)
                    e = Wait(surfacenp.copy())
                    e.set_val('Wait', '')
                    e.x_shift = 700
                    e.y_shift = 300
                    for name, frame in framesmodel.frames.items():
                        predict(frame, framesmodel)
                        mouse_pos = pygame.mouse.get_pos()
                        res = e.update(mouse_pos, pygame.event.get())
                        show(e.img_BG)

                    dis.predict_res = 'ok'
                    dis.old_res = 'ok'
                    for name, frame in framesmodel.frames.items():
                        if frame.highest_score_name not in frame.res_ok:
                            print(frame.res_ok, frame.highest_score_name)
                            if name in ['RJ45.1', 'RJ45.2', 'c2.1', 'c2.2']:
                                continue
                            dis.predict_res = 'ng'
                            dis.old_res = 'ng'

                    print()
                    print('dis.predict_res =', dis.predict_res)



                else:
                    e = Confirm(surfacenp.copy())
                    e.set_val('Error', "don't have modelname", f"pcb model name is {pcb_model_name}")
                    e.x_shift = 700
                    e.y_shift = 300
                    while True:
                        mouse_pos = pygame.mouse.get_pos()
                        res = e.update(mouse_pos, pygame.event.get())
                        show(e.img_BG)
                        if res:
                            print(res)
                        if res in ['OK', 'Cancel', 'x']:
                            break

                surface_img = cv2.resize(img_form_cam_and_frame, (1344, 1008))
                surfacenp = overlay(surfacenp, surface_img, (41, 41))

            if res_dis == 'Save Image':
                e = Confirm(surfacenp.copy())
                e.set_val('Confirm', 'Are you sure', 'You want to Save Image?')
                e.x_shift = 1440
                e.y_shift = 160
                while True:
                    mouse_pos = pygame.mouse.get_pos()
                    res = e.update(mouse_pos, pygame.event.get())
                    show(e.img_BG)
                    if res:
                        print(res)
                    if res == 'OK':
                        if dis.mode in ['manual', 'run']:
                            namefile = datetime.now().strftime('Save Image/%y%m%d %H%M%S.png')
                            cv2.imwrite(namefile, img_form_cam)
                        if dis.mode == 'debug':
                            path = f'data/{pcb_model_name}/img_full/'
                            namefile = datetime.now().strftime('%y%m%d %H%M%S')
                            cv2.imwrite(path + namefile + '.png', img_form_cam)
                            string = ''
                            for name, frame in framesmodel.frames.items():
                                if frame.debug_res_name == '-':
                                    continue
                                string += f'{name}:{frame.debug_res_name}\n'
                                # ย้าย model.h5 go to old folder
                                f'data/{framesmodel.name}/model'
                            # todo
                            # สร้าง folder (path + namefile)
                            with open(path + namefile + '.txt', 'w') as file:
                                file.write(string)

                    if res in ['OK', 'Cancel', 'x']:
                        break

            if res_dis == 'Load Image':
                e = Select(surfacenp.copy())
                data_list = [f'{i}. {data}' for i, data in enumerate(os.listdir('Save Image'), start=1) if
                             '.png' in data]
                e.add_data(*data_list)
                e.x_shift = 1546
                e.y_shift = 121
                play = True
                while play:
                    mouse_pos = pygame.mouse.get_pos()
                    res = e.update(mouse_pos, pygame.event.get())
                    show(e.img_BG)

                    if res:
                        print(res)
                        if 'break' in res:
                            play = False
                        elif res == '- next -':
                            e.next_page()
                        else:
                            namefile = fr'Save Image/{res.split(". ")[1]}'
                            imread = cv2.imread(namefile)
                            h, w, _ = imread.shape
                            if h == 2448 or w == 3264:
                                img_form_cam = imread.copy()
                            else:
                                e = Confirm(surfacenp.copy())
                                e.set_val(f'Confirm (h,w) is {h, w}',
                                          f"which is not equal to (2448 3264)",
                                          'Are you sure', 'You want to Load Image?')
                                e.x_shift = 700
                                e.y_shift = 300
                                while True:
                                    mouse_pos = pygame.mouse.get_pos()
                                    res = e.update(mouse_pos, pygame.event.get())
                                    show(e.img_BG)
                                    if res:
                                        print(res)
                                    if res in ['OK']:
                                        img_form_cam = imread.copy()
                                        break
                                    if res in ['Cancel', 'x']:
                                        break
                            play = False

            if res_dis == 'minimize':
                pygame.display.iconify()

            if res_dis == 'Close':
                e = Exit(surfacenp.copy())
                e.x_shift = 700
                e.y_shift = 400
                play = True
                while play:
                    mouse_pos = pygame.mouse.get_pos()
                    res = e.update(mouse_pos, pygame.event.get())
                    show(e.img_BG)
                    if res:
                        print(res)
                    if res in ['Cancel', 'x']:
                        play = False
                    if res == 'Exit':
                        stop_event.set()
                        play = False

            if res_dis == 'setting':
                esetting = Setting(surfacenp.copy())
                esetting.x_shift = 400
                esetting.y_shift = 200

                while True:
                    mouse_pos = pygame.mouse.get_pos()
                    res = esetting.update(mouse_pos, pygame.event.get())
                    show(esetting.img_BG)
                    if res:
                        print(res)
                    if res in ['x', 'Cancel']:
                        esetting.read_check_box_data()
                        break
                    elif res == 'OK':
                        with open(r'ui\windows_Setting\check box.json', 'w') as file:
                            file.write(json.dumps(esetting.check_box, indent=4))
                        break
                    elif res == 'Reconnect Camera':
                        reconnect_cam.set()
                        e = Wait(surfacenp.copy())
                        e.set_val('Wait', '')
                        e.x_shift = 700
                        e.y_shift = 300
                        while True:
                            mouse_pos = pygame.mouse.get_pos()
                            res = e.update(mouse_pos, pygame.event.get())
                            show(e.img_BG)
                            if res:
                                print(res)
                            if res == 'x':
                                break
                            if reconnect_cam.is_set() == False:
                                break
                        break

        t2 = datetime.now()
        t_sec = (t2 - t1).total_seconds()
        fps.append(t_sec)
        if len(fps) > 20:
            fps = fps[1:]

        if dis.mode == 'run':
            class txt:
                def __init__(self):
                    self.txt_list = []
                    self.row = 0

                def add(self, txt, command=None, image=None):
                    self.txt_list.append([txt, command, image])

                def show(self, surfacenp):
                    for txt, command, image in self.txt_list:
                        print(txt, command)
                        line = 1
                        col = 0
                        color = (255, 255, 255)
                        if command:
                            for c in command:
                                c, v = c.split('=')
                                if c == 'color':
                                    if v == 'y':
                                        color = (0, 255, 255)
                                if c == 'spacing':
                                    line = float(v)
                                if c == 'col':
                                    line = 0
                                    col = float(v)

                        self.row += line
                        print('txt', txt)
                        cv2.putText(surfacenp, txt, (round(1440 + col * 50), round(128 + self.row * 24)),
                                    16, 0.5,
                                    color, 1, cv2.LINE_AA)

                        # if image is not None:
                        #     print('img')
                        #     surfacenp = overlay(surfacenp.copy(), image, (100, 100))

            t = txt()
            for k, v in framesmodel.frames.items():
                if v.highest_score_name and v.highest_score_name in v.res_ok:
                    continue
                t.add(k, ['color=y', 'spacing=1.8', ])
                t.add(v.highest_score_name, ['col=1'], v.img)
                cv2.imshow(k, v.img)
                cv2.waitKey(1)
            t.show(surfacenp)

        if dis.old_res:
            if dis.old_res == 'ok':
                color = (0, 255, 0)
            elif dis.old_res == 'ng':
                color = (0, 0, 255)
            else:
                color = (0, 255, 255)
            cv2.putText(surfacenp, f'{dis.old_res}', (1500, 900), 2, 8, color, 2, cv2.LINE_AA)
        cv2.putText(surfacenp, f'{pcb_model_name}',
                    (80, 26), 2, 0.6, (255, 255, 255), 1, cv2.LINE_AA)

        cv2.putText(surfacenp, f'fps: {round(1 / statistics.mean(fps))}',
                    (10, 1068), 16, 0.45, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(surfacenp, f'pos: {mouse_pos}',
                    (90, 1068), 16, 0.45, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(surfacenp, f'auto capture: {autocap}',
                    (250, 1068), 16, 0.45, (255, 255, 255), 1, cv2.LINE_AA)

        cv2.putText(surfacenp, f'{datetime.now().strftime("%d/%m/%y %H:%M:%S")}',
                    (1750, 1068), 16, 0.45, (255, 255, 255), 1, cv2.LINE_AA)
        show(surfacenp)
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    import cv2
    import numpy as np
    import multiprocessing

    stop_event = multiprocessing.Event()
    reconnect_cam = multiprocessing.Event()
    manager = multiprocessing.Manager()
    img = manager.list()

    capture_process = multiprocessing.Process(target=capture, args=(img, stop_event, reconnect_cam))
    show_process = multiprocessing.Process(target=main, args=(img, stop_event, reconnect_cam))

    capture_process.start()
    show_process.start()

    capture_process.join()
    show_process.join()
