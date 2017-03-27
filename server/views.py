#!/usr/bin/python3
from server import server
from image_generator import ImageGenerator
from flask import request
from flask import send_file
import subprocess

@server.route('/')
@server.route('/index')
def index():
    return "Hello, World!\n"

@server.route('/meteogalicia')
def get_forecast():
    try:
        subprocess.check_output(['/bin/rm', 'result.png', 'result.svg'])
    except subprocess.CalledProcessError:
        pass

    if request.args.get('battery'):
        ImageGenerator.generate_svg(request.args.get('battery'))
    else:
        ImageGenerator.generate_svg()
    subprocess.check_output(['/usr/bin/inkscape', '-z', '-e', 'result.png', '-w', '600', '-h', '800', '-y', '255', 'result.svg'])

    return send_file('../result.png', mimetype='image/png')