import webbrowser
from threading import Timer
import gui.flaskServe as serve

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")

Timer(1, open_browser).start()
serve.app.run()