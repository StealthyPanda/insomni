from bokeh.plotting import figure, show, Figure
from bokeh.models import ColumnDataSource
from typing import Iterable
import numpy as np
import streamlit as st


@st.cache_resource
def histogramnormal(data : Iterable, label : str = '', fig : Figure = None) -> Figure:
    freqs = dict()
    for each in data:
        if each in freqs : freqs[each] += 1
        else : freqs[each] = 1
    
    keys = list(freqs.keys())
    keys.sort(key = lambda x: freqs[x], reverse = True)
    vals = [freqs[k] for k in keys]
    keys = list(map(lambda x:str(x), keys))

    hsource = ColumnDataSource({
        'x' : keys,
        'y' : vals
    })

    plot = figure(x_range = keys) if fig is None else fig
    plot.xaxis.major_label_orientation = 0.8

    plot.vbar(
        source = hsource,
        x = 'x',
        top = 'y',
        width = 0.8,
        alpha = 0.7,
        legend_label = label
    )

    plot.line(
        source = hsource,
        x = 'x',
        y = 'y',
        width = 2,
        legend_label = label
    )

    plot.circle(
        source = hsource,
        x = 'x',
        y = 'y',
        radius = 0.05,
        alpha = 0.8,
        legend_label = label
    )

    return plot

@st.cache_resource
def histogramdistribution(data : Iterable, nbins : int = 2, label : str = '', fig : Figure = None) -> Figure:
    freqs = dict()
    for each in data:
        if each in freqs : freqs[each] += 1
        else : freqs[each] = 1
    keys = list(freqs.keys())
    keys.sort(key = lambda x: freqs[x])

    intervals = np.linspace(min(keys), max(keys), nbins + 1)

    size = abs(intervals[1] - intervals[0])

    j = 0
    skeys = sorted(keys)
    

    heights = [0 for _ in range(len(intervals) - 1)]
    mids = []

    for i, each in enumerate(intervals):
        left = each
        if i == (len(intervals) - 1):
            right = left
            i = len(heights) - 1
        else:
            right = intervals[i + 1]
            mids.append((left + right)/2)

        
        while j < len(skeys):
            if (left <= skeys[j]) and ((skeys[j] < right) or (i == (len(heights) - 1))):
                heights[i] += freqs[skeys[j]]
                j += 1
            else: break
    
    
    
    dsource = ColumnDataSource({
        'x' : mids,
        'y' : heights
    })


    plot = figure() if fig is None else fig
    # plot.x_range.bounds = (intervals[0], intervals[-1])
    

    plot.vbar(
        source = dsource,
        x = 'x',
        top = 'y',
        width = 0.8 * size,
        alpha = 0.7,
        legend_label = label
    )

    plot.line(
        source = dsource,
        x = 'x',
        y = 'y',
        width = 2,
        legend_label = label
    )

    plot.circle(
        source = dsource,
        x = 'x',
        y = 'y',
        radius = 0.05,
        alpha = 0.8,
        legend_label = label
    )
    
    return plot
