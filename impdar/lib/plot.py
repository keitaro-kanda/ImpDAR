#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2019 David Lilien <dlilien90@gmail.com>
#
# Distributed under terms of the GNU GPL3.0 license.

"""

"""
import os.path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.widgets import Slider
from .load import load


def plot(fn, tr=None, gssi=False, pe=False, s=False, ftype='png', dpi=300, xd=False, yd=False, x_range=(0, -1), power=None, *args, **kwargs):
    """We have an overarching function here to handle a number of plot types

    Parameters
    ----------
    fn: list of strs
        A list of filenames to plot individually.
    tr: tuple or int, optional
        Plot traces tr[1] to tr[2] (or trace tr) rather than the radargram. Default is None (plot radargram)
    power: int, optional
        If not None, then plot power returned from this layer
    gssi: bool, optional
        If True, fns are .DZT files
    pe: bool, optional
        If True, fns are Pulse Ekko files
    x_range: tuple, optional
        The range of traces to plot in the radargram. Default is (0, -1) (plot all traces)
    """
    if gssi and pe:
        raise ValueError('Input cannot be both pulse-ekko and gssi')
    if gssi:
        radar_data = load('gssi', fn)
    elif pe:
        radar_data = load('pe', fn)
    else:
        radar_data = load('mat', fn)

    if xd:
        xdat = 'dist'
    else:
        xdat = 'tnum'
    if yd:
        ydat = 'depth'
    else:
        ydat = 'twtt'

    if (tr is not None) and (power is not None):
        raise ValueError('Cannot do both tr and power. Pick one')

    if tr is not None:
        figs = [plot_traces(dat, tr, ydat=ydat) for dat in radar_data]
    elif power is not None:
        figs = [plot_power(dat, power) for dat in radar_data]
    else:
        figs = [plot_radargram(dat, xdat=xdat, ydat=ydat, x_range=None) for dat in radar_data]

    if s:
        [f[0].savefig(os.path.splitext(fn0)[0] + '.' + ftype, dpi=dpi) for f, fn0 in zip(figs, fn)]
    else:
        plt.tight_layout()
        plt.show()


def plot_radargram(dat, xdat='tnum', ydat='twtt', x_range=(0, -1), cmap=plt.cm.gray, fig=None, ax=None, return_plotinfo=False):
    """This is the function to plot the normal radargrams that we are used to.

    This function is a little weird since I want to be able to plot on top of existing figures/axes or on new figures an axes. There is therefore an argument `return_plotinfo` that funnels between these options and changes the return types

    Parameters
    ----------
    dat: impdar.lib.RadarData.Radardata
        The RadarData object to plot.
    xdat: str, optional
        The horizontal axis units. Either tnum or distance.
    ydat: str, optional
        The vertical axis units. Either twtt or or depth. Default twtt.
    x_range: 2-tuple, optional
        The range of values to plot. Default is plot everything (0, -1)
    cmap: matplotlib.pyplot.cm, optional
        The colormap to use
    fig: matplotlib.pyplot.Figure
        Figure canvas that should be plotted upon
    ax: matplotlib.pyplot.Axes
        Axes that should be plotted upon


    Returns
    -------
    If not return_plotinfo

        fig: matplotlib.pyplot.Figure
            Figure canvas that was plotted upon
        ax: matplotlib.pyplot.Axes
            Axes that were plotted upon

    else
        im: pyplot.imshow
            The image object plotted
        xd: np.ndarray
            The x values of the plot
        yd: np.ndarray
            The y values of the plot
        x_range: 2-tuple
            The limits of the x range, after modification to remove negative indices
        clims: 2-tuple
            The limits of the colorbar

    """
    if xdat not in ['tnum', 'dist']:
        raise ValueError('x axis choices are tnum or dist')
    if ydat not in ['twtt', 'depth']:
        raise ValueError('y axis choices are twtt or depth')

    if x_range is None:
        x_range = (0, -1)
    if x_range[-1] == -1:
        x_range = (x_range[0], dat.tnum)

    lims = np.percentile(dat.data[:, x_range[0]:x_range[-1]][~np.isnan(dat.data[:, x_range[0]:x_range[-1]])], (10, 90))
    clims = [lims[0] * 2 if lims[0] < 0 else lims[0] / 2, lims[1] * 2]

    if fig is not None:
        if ax is None:
            ax = plt.gca()
    else:
        fig, ax = plt.subplots(figsize=(12, 8))

    if hasattr(dat.flags, 'elev') and dat.flags.elev:
        yd = dat.elevation
        ax.set_ylabel('Elevation (m)')
    else:
        ax.invert_yaxis()
        if ydat == 'twtt':
            yd = dat.travel_time
            ax.set_ylabel('Two way travel time (usec)')
        elif ydat == 'depth':
            if dat.nmo_depth is not None:
                yd = dat.nmo_depth
            else:
                yd = dat.travel_time / 2.0 * 1.69e8 * 1.0e-6
            ax.set_ylabel('Depth (m)')

    if xdat == 'tnum':
        xd = np.arange(int(dat.tnum))[x_range[0]:x_range[-1]]
        ax.set_xlabel('Trace number')
    elif xdat == 'dist':
        xd = dat.dist[x_range[0]:x_range[-1]]
        ax.set_xlabel('Distance (km)')

    if hasattr(dat.flags, 'elev') and dat.flags.elev:
        im = ax.imshow(dat.data[:, x_range[0]:x_range[-1]], cmap=cmap, vmin=lims[0], vmax=lims[1], extent=[np.min(xd), np.max(xd), np.min(yd), np.max(yd)], aspect='auto')
    else:
        im = ax.imshow(dat.data[:, x_range[0]:x_range[-1]], cmap=cmap, vmin=lims[0], vmax=lims[1], extent=[np.min(xd), np.max(xd), np.max(yd), np.min(yd)], aspect='auto')
    if not return_plotinfo:
        return fig, ax
    else:
        return im, xd, yd, x_range, clims


def plot_traces(dat, tr, ydat='twtt'):
    """Plot power vs depth or twtt in a trace

    Parameters
    ----------
    dat: impdar.lib.RadarData.Radardata
        The RadarData object to plot.
    tr: int or 2-tuple
        Either a single trace or a range of traces to plot
    ydat: str, optional
        The vertical axis units. Either twtt or or depth. Default twtt.

    Returns
    -------
    fig: matplotlib.pyplot.Figure
        Figure canvas that was plotted upon
    ax: matplotlib.pyplot.Axes
        Axes that were plotted upon
    """
    #Two options of trace input, a single trace or multiple
    if hasattr(tr, '__iter__'):
        if not len(tr) == 2:
            raise ValueError('tr must either be a 2-tuple of bounds for the traces or a single trace index')
    if type(tr) == int:
        tr = (tr, tr + 1)
    elif tr[0] == tr[1]:
        tr = (tr[0], tr[0] + 1)

    if ydat not in ['twtt', 'depth']:
        raise ValueError('y axis choices are twtt or depth')
    fig, ax = plt.subplots(figsize=(8, 12))
    lims = np.percentile(dat.data[:, tr[0]:tr[1]], (1, 99))
    ax.invert_yaxis()

    if ydat == 'twtt':
        yd = dat.travel_time
        ax.set_ylabel('Two way travel time (usec)')
    elif ydat == 'depth':
        if dat.nmo_depth is None:
            yd = dat.travel_time / 2.0 * 1.69e8 * 1.0e-6
        else:
            yd = dat.nmo_depth
        ax.set_ylabel('Depth (m)')

    for j in range(*tr):
        ax.plot(dat.data[:, j], yd)

    if lims[0] < 0 and lims[1] > 0:
        ax.set_xlim(lims[0], -lims[0])
    else:
        ax.set_xlim(*lims)
    ax.set_xlabel('Power')
    return fig, ax


def plot_power(dat, idx):
    """Make a plot of the reflected power along a given pick
    

    Parameters
    ----------
    dat: impdar.lib.RadarData.Radardata
        The RadarData object to plot.
    idx: int
        A picknum in the dat.picks.picknum array

    Returns
    -------
    fig: matplotlib.pyplot.Figure
        Figure canvas that was plotted upon
    ax: matplotlib.pyplot.Axes
        Axes that were plotted upon
    """
    #check to see if user entered an integer pick number
    try:
        idx = int(idx)
    except TypeError:
        raise TypeError('Please enter an integer pick number')

    if (dat.picks is None) or (dat.picks.picknums is None):
        raise ValueError('There are no picks on this radardata, cannot plot return power')

    if idx not in dat.picks.picknums:
        raise ValueError('Pick number {:d} not found in your file'.format(idx))

    fig, ax = plt.subplots(figsize=(8, 12))
    c = 10 * np.log10(dat.picks.power[dat.picks.picknums.index(idx)])
    clims = np.percentile(c, (1, 99))

    # I think we throw an error if vmin=vmax, but we still want a plot of constant power
    if (clims[0] - clims[1]) / clims[0] < 1.0e-8:
        clims[0] = 0.99 * clims[0]
        clims[1] = 1.01 * clims[1]

    img = ax.scatter(dat.long, dat.lat, c=c.flatten(), vmin=clims[0], vmax=clims[1])
    h = fig.colorbar(img)
    ax.set_ylabel('dB')

    return fig, ax
