# -*- coding: utf-8 -*-
"""
Created on Mon Sep 12 23:00:06 2011

@author: -
"""
from matplotlib.artist import Artist
from matplotlib.colors import LightSource
import numpy
from scipy import  zeros
from datetime import datetime

def convert_to_dates(data):
    '''Take and array of integers representing date ordinals 
       andconverts them into a list of datetime objects.'''    
    out = []
    for js in range(len(data)):
        out.append(datetime.fromtimestamp(data[js]))
    return out
    
def smooth1d(x, window_len):
    # copied from http://www.scipy.org/Cookbook/SignalSmooth

    s= numpy.r_[2*x[0]-x[window_len:1:-1],x,2*x[-1]-x[-1:-window_len:-1]]
    w = numpy.hanning(window_len)
    y= numpy.convolve(w/w.sum(),s,mode='same')
    return y[window_len-1:-window_len+1]

def smooth2d(A, sigma=3):

    window_len = max(int(sigma), 3)*2+1
    A1 = numpy.array([smooth1d(x, window_len) for x in numpy.asarray(A)])
    A2 = numpy.transpose(A1)
    A3 = numpy.array([smooth1d(x, window_len) for x in A2])
    A4 = numpy.transpose(A3)

    return A4


class BaseFilter(object):
    def prepare_image(self, src_image, dpi, pad):
        ny, nx, depth = src_image.shape
        #tgt_image = np.zeros([pad*2+ny, pad*2+nx, depth], dtype="d")
        padded_src = zeros([pad*2+ny, pad*2+nx, depth], dtype="d")
        padded_src[pad:-pad, pad:-pad,:] = src_image[:,:,:]

        return padded_src#, tgt_image

    def get_pad(self, dpi):
        return 0

    def __call__(self, im, dpi):
        pad = self.get_pad(dpi)
        padded_src = self.prepare_image(im, dpi, pad)
        tgt_image = self.process_image(padded_src, dpi)
        return tgt_image, -pad, -pad

class GaussianFilter(BaseFilter):
    "simple gauss filter"
    def __init__(self, sigma, alpha=0.5, color=None):
        self.sigma = sigma
        self.alpha = alpha
        if color is None:
            self.color=(0, 0, 0)
        else:
            self.color=color

    def get_pad(self, dpi):
        return int(self.sigma*3/72.*dpi)

    def process_image(self, padded_src, dpi):
        #offsetx, offsety = int(self.offsets[0]), int(self.offsets[1])
        tgt_image = numpy.zeros_like(padded_src)
        aa = smooth2d(padded_src[:,:,-1]*self.alpha,
                      self.sigma/72.*dpi)
        tgt_image[:,:,-1] = aa
        tgt_image[:,:,:-1] = self.color
        return tgt_image

class LightFilter(BaseFilter):
    "simple gauss filter"
    def __init__(self, sigma, fraction=0.5):
        self.gauss_filter = GaussianFilter(sigma, alpha=1)
        self.light_source = LightSource()
        self.fraction = fraction
        #hsv_min_val=0.5,hsv_max_val=0.9,
        #                                hsv_min_sat=0.1,hsv_max_sat=0.1)
    def get_pad(self, dpi):
        return self.gauss_filter.get_pad(dpi)

    def process_image(self, padded_src, dpi):
        t1 = self.gauss_filter.process_image(padded_src, dpi)
        elevation = t1[:,:,3]
        rgb = padded_src[:,:,:3]

        rgb2 = self.light_source.shade_rgb(rgb, elevation,
                                           fraction=self.fraction)

        tgt = numpy.empty_like(padded_src)
        tgt[:,:,:3] = rgb2
        tgt[:,:,3] = padded_src[:,:,3]

        return tgt

class OffsetFilter(BaseFilter):
    def __init__(self, offsets=None):
        if offsets is None:
            self.offsets = (0, 0)
        else:
            self.offsets = offsets

    def get_pad(self, dpi):
        return int(max(*self.offsets)/72.*dpi)

    def process_image(self, padded_src, dpi):
        ox, oy = self.offsets
        a1 = numpy.roll(padded_src, int(ox/72.*dpi), axis=1)
        a2 = numpy.roll(a1, -int(oy/72.*dpi), axis=0)
        return a2

class DropShadowFilter(BaseFilter):
    def __init__(self, sigma, alpha=0.3, color=None, offsets=None):
        self.gauss_filter = GaussianFilter(sigma, alpha, color)
        self.offset_filter = OffsetFilter(offsets)

    def get_pad(self, dpi):
        return max(self.gauss_filter.get_pad(dpi),
                   self.offset_filter.get_pad(dpi))

    def process_image(self, padded_src, dpi):
        t1 = self.gauss_filter.process_image(padded_src, dpi)
        t2 = self.offset_filter.process_image(t1, dpi)
        return t2

class FilteredArtistList(Artist):
    """
    A simple container to draw filtered artist.
    """
    def __init__(self, artist_list, filter):
        self._artist_list = artist_list
        self._filter = filter
        Artist.__init__(self)

    def draw(self, renderer):
        renderer.start_rasterizing()
        renderer.start_filter()
        for a in self._artist_list:
            a.draw(renderer)
        renderer.stop_filter(self._filter)
        renderer.stop_rasterizing()


def light_filter_pie(ax, fracs):
    '''Generates a pie chart of the fractional time spend in each state'''
    fracs[3] = fracs[3] + fracs[4] +fracs[5]
    fracs = fracs[:4]
    explode = (0, 0, 0.05, 0)
    labels = 'Low', 'Warn', 'OK', 'High'
    colors = ('red', 'yellow', 'green','blue')
    pies = ax.pie(fracs, explode=explode, labels=labels, 
                  colors = colors, autopct = '%.1f')
    ax.patch.set_visible(True)

    light_filter = LightFilter(9)
    for p in pies[0]:
        p.set_agg_filter(light_filter)
        p.set_rasterized(True) # to support mixed-mode renderers
        p.set(ec="none",
              lw=2)

    gauss = DropShadowFilter(9, offsets=(3,4), alpha=0.7)
    shadow = FilteredArtistList(pies[0], gauss)
    ax.add_artist(shadow)
    shadow.set_zorder(pies[0][0].get_zorder()-0.1)

    
def calc_fractions(data):
    '''Calculating the fraction of samples in each state.'''
    # total is hypo + OK + hyper states
    total_samples = len(data[6][0]) + len(data[2][0]) + len(data[7][0]) 
    frac_high3 = len(data[5][0]) *100. / total_samples
    frac_high2 = len(data[4][0]) *100. / total_samples
    frac_high1 = len(data[3][0]) *100. / total_samples
    frac_ok    = len(data[2][0]) *100. / total_samples
    frac_warn  = len(data[1][0]) *100. / total_samples
    frac_low   = len(data[0][0]) *100. / total_samples
    return [frac_low, frac_warn, frac_ok, frac_high1, frac_high2, frac_high3]