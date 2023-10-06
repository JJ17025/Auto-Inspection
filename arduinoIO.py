import json
import time
from time import sleep

import cv2
import keyboard
import serial
from serial.tools.list_ports_windows import comports
from datetime import datetime, timedelta
from predict import predict

class ArduinoIO:
    def __init__(self, COM, *args):

        self.USBtoTTL_name = args
        if COM == 'auto':
            if len(args) == 0:
                print('-----+---------------------')
                for i in comports():
                    print(i)
                print('-----+---------------------')
                return
            COM = self.find_comports(args)

        self.com = COM
        # self.ser = serial.Serial('COM5', baudrate=9600, timeout=0, parity=serial.PARITY_EVEN, rtscts=1)
        self.ser = serial.Serial(COM, baudrate=9600, timeout=0)
        print(f'connect to "{COM}"')


    def find_comports(self, args):
        for i in comports():
            for name_of_comports in args:
                if name_of_comports in i.description:
                    print(f'auto connect')
                    return i.device

    def write(self, txt):
        self.ser.write(f'{txt}\n'.encode())

    def readstr(self, read_round=1, print_round=False):
        '''
        :return: -> str
        '''

        ch = self.ser.read()
        # print(f'-{ch}-') #-b''-
        if ch:
            txt = ch.decode()
            while True:
                t = self.ser.readline().decode()
                if t:
                    # print('------', t, len(t), '\n'in t)
                    txt += t

                    if '\n' in t or len(txt) > 50:
                        txt = txt.strip()
                        # print(f'-{txt}-')
                        break

            return txt

    def str2dict(self, str):
        '''

        :param str: str
        :return: -> dict

        str = B:63/C:51/D:3
        list = ['B:63', 'C:51', 'D:3']
        dict = {'B': '63', 'C': '51', 'D': '3'}
        '''
        dict = {}
        list = str.split('/')
        for i in list:
            k, v = i.split(':')
            dict[k] = int(v)
        return dict

    def int2bit_list(self, byte2bit_list):
        '''
        :param byte2bit_list: int 1 byte
        :return: ->list = [0,0,1,1,1,0,1,1]

        strBIN: '0b111011'
        '''
        strBIN = bin(byte2bit_list)
        list = [int(x) for x in strBIN[2:]]
        list = [int(x) for x in '0' * (8 - len(list)) + strBIN[2:]]
        return list

    def pin(self, dict):
        '''
        dict = {'PIN': 0, 'B': 63, 'C': 49, 'D': 1}
        to
        new_dict = {'B': [0, 0, 1, 1, 1, 1, 1, 1], 'C': [0, 0, 1, 1, 0, 0, 0, 1], 'D': [0, 0, 0, 0, 0, 0, 0, 1]}

        :param dict:
        :return:
        '''
        new_dict = {}
        new_dict_bit1isback = {}
        if 'PIN' in dict:
            for k, v in dict.items():
                if k == 'PIN':
                    continue
                v = self.int2bit_list(v)
                new_dict[k] = v
                new_dict_bit1isback[k] = v[::-1]
            return new_dict_bit1isback

    def ddr(self, dict):
        new_dict = {}
        new_dict_bit1isback = {}
        if 'DDR' in dict:
            for k, v in dict.items():
                if k == 'DDR':
                    continue
                v = self.int2bit_list(v)
                new_dict[k] = v
                new_dict_bit1isback[k] = v[::-1]
            return new_dict_bit1isback

    def port(self, dict):
        new_dict = {}
        new_dict_bit1isback = {}
        if 'PORT' in dict:
            for k, v in dict.items():
                if k == 'PORT':
                    continue
                v = self.int2bit_list(v)
                new_dict[k] = v
                new_dict_bit1isback[k] = v[::-1]
            return new_dict_bit1isback

    def PIN(self, read_round=10000, print_round=False):
        '''
        :param read_round:รอบที่จะให้รอ ถ้าไม่เจอ data return None
        :param print_round:
        :return: dict

        write 'PIN' จากนั้นรอ PIN->
        '''
        self.write('PIN')
        for round in range(read_round):
            txt = self.readstr()
            if txt:
                dict = self.str2dict(txt)
                if 'PIN' in dict:
                    dict = self.pin(dict)
                if print_round:
                    print(round)
                return dict

    def DDR(self, read_round=10000, print_round=False):
        self.write('DDR')
        for round in range(read_round):
            txt = self.readstr()
            if txt:
                dict = self.str2dict(txt)
                if 'DDR' in dict:
                    dict = self.ddr(dict)
                if print_round:
                    print(round)
                return dict

    def PORT(self, read_round=10000, print_round=False):
        self.write('PORT')
        for round in range(read_round):
            txt = self.readstr()
            if txt:
                dict = self.str2dict(txt)
                if 'PORT' in dict:
                    dict = self.port(dict)
                if print_round:
                    print(round)
                return dict


class InOut():
    def __init__(self):
        self.AIO = ArduinoIO('auto', 'Arduino Uno')
        while not self.AIO.com:
            'กำลังเชื่อมต่อ COM'
            self.AIO = ArduinoIO('auto', 'Arduino Uno')
            time.sleep(1)
        self.step = 0
        self.setup()
    def setup(self):
        inputOK = False
        outputOK = False
        while True:
            DDR = self.AIO.DDR()
            print('.', end='')
            if DDR:
                # C0 C1 C2 C3 is output
                if not (DDR['C'][0] == DDR['C'][1] == DDR['C'][2] == DDR['C'][3] == 1):
                    self.AIO.write('DDRC=xxxx1111')
                else:
                    print('\nset DDRC=xxxx1111 ok')
                    outputOK = True

                # D7 D6 is input
                if not (DDR['D'][7] == DDR['D'][6] == 0):
                    self.AIO.write('DDRD=00xxxxxx')
                else:
                    print('\nset DDRD=00xxxxxx ok')
                    inputOK = True

            if inputOK and outputOK:
                break
        self.res3 = None
        self.res2 = None
        self.res1 = None
        self.t1 = 0

    def update(self, img, frames):
        PIN = self.AIO.PIN()

        if PIN:
            if self.step == 0:
                print(0)
                # สั่ง output
                self.AIO.write('PORTC3=1')  # led
                self.AIO.write('PORTC1=0')  # output2 = ยก
                if PIN['D'][7] == 0 and PIN['D'][5] == 0 :
                    self.AIO.write('PORTC0=1')  # output1 = ลง
                else:
                    print(f"รอ dip1 ออก")

                if PIN['C'][1] == 0 and PIN['C'][0] == 1 and PIN['C'][3] == 1:  # if output1 ลง  xxxxxxxxxxxxxxxx
                    print(f'self.step {self.step}')
                    self.step = 1
                    return

            if self.step == 1:
                print('1 wait dippallet')
                if PIN['D'][7] == 1:  # ถ้า senser1 เจอ pcb
                    if PIN['D'][6] == 1:  # ถ้า senser2 เจอ
                        print('error: dip pallet come together')
                    elif PIN['D'][6] == 0:  # แต่ถ้า senser2 ไม่เจอ
                        self.AIO.write('PORTC1=1')  # output2 = ลง
                        self.t1 = datetime.now()
                        print(f'self.step {self.step}')
                        self.step = 2
                        return


            if self.step == 2:
                print(2)
                if (datetime.now()-self.t1).seconds > 3:
                    print(f'self.step {self.step}')
                    self.step = 3
                    return
            if self.step == 3:
                print(3)
                '''อ่านภาพ'''

                print(f'self.step {self.step}')
                self.step = 4
                return 'read img'

            if self.step == 4:
                print(4)
                res = predict(img, frames)
                print(res)
                self.res3 = self.res2
                self.res2 = self.res1
                self.res1 = res

                if self.res3 == self.res2 == self.res1:
                    values = self.res1.values()
                    self.res3 = self.res2 = self.res1 = None


                    if list(values).count('ok') == len(values):
                        self.step = 5.1
                        print(f'self.step {self.step}')
                        return 'OK'
                    else:
                        self.step = 5.2
                        print(f'self.step {self.step}')
                        return 'NG'
                else:
                    return 'read img'




            if self.step == 5.1:
                '''
                แสดง OK
                แสดงภาพ
                '''
                self.AIO.write('PORTC0=0')  # output1 = ยก

                print(f'self.step {self.step}')
                self.step = 0
                time.sleep(5)
                return


            if self.step == 5.2:
                '''
                แสดง NG
                กดปุ่มเพื่อ predict ใหม่
                '''
                if PIN['D'][5] == 1:# if กดปุ่ม

                    self.step = 3
                    return True




if __name__ == '__main__':
    from tensorflow.keras.models import Sequential, load_model

    img = cv2.imread('d992img.png')
    frames = json.loads(open(rf'data\D992vtest\setting_frames.json').read())
    for k, v in frames.items():
        frames[k]['status'] = -1
        frames[k]['color_frame'] = (255, 255, 0)
    print('กำลังโหลด Models')
    for k, v in frames.items():
        print(k, end=' ')
        v['model'] = load_model(fr'data/D992vtest/models/{k}.h5')
    print('\nโหลด Models สำเร็จ')
    s = InOut()
    s.setup()
    while True:
        s.update(img,frames)

