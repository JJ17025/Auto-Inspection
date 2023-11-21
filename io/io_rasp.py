# import RPi.GPIO as GPIO
from datetime import datetime
import json
import time
path = '/home/pi/autorun/'
path = ''

# GPIO.setmode(GPIO.BCM)
datetime_old = datetime.now()
run_step = 1
HIGH = 0
LOW = 1

I = {
    "Button Input 1": 7,
    "Button Input 2": 8,
    "Senser Infrared 0": 5,
    "Senser Infrared 1": 12,
    "Senser Infrared 2": 20,
    "Reed Switch 11": 6,
    "Reed Switch 12": 13,
    "Reed Switch 21": 19,
    "Reed Switch 22": 21,
}
O = {
    "Button_LED_1": 22,
    "Button_LED_2": 24,
    "Stopper_1": 4,
    "Stopper_2": 18,
}
IO = {}
IO.update(O)
IO.update(I)

# for k, v in I.items():
#     GPIO.setup(v, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
# for k, v in O.items():
#     GPIO.setup(v, GPIO.OUT)




def on(pin):
    if not pin.isnumeric():
        pin = O.get(pin)
    pin = int(pin)
    # GPIO.output(pin, GPIO.HIGH)
    print(f'func >> {pin} is on')


def off(pin):
    if not pin.isnumeric():
        pin = O.get(pin)
    pin = int(pin)
    # GPIO.output(pin, GPIO.LOW)
    print(f'func >> {pin} is off')


def read(pinstr):
    if type(pinstr) == str:
        pin = I.get(pinstr)
    else:
        pin = pinstr
    # res = GPIO.input(pin)

    res = 0
    print(f'func >> {pinstr} is {res}')
    return res

def readall():
    data = {}
    for name, pin in IO.items():
        res = 0
        data[name] = [pin, res]
    print(f'func >> readall == {data}')
    return data



def main_program():
    global run_step, datetime_old

    if 2 <= run_step <= 5:
        if read("Senser Infrared 1") == HIGH and read("Senser Infrared 2") == HIGH:
            # sen1 sen2 เจอ --> stop2 ลงมาเหยียบ
            on('Stopper_2')

    if run_step == 1:
        if read("Senser Infrared 0") == LOW and read("Senser Infrared 1") == LOW:
            # sen0 sen1 ไม่เจอ --> stopper1 ลง  ### เพื่อรอ pcb มา
            on('Stopper_1')
            run_step = 2

    elif run_step == 2:
        if read("Senser Infrared 1") == HIGH:
            # sen1 เจอ --> ___ ### ถ้าเจอ pcb มา delay รอถ่ายภาพ
            run_step = 3
            datetime_old = datetime.now()
            
    elif run_step == 3:
        if (datetime.now() - datetime_old).total_seconds() > 5:
            # หน่วงเวลา รอให้กล้องถ่ายภาพ
            run_step = 4

    elif run_step == 4:
        # บอกให้ predict
        with open(f'{path}static/data.txt', 'w') as f:
            f.write('capture and predict')
        run_step = 5

    elif run_step == 5:
        # อ่านผลลัพธ์
        with open(f'{path}static/data.txt') as f:
            res = f.read()
            print("res",res)
            
        if res == 'ok':
            run_step = 6
        else:
            time.sleep(0.1)

    elif run_step == 6:  # OK
        off('Stopper_1')
        run_step = 7
        datetime_old = datetime.now()
    elif run_step == 7:
        # หน่วงเวลา
        if (datetime.now() - datetime_old).total_seconds() > 2:
            off('Stopper_2')
            run_step = 8
    elif run_step == 8:
        with open(f'{path}static/data.txt', 'w') as f:
            f.write('None')
        run_step = 1



if __name__ == '__main__':
    while True:
        try:
            with open(f"{path}static/log.txt", 'a' ,encoding='utf-8') as f:
                f.write(f'{datetime.now()} run io\n\n')
            old_txt = '0'
            txt = '0'
            step_text = [
            'step 0',
            'ต้องไม่มีอะไรขวาง Infrared Senser 0 and 1 เพื่อจะให้ stoper 1 ลงมากั้น',
            'รอ PCB เข้ามา',
            'หน่วงเวลา รอให้กล้องถ่ายภาพ',
            'บอกให้ computer predict',
            'รออ่านผลลัพธ์ จากการ predict',
            'ปล่อย PCB โดย การยก Stopper_1 ขึ้น',
            'หน่วงเวลา รอยก Stopper_2 ขึ้น',
            'step 8'
            ]
            while True:
                with open(f'{path}static/run.txt') as f:
                    old_txt = txt
                    txt = f.read()
                printt = f'{datetime.now()} run={txt} step={run_step}'
                print(printt)
                with open(f"{path}static/step.txt", 'w') as f:
                    f.write(f'{printt}\n{step_text[run_step]}')
                if old_txt == '0' and txt == '1': # สั่งrun
                    run_step = 1
                    
                elif old_txt == '1' and txt == '0': # สั่งหยุด
                    off('Stopper_1')
                    off('Stopper_2')
                    
                elif txt == '0':
                    off('Stopper_1')
                    off('Stopper_2')
                
                elif txt == '1':
                    main_program()
                
                
                time.sleep(0.1)

        except:        
        # except Exception as e:
            # with open(f"{path}static/log.txt", 'a') as f:
                # f.write(f'{datetime.now()}\n{e}\n\n')
            time.sleep(2)
        
        
        
