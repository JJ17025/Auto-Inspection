from io_rasp import I, O, on, off, readall
from flask import Flask, render_template, request, redirect, url_for
import json
from datetime import datetime
import time

app = Flask(__name__)

@app.route('/')
def index():
    read_pin_dict = readall()
    return render_template(
        'index.html',
        data={"output_pin": O, "read_all_pin": read_pin_dict}
    )
    
@app.route('/auto-refresh')
def index_auto_refresh():
    read_pin_dict = readall()
    return render_template(
        'index_auto_refresh.html',
        data={"output_pin": O, "read_all_pin": read_pin_dict}
    )


@app.route('/on/<pin>', methods=['GET', 'POST'])
def turn_on(pin):
    on(pin)
    return redirect(url_for('index'))


@app.route('/off/<pin>', methods=['GET', 'POST'])
def turn_off(pin):
    off(pin)
    return redirect(url_for('index'))

@app.route('/readpinall')
def read_pin_all():
    res = {}
    for name, [pin,vel] in readall().items():
        res[name] = vel
    res = json.dumps(res, indent=4)
    return f"{res}"

@app.route('/<file_name>/read')
def data_read(file_name):
    if file_name in ['data', 'log']:
        with open('/home/pi/autorun/static/data.txt') as f:
            val = f.read()
        return f"{val}"
    else:
        return f'"/<file_name>/read" file_name in ["data", "log"]'

@app.route('/data/write/<data>')
def data_write(data):
    with open('/home/pi/autorun/static/data.txt' ,'w') as f:
        f.write(data)
    return f"write>{data}"
    
@app.route('/run/<val>')
def run_io_programe(val):
    if val in ['0', '1']:
        with open('/home/pi/autorun/static/run.txt' ,'w') as f:
            f.write(val)
        with open('/home/pi/autorun/static/data.txt' ,'w') as f:
            f.write('None')
        return redirect(url_for('index'))
    return redirect(url_for('index'))
    
        
if __name__ == '__main__':
    while True:
        try:
            with open("/home/pi/autorun/static/log.txt", 'a' ,encoding='utf-8') as f:
                f.write(f'{datetime.now()} run web\n\n')
            app.run('192.168.225.198',port=8080, debug=True)
        except:
            # with open("/home/pi/autorun/static/log.txt", 'a') as f:
                # f.write(f'{datetime.now()}\n{e}\n\n')
            time.sleep(3)
        
