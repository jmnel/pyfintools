import numpy as np
import cairo

from .geometry import Rect, Point


class Axes:

    def __init__(self):
        self.plot_series = list()

        m = 20
        p = 10
        b = 0.0
        self.margins = (m,) * 4
        self.padding = (p,) * 4
        self.border = b

        self.background_color = (0.86, 0.86, 0.86, 0)
        self.border_color = (0, 0, 0, 1)

    def layout(self, rect: Rect, transform: np.ndarray):

        m = self.margins
        p = self.padding
        b = self.border

        self.rect = rect
        w, h = self.rect.scale.xy

        self.rect_outer = Rect(Point(rect.position.x + m[0] + 0.5 * b, rect.position.y + m[2] + 0.5 * b),
                               Point(w - m[0] - m[1] - b, h - m[2] - m[3] - b))

        self.rect_inner = Rect(Point(rect.position.x + m[0] + b + p[0], rect.position.y + m[2] + b + p[2]),
                               Point(w - m[0] - m[1] - 2 * b - p[0] - p[1], h - m[2] - m[3] - 2 * b - p[2] - p[3]))
        inner_pos = self.rect_inner.position
        inner_scale = self.rect_inner.scale

        self.transform = transform
        self.transform_inner = np.array([[inner_scale.x, 0, inner_pos.x],
                                         [0, inner_scale.y, inner_pos.y],
                                         [0, 0, 1]])

        for ps in self.plot_series:
            ps.layout(self.rect_inner, self.transform_inner)

    def draw(self, ctx: cairo.Context):

        p0 = self.rect_inner.position
        s0 = self.rect_inner.scale

        if self.background_color[-1] > 0:
            ctx.set_source_rgba(*self.background_color)
            ctx.rectangle(*p0.xy, *s0.xy)
            ctx.fill()

        if self.border > 0 and self.border_color[-1] > 0:
            ctx.set_source_rgba(*self.border_color)
            ctx.rectangle(*p0.xy, *s0.xy)
            ctx.stroke()

        for ps in self.plot_series:
            ps.draw(ctx)
