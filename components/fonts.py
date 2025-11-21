import os
import pyglet

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MONTSERRAT_PATH = os.path.join(BASE_DIR, "..", "assets", "font", "Montserrat.ttf")
MONTSERRAT_PATH = os.path.normpath(MONTSERRAT_PATH)

pyglet.font.add_file(MONTSERRAT_PATH)

Montserrat = "Montserrat"