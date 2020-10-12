from typing import List, Union, Tuple

from figure import Figure
from axes import Axes
from ohlcv import TickVolume, TickCandles
import model


def subplots(num_rows: int, num_cols: int):
    fig = Figure()

    axes = list()
    for i in range(num_rows):

        axes.append(list())

        for j in range(num_cols):

            ax = Axes()
            axes[-1].append(ax)

    fig.axes = axes

    if num_cols == 1 and num_rows == 1:
        return fig, axes[0][0]

    elif num_rows == 1:
        return fig, axes[0]

    elif num_cols == 1:
        return fig, list(a[0] for a in axes)

    return fig, axes


def ohlcv_plot(model: model.TickModel):

    fig, axes = subplots(2, 1)
    axes[0].plot_series.append(TickCandles(model))
    axes[1].plot_series.append(TickVolume(model))

    fig.set_title(f'{model.contract} {model.date}')

    fig.layout()
    fig.draw()

    return fig, axes

#    print(buff.getvalue().decode('utf-8'))
