#!/usr/bin/python3
from flask import Flask

server = Flask(__name__)
from server import views
