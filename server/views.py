#!/usr/bin/python3
from server import server
from image_generator import ImageGenerator
from flask import request
from flask import send_file
import subprocess
from datetime import datetime, timedelta

@server.route('/')
@server.route('/index')
def index():
    return "Hello, World!\n"

@server.route('/meteogalicia')
def get_forecast():
    try:
        subprocess.check_output(['/bin/rm', '/tmp/result.png', '/tmp/result.svg', '/tmp/result_crush.png'])
    except subprocess.CalledProcessError:
        pass

    if request.args.get('battery'):
        ImageGenerator.generate_svg(request.args.get('battery'))
    else:
        ImageGenerator.generate_svg()
    subprocess.check_output(['/usr/bin/rsvg-convert', '-o', '/tmp/result.png', '-w', '600', '-h', '800', '--background-color','white', '/tmp/result.svg'])
    subprocess.check_output(['/usr/bin/pngcrush', '-c', '0', '-nofilecheck', '/tmp/result.png', '/tmp/result_crush.png'])

    return send_file('/tmp/result_crush.png', mimetype='image/png')

@server.route('/meteogalicia/timer')
def get_timer():
    #return str(60*60*8)
    update_hours = [4, 11, 18] ### UTC
    now = datetime.now()
    return str(int(min(map(lambda x:(datetime(now.year, now.month, now.day, x, 0, 0, 0) - now).total_seconds() if (datetime(now.year, now.month, now.day, x, 0, 0, 0) - now).total_seconds() > 0 else ((datetime(now.year, now.month, now.day, x, 0, 0, 0) + timedelta(days=1)) - now).total_seconds(), update_hours))))
