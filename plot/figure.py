from io import BytesIO
from pathlib import Path

import cairo
import numpy as np

from .geometry import Point, Rect


class Figure:

    def __init__(self):
        self.axes = list()

        self.rect = Rect(Point(0, 0), Point(800, 600))

        m = 4
        p = 4
        b = 0.5
        self.margins = (m,) * 4
        self.padding = (p,) * 4
        self.border = b

        self.background_color = (1.0, 1.0, 1.0, 1.0)
        self.border_color = (0,) * 4

        self.title = ''
        self.sup_title = ''

    def layout(self):

        m = self.margins
        p = self.padding
        b = self.border
        w, h = self.rect.scale.xy
        self.rect_outer = Rect(Point(m[0] + 0.5 * b, m[2] + 0.5 * b),
                               Point(w - m[0] - m[1] - b, h - m[2] - m[3] - b))

        self.rect_inner = Rect(Point(m[0] + b + p[0], m[2] + b + p[2]),
                               Point(w - m[0] - m[1] - 2 * b - p[0] - p[1], h - m[2] - m[3] - 2 * b - p[2] - p[3]))
        inner_pos = self.rect_inner.position
        inner_scale = self.rect_inner.scale

        self.transform = np.eye(3)
        self.transform_inner = np.array([[inner_scale.x, 0, inner_pos.x],
                                         [0, inner_scale.y, inner_pos.y],
                                         [0, 0, 1]])

        y_pos = self.rect_inner.position.y
        h = self.rect_inner.scale.y / len(self.axes)

        for i in range(len(self.axes)):

            x_pos = self.rect_inner.position.x
            w = self.rect_inner.scale.x / len(self.axes[i])

            for j in range(len(self.axes[i])):

                child_rect = Rect(Point(x_pos, y_pos), Point(w, h))
                child_trans = np.array([[w, 0, x_pos],
                                        [0, h, y_pos],
                                        [0, 0, 1]])
                self.axes[i][j].layout(child_rect, child_trans)
                x_pos += w

            y_pos += h

    def draw(self):

        self.buffer = BytesIO()
        surf = cairo.SVGSurface(self.buffer, *self.rect.scale.xy)

        ctx = cairo.Context(surf)
        ctx.scale(1, 1)
        ctx.set_line_width(0.0002)

        ctx.set_source_rgb(0, 0, 0)

        m = self.margins
        p = self.padding
        b = self.border

        w, h = self.rect.scale.x, self.rect.scale.y

        # Draw border.
        b0 = self.rect_outer.position
        b1 = self.rect_outer.scale
        ctx.set_line_width(b)

        if self.background_color[-1] > 0:
            ctx.set_source_rgba(*self.background_color)
            ctx.rectangle(*b0.xy, *b1.xy)
            ctx.fill()

        if self.border > 0:
            ctx.set_source_rgb(0, 0, 0)
            ctx.rectangle(*b0.xy, *b1.xy)
            ctx.stroke()

        inner_pos = self.rect_inner.position
        inner_scale = self.rect_inner.scale

        trans = np.array([[inner_scale.x, 0, inner_pos.x],
                          [0, inner_scale.y, inner_pos.y],
                          [0, 0, 1]])

        for i in range(len(self.axes)):
            for j in range(len(self.axes[i])):
                self.axes[i][j].draw(ctx)

        (x, y, txt_w, txt_h, dx, dy) = ctx.text_extents(self.title)
        ctx.move_to(0.5 * w - txt_w / 2, 20 + txt_h)
        ctx.show_text(self.title)

        ctx.set_font_size(10)
        (x, y, txt_w, txt_h, dx, dy) = ctx.text_extents(self.sup_title)
        ctx.move_to(0.5 * w - txt_w / 2, 35 + txt_h)
        ctx.show_text(self.sup_title)

    def set_title(self, title: str):
        self.title = title
        self.layout()
        self.draw()

    def save(self, path: Path):
        with open(path, 'wb') as f:
            f.write(self.buffer.getvalue())
