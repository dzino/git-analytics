#!/usr/bin/python3
# -*- coding: utf-8 -*-

# sudo apt install python3-pip
# pip3 install -U Flask  # Server
# pip3 install numpy  # Moving average

# Lists and dictionaries https://habr.com/ru/post/470774/
from typing import List, TypedDict
from flask import Flask, render_template, request  # HTTP server
import threading  # Asynchrony
import webbrowser  # Automatically open in browser
from statistics import Dynamics, Statistics, MovingAverage


class Request(TypedDict):
    value: str
    size: str


class StatisticsParam(TypedDict):
    line: int
    commit: int
    chart: List


class Response(TypedDict):
    lineChanges: int
    changes: List
    line: int
    commit: int
    statistics: List


app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


@app.route('/post', methods=['POST'])
def post() -> Response:
    content: Request = request.json  # Body json
    if content["size"] == "":
        content["size"] = 0
    dynamics = Dynamics(content["value"]).get()
    table = MovingAverage(dynamics["table"], int(content["size"])).get()\
        if int(content["size"]) > 0 else dynamics["table"]
    statistics_obj: StatisticsParam = Statistics(content["value"]).get()
    return {
        "lineChanges": dynamics["lineChanges"],
        "changes": table,
        "line": statistics_obj["line"],
        "commit": statistics_obj["commit"],
        "statistics": statistics_obj["chart"]
    }


# Server start
def start():
    app.run()


# Browser start
def my_web_browser():
    webbrowser.open('http://127.0.0.1:5000/')


if __name__ == '__main__':
    # Creating streams
    t1 = threading.Thread(target=start)  # , args=(10,))
    t2 = threading.Thread(target=my_web_browser)  # , args=(10,))
    # Launching streams
    t1.start()
    t2.start()
    # Waiting for threads to end
    t1.join()
    t2.join()
