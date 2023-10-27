import RPi.GPIO as GPIO
from datetime import datetime
import json


GPIO.setmode(GPIO.BCM)
datetime_old = datetime.now()
run_step = 0
HIGH = 1
LOW = 0

I = {
    "Button Input 1": 4,
    "Button Input 2": 17,
    "Senser Infrared 0": 10,
    "Senser Infrared 1": 9,
    "Senser Infrared 2": 11,
    "Reed Switch 11": 5,
    "Reed Switch 12": 6,
    "Reed Switch 21": 13,
    "Reed Switch 22": 19,
}
O = {
    "Button_LED_1": 23,
    "Button_LED_2": 24,
    "Stopper_1": 8,
    "Stopper_2": 7,
}
IO = {}
IO.update(I)
IO.update(O)

for k, v in I.items():
    GPIO.setup(v, GPIO.IN)
for k, v in O.items():
    GPIO.setup(v, GPIO.OUT)




def on(pin):
    if type(pin) == str:
        pin = O.get(pin)
    GPIO.output(pin, GPIO.HIGH)
    print(f'{pin} is on')


def off(pin):
    if type(pin) == str:
        pin = O.get(pin)
    GPIO.output(pin, GPIO.LOW)
    print(f'{pin} is off')


def read(pinstr):
    if type(pinstr) == str:
        pin = O.get(pinstr)
    else:
        pin = pinstr
    res = GPIO.input(pin)
    print(f'read {pinstr} == {res}')
    return res





def main_program():
    global run_step, datetime_old
    print(f'step = {run_step}')

    if run_step >= 2:
        if read("Senser Infrared 1") == HIGH and read("Senser Infrared 2") == HIGH:
            # sen1 sen2 เจอ --> stop2 ลงมาเหยียบ
            on('Stopper_2')

    if run_step == 0:
        off('Stopper_1')
        off('Stopper_2')
        run_step = 1

    elif run_step == 1:
        if read("Senser Infrared 0") == LOW and read("Senser Infrared 1") == LOW:
            # sen0 sen1 ไม่เจอ --> stopper1 ลง  ### เพื่อรอ pcb มา
            on('Stopper_1')
            run_step = 2
            datetime_old = datetime.now()
        else:
            print('มีอะไรขวาง Senser Infrared')

    elif run_step == 2:
        if read("Senser Infrared 1") == HIGH:
            # sen1 เจอ --> ___ ### ถ้าเจอ pcb มา delay รอถ่ายภาพ
            run_step = 3

    elif run_step == 3:
        if (datetime.now() - datetime_old).total_seconds() > 2:
            # หน่วงเวลา predict
            run_step = 4

    elif run_step == 4:
        # predict
        predict_auto = True
        run_step = 5.1
        # run_step = 6.1

    elif run_step == 5.1:  # OK
        off('Stopper_1')
        run_step = 5.2
    elif run_step == 5.2:
        # หน่วงเวลา
        if (datetime.now() - datetime_old).total_seconds() > 2:
            off('Stopper_2')
            run_step = 5.3
    elif run_step == 5.3:
        run_step = 1


if __name__ == '__main__':
    while True:
        with open('run.txt') as f:
            txt = f.read()
        print(txt)
        if txt == '1':
            main_program()
        else:
            off('Stopper_1')
            off('Stopper_2')
