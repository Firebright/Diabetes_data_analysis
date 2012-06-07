# -*- coding: utf-8 -*-
"""
Created on Wed Jan 25 12:06:06 2012

@author: afdm76
"""
from matplotlib.pyplot import figure, show, hold, subplot, axes, plot_date, plot, hist, text, imshow,cm
import plottinglib
import matplotlib.dates as mdates
import numpy
from datetime import timedelta

def main_plot(bgstream, state_streams, combined_trace,
              bg_day_min, bg_day_max, bg_day_mean, bg_day_std,
              carb_dailys, bolus_dailys, event_num,event_recovery_mean,
              event_duration_mean,event_type, 
               event_duration, event_recovery):
    '''Generates the main overview plot.'''
    Fmt = mdates.DateFormatter('%d\n%b\n%Y')  
    fig7 = figure(7, figsize=(20,11))
    #years    = mdates.YearLocator()   # every year
    days = mdates.WeekdayLocator(byweekday=mdates.MO)
    #Fmt = mdates.DateFormatter('%DD%MMM')
    # Daily totals    
    ax1_loc = [0.05, 0.22, 0.4, 0.25]
    # main data plot    
    ax2_loc = [0.05, 0.65, 0.94, 0.3]
    #Stability plot    
    ax3_loc = [0.5, 0.06, 0.11, 0.19]
    # pie graph
    ax4_loc = [0.45, 0.29, 0.23, 0.23]
    # carbs plot    
    ax5_loc = [0.05, 0.07, 0.4, 0.15]
    # hypo durations hist
    ax6_loc = [0.8, 0.12, 0.19, 0.15]
    # hyper durations hist
    ax7_loc = [0.8, 0.30, 0.19, 0.15] 
    ax8_loc = [0.7, 0.12, 0.1, 0.33]
#    ax6_loc = [0.05, 0.05, 0.4, 0.15]
    fracs = plottinglib.calc_fractions(state_streams)
    # Main BG time series plot
    ax2 = axes(ax2_loc)
    hold(True)
    y_data =  combined_trace[1, :]
    x_dates = plottinglib.convert_to_dates(combined_trace[0, :])
    graph_x_lims = [x_dates[0], x_dates[-1]]
    # Marking the times for warning, low and high.
    wh_r = numpy.where(y_data < 3.7, True, False)
    wh_y = numpy.where(y_data <4.0, True, False)
    wh_b = numpy.where(y_data > 8.0, True, False)
#    imshow([[.6, .6],[.7,.7]], interpolation='bicubic', cmap=cm.copper,
#         extent=(graph_x_lims[0], graph_x_lims[1], min(y_data), max(y_data)), alpha=1)
    # TODO replace the hard coded numbers with the limits passsed in.
    ax2.plot_date(x_dates, numpy.ones_like(y_data) * 3.7, fmt = ':r', marker = None)
    ax2.plot_date(x_dates, numpy.ones_like(y_data) * 8.0, fmt = ':b', marker = None)
    # Plot the data
    ax2.plot_date(x_dates, y_data, fmt = 'k-', marker = None)
    # Fill under the curve for each condition (warn, low,high).    
    lim_vec = numpy.ones((combined_trace.shape[1]))
    ax2.fill_between(x_dates, y_data, lim_vec*4.0 , where=wh_y, facecolor='yellow')
    ax2.fill_between(x_dates, y_data, lim_vec*3.7, where=wh_r, facecolor='red')    
    ax2.fill_between(x_dates, y_data, lim_vec*8.0, where=wh_b, facecolor='blue')     
    ax2.set_xlim(graph_x_lims[0], graph_x_lims[1])
    hold(False)
    ax2.set_ylabel('Blood Glucose (mg/mmol)')
    ax2.set_title('Blood glucose over time')
    ax2.set_xlabel('Time')
    ax2.xaxis.set_major_formatter(Fmt)
    ax2.xaxis.set_major_locator(days)    
    # Plot of daily means, mins and maxes    
    ax1 = axes(ax1_loc)
    hold(True)
    ax1.plot_date(plottinglib.convert_to_dates(bg_day_min[0, :]), bg_day_min[1, :], '.r')
    ax1.plot_date(plottinglib.convert_to_dates(bg_day_max[0, :]), bg_day_max[1, :], '.b')
    ax1.plot_date(plottinglib.convert_to_dates(bg_day_mean[0, :]), bg_day_mean[1, :], 'k.')
    ax1.plot_date(plottinglib.convert_to_dates(bg_day_mean[0, :]), bg_day_mean[1, :], ':k')
    ax1.plot_date(plottinglib.convert_to_dates(bg_day_mean[0, :]), numpy.ones_like(bg_day_mean[1, :]) * 3.7, ':r')
    ax1.plot_date(plottinglib.convert_to_dates(bg_day_mean[0, :]), numpy.ones_like(bg_day_mean[1, :]) * 8.0, ':b')
    hold(False)    
    ax1.set_ylabel('Blood Glucose (mg/mmol)')
    ax1.set_title('Daily values')
    ax1.xaxis.set_major_formatter(Fmt)
    ax1.xaxis.set_major_locator(days)
    ax1.set_xlim(graph_x_lims[0], graph_x_lims[1])
    # Metabolic stability graph
    stability_plot(ax3_loc,bg_day_mean, bg_day_std)
    # Pie chart of time spent in each state
    ax4 = axes(ax4_loc)
    ax4.set_aspect(1)
    plottinglib.light_filter_pie(ax4, fracs)
    ax4.set_title('Fraction of time in each state')
    # Plot of total daily carbs
    ax5 = axes(ax5_loc)
    ax5.plot_date(plottinglib.convert_to_dates(carb_dailys[0,:]),carb_dailys[1,:],':b')
    ax5.set_ylabel('Carbs (g)')
    ax5.set_xlabel('Time')
    ax5.set_xlim(graph_x_lims[0], graph_x_lims[1])
    ax5.xaxis.set_major_formatter(Fmt)
    ax5.xaxis.set_major_locator(days)
    event_plot(ax6_loc, ax7_loc, ax8_loc, event_num,event_recovery_mean,event_duration_mean,event_type, 
               event_duration, event_recovery)
    # Plot of ratio of Basal to Bolus TODO    
#    ax6 = axes(ax6_loc)
#    ax6.bar(plottinglib.convert_to_dates(bolus_dailys[0,:]),bolus_dailys[1,:])
#    ax6.set_ylabel('Ratio')
#    ax6.set_xlabel('Time')
#    ax6.set_xlim(graph_x_lims[0], graph_x_lims[1])
#    ax6.xaxis.set_major_formatter(Fmt)
#    ax6.xaxis.set_major_locator(days)
def event_plot(ax6_loc, ax7_loc, ax8_loc, event_num,event_recovery_mean,event_duration_mean,event_type, 
               event_duration, event_recovery):
    '''Generates the main overview plot.'''
   # fig8 = figure(8, figsize=(16,10))
    #ax6_loc = [0.05, 0.05, 0.9, 0.4]
    #ax7_loc = [0.05, 0.55, 0.9, 0.4]  
    print event_num
    ax6 = axes(ax6_loc)
    hold(True)
    ax7 = axes(ax7_loc)
    hold(True)
    # the histogram of the data
    low_duration = event_duration[0][1]
    warn_duration = event_duration[1][1]
    high1_duration = event_duration[2][1]
    high2_duration = event_duration[3][1]
    high3_duration = event_duration[4][1]
    hypo_duration = event_duration[5][1]    
    hyper_duration = event_duration[6][1]
    n, bins, patches = ax7.hist([high1_duration, high2_duration, high3_duration],
                                numpy.ceil(max(hyper_duration)),  
                                normed=0, color=['MediumBlue', 'MidnightBlue', 'Navy'], 
                                alpha=1, histtype='barstacked')
    n, bins, patches = ax6.hist([warn_duration,low_duration], 
                                numpy.ceil(max(hypo_duration)), 
                                normed=0, color=['yellow', 'red'], 
                                alpha=1, histtype='barstacked')
    ax6.set_xlabel('Duration (hrs)')
    ax6.set_ylabel('Num events')
    ax8 = axes(ax8_loc)
    hold(True)
    col3 = 0.7
    textbox(col3, 0.55, dec_time_to_str(numpy.mean(event_recovery[5][1])),"left")
    textbox(col3, 0.6, dec_time_to_str(numpy.mean(event_recovery[0][1])),"left")
    textbox(col3, 0.65, dec_time_to_str(numpy.mean(event_recovery[1][1])),"left")
#    textbox(col3, 0.4, '')
    textbox(col3, 0.75, dec_time_to_str(numpy.mean(event_recovery[6][1])),"left")
    textbox(col3, 0.8, dec_time_to_str(numpy.mean(event_recovery[2][1])),"left")
    textbox(col3, 0.85, dec_time_to_str(numpy.mean(event_recovery[3][1])),"left")
    textbox(col3, 0.9, dec_time_to_str(numpy.mean(event_recovery[4][1])),"left")
    textbox(col3, 0.95, 'time',"left")
    textbox(col3, 1, 'Recovery',"left")
    col2 = 0.3
    textbox(col2, 0.55, dec_time_to_str(numpy.mean(event_duration[5][1])),"left")
    textbox(col2, 0.6, dec_time_to_str(numpy.mean(event_duration[0][1])),"left")
    textbox(col2, 0.65, dec_time_to_str(numpy.mean(event_duration[1][1])),"left")
#    textbox(col2, 0.4, '')
    textbox(col2, 0.75, dec_time_to_str(numpy.mean(event_duration[6][1])),"left")  
    textbox(col2, 0.8, dec_time_to_str(numpy.mean(event_duration[2][1])),"left")
    textbox(col2, 0.85, dec_time_to_str(numpy.mean(event_duration[3][1])),"left")
    textbox(col2, 0.9, dec_time_to_str(numpy.mean(event_duration[4][1])),"left")
    textbox(col2, 0.95, 'Duration',"left")
    textbox(col2, 1, 'Event',"left")
    col1 = 0.1
    textbox(col1, 0.55, len(event_recovery[5][1]),"left")
    textbox(col1, 0.6, len(event_recovery[0][1]),"left")
    textbox(col1, 0.65, len(event_recovery[1][1]),"left")
#    textbox(col1, 0.4, '')
    textbox(col1, 0.75, len(event_recovery[6][1]),"left")
    textbox(col1, 0.8, len(event_recovery[2][1]),"left")
    textbox(col1, 0.85, len(event_recovery[3][1]),"left")
    textbox(col1, 0.9, len(event_recovery[4][1]),"left")
    textbox(col1, 0.95, 'of events',"right")
    textbox(col1, 1, 'Number',"right")
    col0 = 0
    textbox(col0, 0.55, 'Total hypo',"right")
    textbox(col0, 0.6, 'Low',"right")
    textbox(col0, 0.65, 'Warning',"right")
    textbox(col0, 0.7, 'OK',"right")
    textbox(col0, 0.75, 'Total high',"right")
    textbox(col0, 0.8, 'High1',"right")
    textbox(col0, 0.85, 'High2',"right")
    textbox(col0, 0.9, 'High3',"right")
    hold(False)
    #ax.set_xlim(40, 160)
    #ax.set_ylim(0, 0.03)

def textbox(x, y, val, align):
       text(x, y, val, size=10, rotation=0.,
         ha=align, va="bottom",
         bbox = dict(ec=(1., 0.5, 0.5),
                     fc=(1., 0.8, 0.8),
                     )
         )
         
def dec_time_to_str(val):
    '''Takes a duration in decimal hours an outputs a string in terms 
    of hours and minutes.'''
    hours, frac_hours = divmod(val, 1)
    minutes, frac_mins = divmod(frac_hours * 60, 1)
    hours = str(int(hours))
    minutes = str(int(minutes))
    if hours > 1 and minutes > 1:
        output = ''.join([hours,'h',minutes,'mins'])
    elif hours > 1 and minutes < 1:
        output = ''.join([hours,'h'])
    elif hours < 1 and minutes > 1:
        output  = ''.join([minutes,'mins'])
    else:
        output = ''
    return output
         
def stability_plot(ax3_loc,bg_day_mean, bg_day_std):
    ax3 = axes(ax3_loc)
    ax3.set_aspect('equal', 'datalim')
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