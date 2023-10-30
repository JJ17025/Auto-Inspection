from io_rasp import I, O, on, off
from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)

data = O

@app.route('/')
def index():
    return render_template('index.html',data)


@app.route('/on/<int:pin>', methods=['POST'])
def turn_on(pin):
    print('on', pin)
    return redirect(url_for('index'))


@app.route('/off/<int:pin>', methods=['POST'])
def turn_off(pin):
    print('off', pin)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
