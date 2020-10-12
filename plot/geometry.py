import numpy as np


class Point(np.ndarray):

    def __new__(cls, x, y, *args, **kwargs):
        return super(Point, cls).__new__(cls, *args, shape=(3,), **kwargs)

    def __init__(self, x, y):
        self[0:3] = [x, y, 1]

    @property
    def x(self):
        return self[0]

    @x.setter
    def x(self, value):
        self.x = value

    @property
    def y(self):
        return self[1]

    @y.setter
    def y(self, value):
        self.y = value

    @property
    def xy(self):
        return self[:2]

    def __str__(self):
        return 'Point( x={}, y={} )'.format(*self[:2])


class Rect:

    def __init__(self, position: Point, scale: Point):
        self.position = position
        self.scale = scale

    def __str__(self):
        return 'Rect( position={}, scale={} )'.format(self.position, self.scale)

    def __getitem__(self, idx):
        if idx > 1:
            raise StopIteration

        if idx == 0:
            return self.position
        else:
            return self.scale
