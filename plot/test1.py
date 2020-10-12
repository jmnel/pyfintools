import sqlite3
from pprint import pprint
from collections import namedtuple
from six import StringIO
import xml.etree.ElementTree as etree
import re

import numpy as np
import cairo
import pandas as pd
import matplotlib
matplotlib.use('module://matplotlib-backend-kitty')
import matplotlib.pyplot as plt
import matplotlib as mpl
from svgpath2mpl import parse_path

from figure import Figure
from geometry import Point, Rect
from axes import Axes
# from ohlcv import TickCandles, TickVolume
import plot
import model


green = (0, 0.8, 0.4)
red = (0.55, 0.15, 0)


data = model.TickModel('ib.sqlite3')
data.load_ticks('KODK', '2020-07-29')
data.tick_bars(n=20)

# fig, axs = plot.subplots(2, 1)


fig, axs = plot.ohlcv_plot(model=data)

fig.save('temp.svg')

with open('temp.svg', 'rt') as f:
    svg_txt = f.read()
svg_txt.replace('\n', '')

#tree = etree.parse(StringIO(svg_txt))
tree = etree.parse('temp.svg')
root = tree.getroot()
width = int(re.match(r'\d+', root.attrib['width']).group())
height = int(re.match(r'\d+', root.attrib['height']).group())
path_elems = root.findall('.//{http://www.w3.org/2000/svg}path')

print(len(path_elems))


paths = [parse_path(elem.attrib['d']) for elem in path_elems]
facecolors = [elem.attrib.get('fill', 'none') for elem in path_elems]
edgecolors = [elem.attrib.get('stroke', 'none') for elem in path_elems]
linewidths = [elem.attrib.get('stroke_width', 1) for elem in path_elems]
collection = mpl.collections.PathCollection(paths,
                                            edgecolors=edgecolors,
                                            linewidths=linewidths,
                                            facecolors=facecolors)


for idx, p in enumerate(paths):
    print(f'{idx} -> {p}')
print(len(paths))
collection = mpl.collections.PathCollection(paths,
                                            edgecolors=edgecolors,
                                            linewidths=linewidths,
                                            facecolors=facecolors)
fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(111)
collection.set_transform(ax.transData)
ax.add_artist(collection)
ax.set_xlim([0, width])
ax.set_ylim([height, 0])

plt.show()
