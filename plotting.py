# -*- coding: utf-8 -*-
"""
Created on Wed Jan 25 12:06:06 2012

@author: afdm76
"""
from matplotlib.pyplot import figure, show, hold, subplot, axes
import plottinglib
import numpy

def main_plot(bgstream, state_streams, combined_trace,
              bg_day_min, bg_day_max, bg_day_mean, bg_day_std):
    '''Generates the main overview plot.'''
    figure(7)
    fracs = plottinglib.calc_fractions(state_streams)
    ax1 = subplot(221)
    #ax1 = axes([0.1, 0.5, 0.4, 0.45])
    ax1.plot(bg_day_min[0, :], bg_day_min[1, :], 'r')
    ax1.plot(bg_day_max[0, :], bg_day_max[1, :], 'b')
    ax1.plot(bg_day_mean[0, :], bg_day_mean[1, :], 'k.')
    ax1.set_ylabel('Blood Glucose (mg/mmol)')
    ax1.set_title('Daily values')
    ax2 = subplot(222)
    hold(True)
    ax2.plot(combined_trace[0, :], combined_trace[1, :], 'k:')
    ax2.fill_between(combined_trace[0, :], combined_trace[1, :], y2=4.0, facecolor='yellow')
    ax2.fill_between(combined_trace[0, :], combined_trace[1, :], y2=3.7, facecolor='red')    
#    ax2.fill_between(st2[0], st2[1], 8.0, facecolor='blue') 
    ax2.set_xlim(combined_trace[0, 0], combined_trace[0, -1])
    hold(False)
    ax2.set_ylabel('Blood Glucose (mg/mmol)')
    ax2.set_title('Blood glucose over time')
    ax2.set_xlabel('Time')
    ax3 = subplot(223)
    data_len = bg_day_mean.shape[1]
    hold(True)
    for  ihp in range(data_len):
        col_val = ((data_len - (ihp-1))/data_len) * 0.6 + 0.4
        sze = numpy.floor(((data_len - ihp)/data_len) * 7) + 3
        ax3.plot(bg_day_std[1, ihp], bg_day_mean[1, ihp], 'o', \
        markersize=sze,\
        markeredgecolor= ((col_val, col_val, 1)), \
        markerfacecolor= ((col_val, col_val, 1)))
    ax3.plot([0, 14], [4, 4], 'r', [0, 14], [8, 8], 'b', \
             [2.8, 2.8], [0, 14], ':k')
    hold(False)    
    ax3.set_ylabel('Standard deviation')
    ax3.set_xlabel('Mean')
    ax3.set_title('Stability')
    ax4 = subplot(224)
    ax4.set_aspect(1)
    plottinglib.light_filter_pie(ax4, fracs)
    ax4.set_title('Fraction of time in each state')
    
def spare_plot(bgstream, basalstream, bolusstream):
    '''TEMP.'''
    figure(8)
    ax5 = subplot(221)
    num, bins, patches = ax5.hist(bgstream[1], 50, normed=1, \
    facecolor='green', alpha=0.75)
#    bincenters = 0.5*(bins[1:]+bins[:-1])
    ax5.set_xlabel('bg TEST')
    ax5.set_ylabel('Number of events')
    ax6 = subplot(222)
    num, bins, patches = ax6.hist(bolusstream[1], 50, normed=1, \
    facecolor='green', alpha=0.75)
#    bincenters = 0.5*(bins[1:]+bins[:-1])
    ax6.set_xlabel('bolus TEST')
    ax6.set_ylabel('Number of events')
    ax7 = subplot(223)
    num, bins, patches = ax7.hist(basalstream[1], 50, normed=1, \
    facecolor='green', alpha=0.75)
#    bincenters = 0.5*(bins[1:]+bins[:-1])
    ax7.set_xlabel('basal TEST')
    ax7.set_ylabel('Number of events')
  
def comp_plot(bgstream, combined_trace, CGMstream):
    '''Generates a plot to show how the traces are combined.'''
    figure(9)
    ax1 = axes([0.05, 0.05, 0.9, 0.9])
    hold(True)
    ax1.plot(bgstream[0, :], bgstream[1, :], 'r')
    ax1.plot(CGMstream[0, :], CGMstream[1, :], 'b')
    ax1.plot(combined_trace[0, :], combined_trace[1, :], 'k')
    ax1.set_ylabel('Blood Glucose (mg/mmol)')
    ax1.set_title('Time')
#    figure(5)
#    plot(basal_dailys[0], basal_dailys[1])
#    plot(bolus_dailys[0], bolus_dailys[1])
#    plot(carb_dailys[0], carb_dailys[1])
#    figure(6)  
#ax.set_title(r'$\mathrm{Histogram\ of\ IQ:}\ \mu=100,\ \sigma=15$')
#    ax.set_xlim(40, 160)
#    ax.set_ylim(0, 0.03)
#    ax.grid(True)
    
#    pie(fracs)
#    figure(3)
#    plot(basalstream[0], basalstream[1])
#    plot(basal_trace[0], array(basal_trace[1])*60.)
#    figure(4)
#    plot(bgstream[0], bgstream[1])
#    plot(bg_trace[0], bg_trace[1])
#    figure(1)
#    plot(bolusstream[0], bolusstream[1])
#    plot(basalstream[0], basalstream[1])
#    plot(basaladjustream[0], basaladjustream[1])
#    plot(basaladjlstream[0], basaladjlstream[1])
#    plot(bgstream[0], bgstream[1])
#    plot(carbstream[0], carbstream[1])
#    figure(2)
#    plot(bg_trace[0], hi_lim_val)
#    plot(bg_trace[0], tm_lst_carbs)
#    plot(bg_trace[0], tm_nxt_carbs)
#    plot(bg_trace[0], tm_lst_bolus)
#    if tm_lst_hypo != None:
#        plot(bg_trace[0], tm_lst_hypo)
#    plot(bg_trace[0], pre_meal_flg)
#    plot(bg_trace[0], post_meal_flg)
#    print len(bg_trace[0]), len(state)
#    plot(bg_trace[0], state)
#    plot(bg_trace[0], val_lst_bolus)
#    legend(('hi_lim_val', 'tm_lst_carbs', 'tm_nxt_carbs', 'tm_lst_bolus',
#            'tm_lst_hypo', 'pre_meal_flg', 'post_meal_flg',
#            'state', 'val_lst_bolus'))
    show()
    #x = raw_input("Press Enter")
    #print 'Done'