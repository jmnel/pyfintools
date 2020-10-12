import numpy as np
import cairo

from plot_series import PlotSeries
from geometry import Point, Rect
from model import TickModel


class TickCandles(PlotSeries):

    def __init__(self, model: TickModel):
        super().__init__()

        self.model = model

        m = 20
        p = 10
        b = 0
        self.margins = (m,) * 4
        self.padding = (p,) * 4
        self.border = b
        self.grid_line_width = 0.5
        self.stick_line_width = 0.5
        self.candle_width_scale = 0.4
        self.x_axis_space = 30
        self.y_axis_space = 20

        self.background_color = (0, 0, 0, 0)
        self.border_color = (0.0, 0, 0, 1)

        self.font_size = 12
        self.font_face = 'InputSans'

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
                                         [0, -inner_scale.y, inner_pos.y + inner_scale.y],
                                         [0, 0, 1]])
        self.transform_plot = np.array([[inner_scale.x - self.x_axis_space, 0, inner_pos.x],
                                        [0, -inner_scale.y + self.y_axis_space,
                                            inner_pos.y + inner_scale.y - self.y_axis_space],
                                        [0, 0, 1]])

    def draw(self, ctx: cairo.Context):

        p0 = self.rect_inner.position
        s0 = self.rect_inner.scale

        if self.background_color[-1] > 0:
            ctx.set_source_rgba(*self.background_color)
            ctx.rectangle(*p0.xy, *s0.xy)
            ctx.fill()

        if self.border > 0 and self.border_color[-1] > 0:
            ctx.set_line_width(self.border)
            ctx.set_source_rgba(*self.border_color)
            ctx.rectangle(*p0.xy, *s0.xy)
            ctx.stroke()

        ctx.select_font_face(self.font_face, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(self.font_size)
        self.draw_ticks(ctx)

    def draw_ticks(self, ctx: cairo.Context):

        #        green = (0, 0.4, 0.2)
        #        red = (0.55, 0.15, 0)
        green = (92 / 256, 214 / 256, 92 / 256)
        red = (1, 102 / 256, 102 / 256)

        bars = self.model.bars_df

        ylim = (bars.low.min(), bars.high.max())

        axis_x_0 = self.transform_plot @ np.array([-0.03, -0.06, 1])
        axis_x_1 = self.transform_plot @ np.array([1.03, -0.06, 1])
        axis_y_0 = self.transform_plot @ np.array([1.03, 1, 1])

        ctx.set_line_width(self.grid_line_width)
        ctx.set_source_rgb(0, 0, 0)
        ctx.move_to(*axis_x_0[:2])
        ctx.line_to(*axis_x_1[:2])
        ctx.line_to(*axis_y_0[:2])
        ctx.stroke()

        ctx.set_font_size(10)
        x_ticks = [-0.5, ] + list(range(7))
        x_tick_labels = ['9:30', ] + list(f'{10+i}:00' for i in x_ticks[1:])
        for idx, tick in enumerate(x_ticks):

            grid_0 = self.transform_plot @ np.array([tick / 6.5 + 0.5 / 6.5, -0.06, 1])
            grid_1 = self.transform_plot @ np.array([tick / 6.5 + 0.5 / 6.5, -0.08, 1])

            ctx.set_line_width(self.grid_line_width)
            ctx.move_to(*grid_0[:2])
            ctx.line_to(*grid_1[:2])
            ctx.set_source_rgb(0, 0, 0)
            ctx.stroke()

            ctx.set_source_rgb(0, 0, 0)
            tick_label = x_tick_labels[idx]
            (x, y, w, h, dx, dy) = ctx.text_extents(tick_label)
            ctx.move_to(grid_0[0] - w / 2, grid_0[1] + h / 2 + 0.9 * self.y_axis_space)
            ctx.show_text(tick_label)

        y_tick_min = np.ceil(ylim[0]) + 0
        y_tick_max = np.ceil(ylim[1])

        num_y_ticks = 6
        tick_int = int((y_tick_max - y_tick_min) / num_y_ticks)

        y_ticks = list(y_tick_min + i * tick_int for i in range(num_y_ticks))
        y_tick_labels = list('{:.0f}.00'.format(i) for i in y_ticks)

        for idx in range(num_y_ticks):

            tick = y_ticks[idx]
            label = y_tick_labels[idx]
            grid_0 = self.transform_plot @ np.array([1.03, (tick - ylim[0]) / (ylim[1] - ylim[0]), 1])
            grid_1 = self.transform_plot @ np.array([1.04, (tick - ylim[0]) / (ylim[1] - ylim[0]), 1])

            ctx.move_to(*grid_0[:2])
            ctx.line_to(*grid_1[:2])
            ctx.stroke()

            (x, y, w, h, dx, dy) = ctx.text_extents(tick_label)
            ctx.move_to(grid_0[0] + w / 2 - 4, grid_0[1] + h / 2)
            ctx.show_text(label)

        for idx in range(len(bars)):

            x0 = bars.t_open.iloc[idx] / ((16 - 9.5) * 60 * 60)
            x1 = bars.t_close.iloc[idx] / ((16 - 9.5) * 60 * 60)

            h = bars.high.iloc[idx]
            l = bars.low.iloc[idx]
            o = bars.open.iloc[idx]
            c = bars.close.iloc[idx]

            y0 = (l - ylim[0]) / (ylim[1] - ylim[0])
            y1 = (h - ylim[0]) / (ylim[1] - ylim[0])

            y2 = (o - ylim[0]) / (ylim[1] - ylim[0])
            y3 = (c - ylim[0]) / (ylim[1] - ylim[0])

            if y2 < y3:
                c = green
            else:
                c = red

            ctx.set_source_rgb(*c)
            y2, y3 = min(y2, y3), max(y2, y3)

            x_mid = 0.5 * (x0 + x1)

            line_0 = np.array([x_mid, y0, 1.0])
            line_1 = np.array([x_mid, y1, 1.0])

            line_0 = self.transform_plot @ line_0
            line_1 = self.transform_plot @ line_1

            ctx.set_source_rgb(0, 0, 0)
            ctx.set_line_width(self.stick_line_width)
            ctx.move_to(*line_0[:2])
            ctx.line_to(*line_1[:2])
            ctx.stroke()

            w, h = x1 - x0, y3 - y2

            ctx.set_source_rgb(*c)

            candle_0 = self.transform_plot @ np.array([x_mid - 0.5 * self.candle_width_scale * w, y2, 1])
            candle_1 = self.transform_plot @ np.array([x_mid + 0.5 * self.candle_width_scale * w, y3, 1])
            candle_sc = candle_1 - candle_0

            ctx.rectangle(*candle_0[:2], *candle_sc[:2])
            ctx.fill_preserve()

            ctx.set_source_rgb(0, 0, 0)
            ctx.set_line_width(0.5)
            ctx.stroke()


class TickVolume(PlotSeries):

    def __init__(self, model: TickModel):
        super().__init__()

        self.model = model

        m = 20
        p = 10
        b = 0
        self.margins = (m,) * 4
        self.padding = (p,) * 4
        self.border = b
        self.grid_line_width = 0.5
        self.stick_line_width = 0.5
        self.candle_width_scale = 0.4
        self.x_axis_space = 30
        self.y_axis_space = 20

        self.background_color = (0, 0, 0, 0)
        self.border_color = (0.0, 0, 0, 1)

        self.font_size = 12
        self.font_face = 'InputSans'

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
                                         [0, -inner_scale.y, inner_pos.y + inner_scale.y],
                                         [0, 0, 1]])
        self.transform_plot = np.array([[inner_scale.x - self.x_axis_space, 0, inner_pos.x],
                                        [0, -inner_scale.y + self.y_axis_space,
                                            inner_pos.y + inner_scale.y - self.y_axis_space],
                                        [0, 0, 1]])

    def draw(self, ctx: cairo.Context):

        p0 = self.rect_inner.position
        s0 = self.rect_inner.scale

        if self.background_color[-1] > 0:
            ctx.set_source_rgba(*self.background_color)
            ctx.rectangle(*p0.xy, *s0.xy)
            ctx.fill()

        if self.border > 0 and self.border_color[-1] > 0:
            ctx.set_line_width(self.border)
            ctx.set_source_rgba(*self.border_color)
            ctx.rectangle(*p0.xy, *s0.xy)
            ctx.stroke()

        ctx.select_font_face(self.font_face, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(self.font_size)
        self.draw_volumes(ctx)

    def draw_volumes(self, ctx: cairo.Context):

        green = (92 / 256, 214 / 256, 92 / 256)
        red = (1, 102 / 256, 102 / 256)

        bars = self.model.bars_df

        ylim = (bars.volume.min(), bars.volume.max())

        axis_x_0 = self.transform_plot @ np.array([-0.03, -0.06, 1])
        axis_x_1 = self.transform_plot @ np.array([1.03, -0.06, 1])
        axis_y_0 = self.transform_plot @ np.array([1.03, 1, 1])

        ctx.set_line_width(self.grid_line_width)
        ctx.set_source_rgb(0, 0, 0)
        ctx.move_to(*axis_x_0[:2])
        ctx.line_to(*axis_x_1[:2])
        ctx.line_to(*axis_y_0[:2])
        ctx.stroke()

        ctx.set_font_size(10)
        x_ticks = [-0.5, ] + list(range(7))
        x_tick_labels = ['9:30', ] + list(f'{10+i}:00' for i in x_ticks[1:])
        for idx, tick in enumerate(x_ticks):

            grid_0 = self.transform_plot @ np.array([tick / 6.5 + 0.5 / 6.5, -0.06, 1])
            grid_1 = self.transform_plot @ np.array([tick / 6.5 + 0.5 / 6.5, -0.08, 1])

            ctx.set_line_width(self.grid_line_width)
            ctx.move_to(*grid_0[:2])
            ctx.line_to(*grid_1[:2])
            ctx.set_source_rgb(0, 0, 0)
            ctx.stroke()

            ctx.set_source_rgb(0, 0, 0)
            tick_label = x_tick_labels[idx]
            (x, y, w, h, dx, dy) = ctx.text_extents(tick_label)
            ctx.move_to(grid_0[0] - w / 2, grid_0[1] + h / 2 + 0.9 * self.y_axis_space)
            ctx.show_text(tick_label)

        y_tick_min = np.ceil(ylim[0]) + 0
        y_tick_max = np.ceil(ylim[1])

        num_y_ticks = 6
        tick_int = int((y_tick_max - y_tick_min) / num_y_ticks)

        y_ticks = list(y_tick_min + i * tick_int for i in range(num_y_ticks))
        y_tick_labels = list('{:.0f}'.format(i) for i in y_ticks)

        for idx in range(num_y_ticks):

            tick = y_ticks[idx]
            label = y_tick_labels[idx]
            grid_0 = self.transform_plot @ np.array([1.03, (tick - ylim[0]) / (ylim[1] - ylim[0]), 1])
            grid_1 = self.transform_plot @ np.array([1.04, (tick - ylim[0]) / (ylim[1] - ylim[0]), 1])

            ctx.move_to(*grid_0[:2])
            ctx.line_to(*grid_1[:2])
            ctx.stroke()

            (x, y, w, h, dx, dy) = ctx.text_extents(tick_label)
            ctx.move_to(grid_0[0] + w / 2 - 4, grid_0[1] + h / 2)
            ctx.show_text(label)

        for idx in range(len(bars)):

            x0 = bars.t_open.iloc[idx] / ((16 - 9.5) * 60 * 60)
            x1 = bars.t_close.iloc[idx] / ((16 - 9.5) * 60 * 60)

            h = bars.high.iloc[idx]
            l = bars.low.iloc[idx]
            o = bars.open.iloc[idx]
            c = bars.close.iloc[idx]
            v = bars.volume.iloc[idx]

            y0 = 0
            y1 = (v - ylim[0]) / (ylim[1] - ylim[0])

            if o < c:
                c = green
            else:
                c = red

            ctx.set_source_rgb(*c)

            x_mid = 0.5 * (x0 + x1)

            w, h = x1 - x0, y1 - y0

            ctx.set_source_rgb(*c)

            vol_bar_0 = self.transform_plot @ np.array([x_mid - 0.5 * self.candle_width_scale * w, y0, 1])
            vol_bar_1 = self.transform_plot @ np.array([x_mid + 0.5 * self.candle_width_scale * w, y1, 1])
            vol_bar_sc = vol_bar_1 - vol_bar_0

            ctx.rectangle(*vol_bar_0[:2], *vol_bar_sc[:2])
            ctx.fill_preserve()

            ctx.set_source_rgb(0, 0, 0)
            ctx.set_line_width(0.5)
            ctx.stroke()
