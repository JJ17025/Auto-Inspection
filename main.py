
def capture(data, stop_event):
    import cv2
    cap = cv2.VideoCapture(0)
    cap.set(3, 3264)
    cap.set(4, 2448)
    while not stop_event.is_set():
        data['cap.read'] = cap.read()
        if data['reconnect_cam']:
            data['reconnect_cam'] = False
            cap = cv2.VideoCapture(0)
            cap.set(3, 3264)
            cap.set(4, 2448)


def req_io_box(data, stop_event):
    import requests
    import time
    time.sleep(5)
    dict_data = data['url requests']

    while not stop_event.is_set():
        for k, v in dict_data.items():
            if (v['status code'] == 1) or (v['command'] == 'run all the time'):
                dict_data[k]['text'] = ''
                try:
                    res = requests.get(v['url'], timeout=0.5)
                    dict_data[k]['status code'] = res.status_code
                    dict_data[k]['text'] = res.text
                except:
                    dict_data[k]['status code'] = 0
                    dict_data[k]['text'] = f"error req {v['url']}"
            data['url requests'] = dict_data
            time.sleep(0.2)
        time.sleep(1)


def printdata(data, stop_event):
    import time
    from pprint import pprint
    from Frames import PINK, ENDC, UNDERLINE
    while not stop_event.is_set():
        print(PINK, UNDERLINE)
        pprint(data['url requests'])
        print(ENDC)
        time.sleep(5)


def main(data, stop_event):
    import cv2
    import numpy as np
    import os
    import sys
    import pygame
    import statistics
    import json
    from datetime import datetime
    import requests
    from bs4 import BeautifulSoup
    import time
    from func.CV_UI import mkdir, remove
    from func.CV_UI import Display, Exit, TextInput, Select, Setting, Wait, Confirm
    from func.about_image import overlay, adj_image
    from Frames import Frames, predict
    from Frames import FAIL, ENDC

    def cvimage_to_pygame(image):
        """Convert cvimage into a pygame image"""
        if type(None) == type(image):
            image = np.full((1008, 1344, 3), (30, 50, 25), np.uint8)
        else:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return pygame.image.frombuffer(image.tobytes(), image.shape[1::-1], "RGB")

    def requests_get(url_all, timeout=0.2):
        count_error = 0
        error = None
        while True:
            try:
                res = requests.get(url_all, timeout=timeout)
                if res.status_code == 200:
                    return 'requests OK', res.text
                else:
                    return 'error', f'status_code = {res.status_code}'
            except requests.exceptions.Timeout:
                count_error += 1
                error = f'{FAIL}Timeout. The request took longer than 0.1 second to complete.{ENDC}'
                print(error)
            except requests.exceptions.RequestException as e:
                count_error += 1
                error = f'{FAIL}{e}{ENDC}'
                print(error)
            if count_error > 3:
                break
        return 'error', error

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
    save_img = False
    time_req = True
    PASS_FAIL = [0, 0]
    NG_list = []
    update_dis_res = []
    while not stop_event.is_set():
        t1 = datetime.now()
        mouse_pos = pygame.mouse.get_pos()
        keys = pygame.key.get_pressed()
        events = pygame.event.get()
        surfacenp = dis.update(mouse_pos, events)  # _______________________________ layer 0 ฉากหลัง
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
        if dis.mode == 'run':
            if save_img:
                namefile = datetime.now().strftime('%y%m%d %H%M%S.png')
                mkdir(f'data/{pcb_model_name}/log_img')
                mkdir(f'data/{pcb_model_name}/log_img/{save_img}')
                log_img_list = os.listdir(f'data/{pcb_model_name}/log_img/{save_img}')
                if len(log_img_list) > 10000:
                    # del file log_img_list[0]
                    remove(f'data/{pcb_model_name}/log_img/{save_img}/{log_img_list[0]}')
                    remove(f'data/{pcb_model_name}/log_img/{save_img}/{log_img_list[1]}')
                cv2.imwrite(f'data/{pcb_model_name}/log_img/{save_img}/{namefile}', img_form_cam_and_frame)
                mkdir(f'data/{pcb_model_name}/log_img_original')
                mkdir(f'data/{pcb_model_name}/log_img_original/{save_img}')
                log_img_original_list = os.listdir(f'data/{pcb_model_name}/log_img/{save_img}')
                if len(log_img_original_list) > 10000:
                    remove(f'data/{pcb_model_name}/log_img_original/{save_img}/{log_img_list[0]}')
                    remove(f'data/{pcb_model_name}/log_img_original/{save_img}/{log_img_list[1]}')
                cv2.imwrite(f'data/{pcb_model_name}/log_img_original/{save_img}/{namefile}', img_form_cam)
                save_img = False
            # if dis.mode == 'run' and pcb_model_name:
            if 'mode_menu-run' in dis.update_dis_res:
                time_req_time = datetime.now()
                dis.update_dis_res -= {'mode_menu-run'}
                requests_get(f'{config.ip_address()}/run/0', timeout=0.2)
                requests_get(f'{config.ip_address()}/run/1', timeout=0.2)

            ''' read data "ให้ ถ่ายภาพ --> predict "'''

            error_text = ''
            if time_req == True:
                time_req_time = datetime.now()
                time_req = False

                res_text = (
                    data['url requests']['read data']['status code'],
                    data['url requests']['read data']['text']
                )

            else:
                if (datetime.now() - time_req_time).total_seconds() > 0.6:
                    time_req = True

            text_only = BeautifulSoup(f'{res_text[1]}', 'html.parser').get_text()
            cv2.putText(surfacenp, f'{res_text[0]}: {text_only}', (430, 1068), 16, 0.45, (255, 255, 255), 1,
                        cv2.LINE_AA)
            if res_text[0] == 200:
                if res_text[1] == 'capture and predict':
                    dis.update_dis_res = dis.update_dis_res.union({'Take a photo', 'adj image', 'predict'})
                    dis.predict_res = None
                    requests_get(f'{config.ip_address()}/data/write/AI is predicting', timeout=0.2)
                elif res_text[1] == 'AI is predicting' and dis.predict_res == 'ok':
                    requests_get(f'{config.ip_address()}/data/write/ok', timeout=0.2)
                    dis.predict_res = 'ok already_read'
                elif res_text[1] == 'AI is predicting' and dis.predict_res == 'ng':
                    requests_get(f'{config.ip_address()}/data/write/ng', timeout=0.2)
                    dis.predict_res = 'ng already_read'

                elif res_text[1] == 'pro=[1, 1, 1, 0]':
                    dis.select_model = 'QM7-3472'
                    dis.update_dis_res.add('select model')
                    requests_get(f'{config.ip_address()}/data/write/None', timeout=0.2)
                elif res_text[1] == 'pro=[1, 1, 0, 1]':
                    dis.select_model = 'QM7-3473_v2'
                    dis.update_dis_res.add('select model')
                    requests_get(f'{config.ip_address()}/data/write/None', timeout=0.2)

        if autocap:
            dis.update_dis_res.add('Take a photo')
        if dis.update_dis_res:
            # print(dis.update_dis_res)
            if 'autocap' in dis.update_dis_res:
                dis.update_dis_res -= {'autocap'}
                if autocap:
                    autocap = False
                else:
                    autocap = True

            elif 'New Project' in dis.update_dis_res:
                dis.update_dis_res -= {'New Project'}
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

            elif 'select model' in dis.update_dis_res:
                dis.update_dis_res -= {'select model'}
                PASS_FAIL = [0, 0]
                e = Select(surfacenp.copy())
                e.add_data(*os.listdir('data'))
                e.x_shift = 43
                e.y_shift = 40
                while True:
                    mouse_pos = pygame.mouse.get_pos()
                    res = e.update(mouse_pos, pygame.event.get())
                    show(e.img_BG)
                    if dis.select_model:
                        res = dis.select_model
                        dis.select_model = None
                    if res:
                        if 'break' in res:
                            break
                        print(res)
                        pcb_model_name = res
                        if True:
                            # if pcb_model_name in ['QM7-3473_v2', 'QM7-3473', 'D07']:
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
            elif 'm3:mode_menu-debug' in dis.update_dis_res:
                dis.update_dis_res -= {'m3:mode_menu-debug'}
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
            elif 'm3:mode_menu-run' in dis.update_dis_res:
                dis.update_dis_res -= {'m3:mode_menu-run'}
                e = Select(surfacenp.copy())
                e.add_data('predict')
                e.x_shift, e.y_shift = mouse_pos
                while True:
                    mouse_pos = pygame.mouse.get_pos()
                    res = e.update(mouse_pos, pygame.event.get())
                    show(e.img_BG)
                    if res:
                        if 'predict' in res:
                            requests_get(f'{config.ip_address()}/data/write/AI is predicting', timeout=0.2)
                            break
                        break
            elif 'Take a photo' in dis.update_dis_res:
                dis.update_dis_res -= {'Take a photo'}
                if len(data) == 0:
                    e = Wait(surfacenp.copy())
                    e.set_val('Wait', '')
                    e.x_shift = 700
                    e.y_shift = 300
                    while data['cap.read'][0] == False:
                        mouse_pos = pygame.mouse.get_pos()
                        res = e.update(mouse_pos, pygame.event.get())
                        show(e.img_BG)
                        if res:
                            print(res)
                        if res in ['OK', 'Cancel', 'x']:
                            break
                img_form_cam = data['cap.read'][1].copy()
                # img_form_cam = cv2.imread(r"C:\Python_Project\Auto Inspection\Save Image\231003 193441.png")

            elif 'adj image' in dis.update_dis_res:
                dis.update_dis_res -= {'adj image'}
                NG_list = []
                if pcb_model_name:
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
                        if dis.mode != 'run':
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

            elif 'predict' in dis.update_dis_res:
                dis.update_dis_res -= {'predict'}
                if pcb_model_name:
                    img_form_cam_bgr = cv2.cvtColor(img_form_cam, cv2.COLOR_RGB2BGR)
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
                    dis.predict_time = datetime.now()
                    dis.predict_res = 'ok'
                    dis.old_res = 'ok'
                    for name, frame in framesmodel.frames.items():
                        if frame.highest_score_name not in frame.res_show['OK']:
                            NG_list.append([frame.pcb_frame_name, frame.resShow()])
                            # if name in ['RJ45.1', 'RJ45.2', 'c2.1', 'c2.2']:
                            #     continue
                            dis.predict_res = 'ng'
                            dis.old_res = 'ng'
                    if dis.old_res == 'ok':
                        PASS_FAIL[0] += 1
                    if dis.old_res == 'ng':
                        PASS_FAIL[1] += 1
                    print()
                    print('dis.predict_res =', dis.predict_res)

                # else:
                #     e = Confirm(surfacenp.copy())
                #     e.set_val('Error', "don't have modelname", f"pcb model name is {pcb_model_name}")
                #     e.x_shift = 700
                #     e.y_shift = 300
                #     while True:
                #         mouse_pos = pygame.mouse.get_pos()
                #         res = e.update(mouse_pos, pygame.event.get())
                #         show(e.img_BG)
                #         if res:
                #             print(res)
                #         if res in ['OK', 'Cancel', 'x']:
                #             break
                save_img = dis.predict_res
                surface_img = cv2.resize(img_form_cam_and_frame, (1344, 1008))
                surfacenp = overlay(surfacenp, surface_img, (41, 41))

            elif 'Save Image' in dis.update_dis_res:
                dis.update_dis_res -= {'Save Image'}
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
                            mkdir(path)
                            namefile = datetime.now().strftime('%y%m%d %H%M%S')
                            cv2.imwrite(path + namefile + '.png', img_form_cam)
                            string = ''
                            for name, frame in framesmodel.frames.items():
                                if frame.debug_res_name == '-':
                                    continue
                                string += f'{name}:{frame.debug_res_name}\n'
                                # ย้าย model.h5 go to old folder
                                f'data/{framesmodel.name}/model'

                            with open(path + namefile + '.txt', 'w') as file:
                                file.write(string)

                    if res in ['OK', 'Cancel', 'x']:
                        break

            elif 'Load Image' in dis.update_dis_res:
                dis.update_dis_res -= {'Load Image'}
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
                                    if res in ['OK']:
                                        img_form_cam = imread.copy()
                                        break
                                    if res in ['Cancel', 'x']:
                                        break
                            play = False
                            if dis.mode == 'debug':
                                dis.update_dis_res.add('adj image')

            elif 'minimize' in dis.update_dis_res:
                dis.update_dis_res -= {'minimize'}
                pygame.display.iconify()

            elif 'Close' in dis.update_dis_res:
                dis.update_dis_res -= {'Close'}
                e = Exit(surfacenp.copy())
                e.x_shift = 700
                e.y_shift = 400
                play = True
                while play:
                    mouse_pos = pygame.mouse.get_pos()
                    res = e.update(mouse_pos, pygame.event.get())
                    show(e.img_BG)
                    if res in ['Cancel', 'x']:
                        play = False
                    if res == 'Exit':
                        stop_event.set()
                        play = False

            elif 'setting' in dis.update_dis_res:
                dis.update_dis_res -= {'setting'}
                esetting = Setting(surfacenp.copy())
                esetting.x_shift = 400
                esetting.y_shift = 200

                while True:
                    mouse_pos = pygame.mouse.get_pos()
                    res = esetting.update(mouse_pos, pygame.event.get())
                    show(esetting.img_BG)
                    if res in ['x', 'Cancel']:
                        esetting.read_check_box_data()
                        break
                    elif res == 'OK':
                        with open(r'ui\windows_Setting\check box.json', 'w') as file:
                            file.write(json.dumps(esetting.check_box, indent=4))
                        break
                    elif res == 'Reconnect Camera':
                        data['reconnect_cam'] = True
                        e = Wait(surfacenp.copy())
                        e.set_val('Wait', '')
                        e.x_shift = 700
                        e.y_shift = 300
                        while True:
                            mouse_pos = pygame.mouse.get_pos()
                            res = e.update(mouse_pos, pygame.event.get())
                            show(e.img_BG)
                            if res == 'x':
                                break
                            if data['reconnect_cam'] == False:
                                break
                        break

        t2 = datetime.now()
        t_sec = (t2 - t1).total_seconds()
        fps.append(t_sec)
        if len(fps) > 20:
            fps = fps[1:]

        if dis.old_res == 'ok':
            color = (0, 255, 0)
            if (datetime.now() - dis.predict_time).total_seconds() < 3:
                cv2.rectangle(surfacenp, (1540, 140), (1780, 280), (75, 76, 79), -1)
                cv2.putText(surfacenp, f'{dis.old_res}'.upper(), (1550, 260), 2, 5, color, 8, cv2.LINE_AA)

        if dis.old_res == 'ng':
            color = (0, 0, 255)
            cv2.rectangle(surfacenp, (1540, 140), (1780, 280), (75, 76, 79), -1)
            cv2.putText(surfacenp, f'{dis.old_res}'.upper(), (1550, 260), 2, 5, color, 8, cv2.LINE_AA)

        if dis.mode in ['manual', 'run']:
            cv2.putText(surfacenp, f'Pass', (1450, 920), 2, 1.2, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.putText(surfacenp, f'Fail', (1450, 970), 2, 1.2, (0, 0, 255), 2, cv2.LINE_AA)
            cv2.putText(surfacenp, f'Pass rate', (1450, 1020), 2, 1.2, (255, 255, 255), 2, cv2.LINE_AA)

            cv2.putText(surfacenp, f': {PASS_FAIL[0]}', (1660, 920), 2, 1.2, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.putText(surfacenp, f': {PASS_FAIL[1]}', (1660, 970), 2, 1.2, (0, 0, 255), 2, cv2.LINE_AA)
            cv2.putText(surfacenp, f': {round(PASS_FAIL[0] * 100 / (PASS_FAIL[0] + PASS_FAIL[1] + 0.000001), 2)}%',
                        (1660, 1020), 2, 1.2, (255, 255, 255), 2, cv2.LINE_AA)

            NG_list_show = NG_list
            NG_list_len = len(NG_list)
            if NG_list_len >= 10:
                NG_list_show = NG_list_show[:10]
                NG_list_show.append(['Other NG', f'{NG_list_len - 10} position'])
            line = 0
            for name, res in NG_list_show:
                cv2.putText(surfacenp, f'{name}  ' + f'{res}',
                            (1450, 320 + line), 2, 1, (255, 255, 255), 1, cv2.LINE_AA)
                line += 40

        cv2.putText(surfacenp, f'{pcb_model_name}',
                    (80, 26), 2, 0.6, (255, 255, 255), 1, cv2.LINE_AA)

        cv2.putText(surfacenp, f'fps: {round(1 / statistics.mean(fps))}',
                    (10, 1068), 16, 0.45, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(surfacenp, f'pos: {mouse_pos}',
                    (90, 1068), 16, 0.45, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(surfacenp, f'Auto Capture: {autocap}',
                    (250, 1068), 16, 0.45, (255, 255, 255), 1, cv2.LINE_AA)

        cv2.putText(surfacenp, f'{datetime.now().strftime("%d/%m/%y %H:%M:%S")}',
                    (1750, 1068), 16, 0.45, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(surfacenp, f'program version: 1.0',
                    (1520, 25), 16, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        show(surfacenp)
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    import cv2
    import numpy as np
    import multiprocessing
    import json
    import os
    from func.Config import config

    stop_event = multiprocessing.Event()
    manager = multiprocessing.Manager()
    data = manager.dict()
    data['cap.read'] = (False, None)
    data['reconnect_cam'] = False

    data['url requests'] = {
        'write data': {
            'command': '',
            'input data': {'data': 'start_program'},
            'url': f'{config.ip_address()}/data/write/<data>',
            'status code': 0,
            'text': '',
            'note': ''
        },
        'read data': {
            'command': 'run all the time',
            'input data': {},
            'url': f'{config.ip_address()}/static/data.txt',
            'status code': 0,
            'text': '',
            'note': ''
        },
        'read step': {
            'command': '',
            'input data': {},
            'url': f'{config.ip_address()}/static/step.txt',
            'status code': 0,
            'text': '',
            'note': ''
        },
    }

    capture_process = multiprocessing.Process(target=capture, args=(data, stop_event))
    show_process = multiprocessing.Process(target=main, args=(data, stop_event))
    req_io_box_process = multiprocessing.Process(target=req_io_box, args=(data, stop_event))
    # printdata_process = multiprocessing.Process(target=printdata, args=(data, stop_event))

    capture_process.start()
    show_process.start()
    req_io_box_process.start()
    # printdata_process.start()

    capture_process.join()
    show_process.join()
    req_io_box_process.join()
    # printdata_process.join()
