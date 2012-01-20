# -*- coding: utf-8 -*-
"""
Created on Tue Aug 23 15:57:57 2011

@author: afdm76
"""
import numpy
#from matplotlib.dates import date2num, num2date
from matplotlib.pyplot import figure, plot, show, hold, legend, subplot, axes
from plottinglib import light_filter_pie
from xls_import import import_module_xls
from cgm_import import get_CGM_data
import datetime

def add_pre_meal_flag(tm_nxt_carbs):
    '''Generating a vector of 0's and 1's to designate if the current bg
    data point is within 1/2 hour of carbs being eaten.
    0 = no, 1 = yes.'''
    pre_meal_flg = []
    for ruh in range(len(tm_nxt_carbs)):       
        if tm_nxt_carbs[ruh] < 60*30:
            # BG reading is taken within 1/2 hour before the next lot of carbs.
            # Therefore classed as pre-meal.
            pre_meal_flg.append(1)
        else:
            pre_meal_flg.append(0)
    return pre_meal_flg

def add_post_meal_flag(tm_lst_carbs):
    '''Generating a vector of 0's and 1's to designate if the current bg
    data point is within 1 hour of carbs having been eaten.
    0 = no, 1 = yes.'''
    post_meal_flg = []
    for ruh in range(len(tm_lst_carbs)):   
        if tm_lst_carbs[ruh] < 60*60:
            # BG reading is taken within 1 hour of the last lot of carbs.
            # therefore classed as post-meal.
            post_meal_flg.append(1)
        else:
            post_meal_flg.append(0)
    return post_meal_flg

def find_time_next_carbs(bg_data, carbs_data):
    '''Finds how long until the next carbs for each bg data point.'''
    tm_nxt_carbs = []
    for ruh in range(len(bg_data[0])):    
        # find the index of the last meal
        next_carb_ind = numpy.nonzero(carbs_data[0] > bg_data[0][ruh])
        if len(next_carb_ind[0]) >0:
            if next_carb_ind[0][0]:
                # Time until last meal (in seconds).
                tm_nxt_carbs.append(bg_data[0][ruh] - 
                                carbs_data[0][next_carb_ind[0][0]])
            else:
                tm_nxt_carbs.append(numpy.nan)
        else:
            tm_nxt_carbs.append(numpy.nan)          
    return tm_nxt_carbs

def find_time_last_carbs(bg_data, carbs_data):
    '''Finds how long ago carbs we easten for each bg data point.'''
    tm_lst_carbs = []
    for ruh in range(len(bg_data[0])):    
        # find the index of the last meal
        last_carb_ind = numpy.nonzero(carbs_data[0] < bg_data[0][ruh])
        if len(last_carb_ind[0]) == 0:
            tm_lst_carbs.append(numpy.nan)
        else:
            # Time until last meal (in seconds).
            tm_lst_carbs.append(bg_data[0][ruh] - 
                                carbs_data[0][last_carb_ind[0][-1]])
    return tm_lst_carbs

def separate_hypo_data(bg_data, low_lim):
    '''Generate a list of hypo events'''
    hypo_data = numpy.array(bg_data[0])[numpy.nonzero(bg_data[1] < low_lim)[0]]
    hypo_data.flatten().tolist()
    return hypo_data
        
def find_time_next_hypo(bg_data, hypo_data):
    '''Finds how long until the next hypo for each bg data point.'''
    tm_nxt_hypo = []
    if len(hypo_data) == 0:
        return None
    else:
        for ruh in range(len(bg_data[0])):    
            # find the index of the last meal
            next_hypo_ind = numpy.nonzero(hypo_data > bg_data[0][ruh])[0]
            if len(next_hypo_ind) == 0:
                tm_nxt_hypo.append(numpy.nan)
            else:
                # Time until last meal (in seconds).
                tm_nxt_hypo.append(bg_data[0][ruh] - 
                                   hypo_data[next_hypo_ind[0]])
        return tm_nxt_hypo

def find_time_last_hypo(bg_data, hypo_data):
    '''Finds how long ago since the last hypo for each bg data point.'''
    tm_lst_hypo = []
    if len(hypo_data) == 0:
        return None
    else:
        for ruh in range(len(bg_data[0])):    
            # find the index of the last meal
            last_hypo_ind = numpy.nonzero(hypo_data < bg_data[0][ruh])[0]
            if len(last_hypo_ind) == 0:
                tm_lst_hypo.append(numpy.nan)
            else:
                # Time until last meal (in seconds).
                tm_lst_hypo.append(bg_data[0][ruh] - 
                                   hypo_data[last_hypo_ind[-1]])
        return tm_lst_hypo
    
def find_val_last_bolus(bg_data, bolus_data):
    '''Finds the value of the last bolus for each bg data point.'''
    val_lst_bolus = []
    for ruh in range(len(bg_data[0])):    
        # find the index of the last meal
        last_bolus_ind = numpy.nonzero(bolus_data[0] < bg_data[0][ruh])
        if len(last_bolus_ind[0]) == 0:
            val_lst_bolus.append(numpy.nan)
        else:
            val_lst_bolus.append(bolus_data[1][last_bolus_ind[0][-1]])
    return val_lst_bolus

def find_time_last_bolus(bg_data, bolus_data):
    '''Finds how long ago since the last bolus for each bg data point.'''
    tm_lst_bolus = []
    for ruh in range(len(bg_data[0])):    
        # find the index of the last meal
        last_bolus_ind = numpy.nonzero(bolus_data[0] < bg_data[0][ruh])
        if len(last_bolus_ind[0]) == 0:
            tm_lst_bolus.append(numpy.nan)
        else:
            # Time until last bolus (in seconds).
            tm_lst_bolus.append(bg_data[0][ruh] - 
                                bolus_data[0][last_bolus_ind[0][-1]])
    return tm_lst_bolus
    
def finding_high_limit(tm_lst_carbs, hi_lim):
    '''Calculating the effective high limit once recent carb intake 
    has been accounted for.'''
    ## setting the hi limit
    if not tm_lst_carbs:
        return None
    else:
        hi_lim_val = []
        for ruh in range(len(tm_lst_carbs)):
            if tm_lst_carbs[ruh] < 60*60:
                # less than an hour so increase the hi limit by 4mmol/ml
                hi_lim_val.append(hi_lim + 4)
            elif tm_lst_carbs[ruh] < 60*60*2:
                # less than 2 hours so increase the hi limit by 2mmol/ml
                hi_lim_val.append(hi_lim + 2)
            else:
                hi_lim_val.append(hi_lim)
    return hi_lim_val

def finding_states(bg_data, levels, hi_lim_val):
    '''Clasifying each blood glucose value as high, OK or low.'''
    hi3_lim = levels[0]
    hi2_lim = levels[1]
    warn_lim = levels[3]
    low_lim = levels[4]
    state = []
    for ruh in range(len(bg_data[1])):
        ## what state is it (high,OK,warn,Low)
        if bg_data[1][ruh] >= hi3_lim:
            state.append(1) # extremelyhigh
        elif bg_data[1][ruh] >= hi2_lim and bg_data[1][ruh] < hi3_lim:
            state.append(2) # very high
        elif bg_data[1][ruh] >= hi_lim_val[ruh] and bg_data[1][ruh] < hi2_lim:
            state.append(3) # high
        elif bg_data[1][ruh] >= warn_lim and bg_data[1][ruh] < hi_lim_val[ruh]:
            state.append(4) # OK
        elif bg_data[1][ruh] >= low_lim and bg_data[1][ruh] < warn_lim:
            state.append(5) # warn
        elif bg_data[1][ruh] < low_lim:
            state.append(6) # Low
        else:
            state.append(numpy.nan)
    return state
        
def etime(endtime, starttime):
    '''Returns the time elapsed between start and end.'''
    return endtime - starttime
    
def datevec(num):
    '''Converts a date number into a vector of 
    [year, month, day, hour, minute, second].'''
    vec = datetime.datetime.fromtimestamp(num)
    return [vec.year, vec.month, vec.day, vec.hour, vec.minute, vec.second]

def time_gap(bg_point, data, ind = None):
    ''' Time between events (in seconds).'''
    if ind == None:
        return numpy.nan
    else:
        return abs(etime(datevec(bg_point), datevec(data[ind, 0])))
    
def round2minute(val_in):
    '''Rounds timestamps to the nearest minute.
    Can deal with inputs as floats, arrays or lists.
    Outputs a list''' 
    # convert from seconds to minutes
    if type(val_in) == 'list':
        val_in = numpy.array(val_in)/60.
    else:
        val_in = val_in / 60.
    val_out = val_in.round() *60.
    if type(val_out) == 'numpy.ndarray' :
        val_out = val_out.flatten().tolist()
    return val_out

def find_ind(data, tik, step):
    '''Finds the index where ti is between +- step/2.'''
    low = tik - step/2.
    high = tik + step/2.
    ind1 = numpy.nonzero(numpy.array(data) > low)
    ind2 = numpy.nonzero(numpy.array(data) <= high)
    if not ind1 or not ind2:
        return None
    return numpy.intersect1d(ind1[0], ind2[0])[0]

def intialise_trace(data):
    '''Sets up the timebase of the trace an a placeholder list of nan for the 
    data to go into.'''
    #length of sample time in seconds
    data_length = etime(data[0][-1], data[0][0])
    data_start_time = round2minute(data[0][0])
    data_time_axis = data_start_time + \
        numpy.linspace(0,data_length-1,data_length/60)
    # making sure no small fractions of a second have been added to the
    # timestamps!
    data_time_axis = round2minute(data_time_axis)
    data_time_axis = data_time_axis.flatten().tolist()
    # setting initial values
    trace = numpy.ones((len(data_time_axis), 1)) * numpy.nan
    trace = trace.flatten().tolist()
    return data_time_axis, trace
    
def generate_bg_trace(bg_data):
    '''Outputs the bg data on a minute by minute basis 
    using linear interpolation where neccessary.''' 
    if not bg_data:
        return None
    data_time_axis, bg_trace = intialise_trace(bg_data)
    for mwg in range(len(bg_data[0])-1):
        # find the start and end times of the current event
        start_time = bg_data[0][mwg]
        end_time   = bg_data[0][mwg + 1]
        start_val  = bg_data[1][mwg]
        end_val    = bg_data[1][mwg + 1]
        num_steps  = int(round(etime(end_time, start_time))/60.)
        step = 120
        increment = (end_val - start_val)/ num_steps
        start_ind = find_ind(data_time_axis, start_time, step/2.)
        for hes in range(num_steps):
            # Adding linearly interpolated values to the trace.
            if start_val != None and end_val != None:
                bg_trace[start_ind + hes] = start_val + (increment * hes)
    return [data_time_axis, bg_trace]

def generate_basal_trace(basal_data):
    '''outputs the basal dose on a minute by minute basis.'''
    if not basal_data:
        return None
    else:
        data_time_axis, basal_trace = intialise_trace(basal_data)
        step = 120
        for mwp in range(2, numpy.size(basal_data[1])-1):
            # find the start and end times of the current event
            start_time = round2minute(basal_data[0][mwp])
            end_time = round2minute(basal_data[0][mwp + 1])
            start_ind = find_ind(data_time_axis, start_time, step / 2)
            end_ind = find_ind(data_time_axis, end_time, step / 2) 
            if end_time - start_time < 86400 and \
            start_ind != None and \
            end_ind != None:
                # less than a day between data points.
                # value divided by 60 as original value is an hourly rate 
                #and I am looking at a per minute dose.
                val = basal_data[1][mwp]
                for lew in range(start_ind, end_ind - 1):
                    basal_trace[lew] = val / 60.
    return [data_time_axis, basal_trace]

def get_daily_totals(data):
    '''outputs the sum value for each day in the datastream.'''
    for kse in range(len(data[0])):
        data[0][kse] = data[0][kse]/86400.
    day_breaks = numpy.nonzero(numpy.diff(numpy.floor(data[0])) != 0)
    day_breaks = day_breaks[0]
#    daily_totals = zeros((len(day_breaks),2))
    time_out = []
    data_out = []
    for nse in range(len(day_breaks)):
        if nse == 0:
            day_start = 0
            day_end = day_breaks[nse]
        else:
            day_start = day_breaks[nse-1] + 1
            day_end = day_breaks[nse]
        time_out.append(data[0][day_start])
        data_out.append(sum(data[1][day_start:day_end]))
    return [time_out, data_out]

def daily_stats(trace):
    '''outputs the max, min, mean, std value for each day in the datastream.'''
    if not trace:
        return [None, None], [None, None], [None, None], [None, None]
    else:
        trace = remove_nan_from_stream(trace)
        print numpy.isnan(numpy.array(trace[0])).any
        for kse in range(len(trace[0])):
            trace[0][kse] = trace[0][kse]/86400.
        day_breaks = numpy.nonzero(numpy.diff(numpy.floor(trace[0])) != 0)
        day_breaks = day_breaks[0]
        time_out = []
        means = []
        day_max = []
        day_min = []
        st_dev = []
        for nse in range(len(day_breaks)):
            if nse == 0:
                day_start = 0
                day_end = day_breaks[nse]
            else:
                day_start = day_breaks[nse-1] + 1
                day_end = day_breaks[nse]
            time_out.append(trace[0][day_start])
            day_data = trace[1][day_start:day_end]
            means.append(numpy.mean(numpy.array(day_data)))
            day_max.append(max(day_data))
            day_min.append(min(day_data))
            st_dev.append(numpy.std(numpy.array(day_data)))
    return [time_out, day_min], [time_out, day_max], \
            [time_out, means], [time_out, st_dev]

def generate_state_streams(bg_data, state):
    '''Contructs the state data stream from the separate sub streams.'''
    t_high3, t_high2, t_high1, t_ok, t_warn, t_low, t_hyper, t_hypo = \
        separate_states(bg_data[0], state)
    high3, high2, high1, okay, warn, low, hyper, hypo = \
        separate_states(bg_data[1], state)
    return [[t_low, low], [t_warn, warn], [t_ok, okay], \
           [t_high1, high1], [t_high2, high2], [t_high3, high3],
            [t_hypo, hypo], [t_hyper, hyper]]

def unique_list(seq):
    '''Return the unique values in a list.'''
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if x not in seen and not seen_add(x)]


def list_subset(data, selectors, condition):
    '''Takes a data list and a selector list along with a criterion for the 
    selector. if the selector meets the criterion then the repective value 
    for the data list is added to the output.'''
    data_out = []    
    for nsj in range(len(selectors)):
        if selectors[nsj] == condition:
            data_out.append(data[nsj])
    return data_out
    
def separate_states(bg_data, state):
    '''Separates out the high Ok and low data.'''
    high3 = list_subset(bg_data, state, 1)
    high2 = list_subset(bg_data, state, 2)
    high1 = list_subset(bg_data, state, 3)
    okay    = list_subset(bg_data, state, 4)
    warn  = list_subset(bg_data, state, 5)
    low   = list_subset(bg_data, state, 6)
    hyper = high3 + high2 + high1
    hypo = warn + low
    return high3, high2, high1, okay, warn, low, hyper, hypo
    
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


def remove_nan_from_list(data_in):
    '''Removes nan from a list of numbers'''
    data_out = []
    for dkn in data_in:
        if not numpy.isnan(dkn):
            data_out.append(dkn)
    return data_out

def remove_nan_from_stream(data_in):
    '''Remove data points where the data is nan
    (so also removes the timestamp)'''
    time_out = []    
    data_out = []
    for hst in range(len(data_in[0])):
        if not numpy.isnan(data_in[0][hst]) and not \
                numpy.isnan(data_in[1][hst]):
            data_out.append(data_in[1][hst])
            time_out.append(data_in[0][hst])
    return [time_out, data_out]


def top():   
    '''Analysis of blood glucose and insulin dose data which has been 
    extracted into a xls spreadsheet from the manufacturers reporting tools.'''
    # Alarm levels
    levels = [20, 15, 8, 4, 3.7]
    # Generate a set of datastreams from the xls. each stream is a 
    # matrix with dimensions 2XN with [0] being the time and
    # [1] being the data.
    bolusstream, basalstream, basaladjustream, basaladjlstream, \
            bgstream, carbstream, eventstream\
            = import_module_xls('.')
    cgmstream, cgm_device_name, cgm_device_id = \
            get_CGM_data('./CGM_data')
    # Need to generate minute by minute traces
    basal_trace = generate_basal_trace(basalstream)
    bg_trace = generate_bg_trace(bgstream)
    hypostream = separate_hypo_data(bgstream, levels[4])
    tm_lst_hypo = find_time_last_hypo(bg_trace, hypostream)
    tm_nxt_hypo = find_time_next_hypo(bg_trace, hypostream)
    tm_lst_carbs = find_time_last_carbs(bg_trace, carbstream)
    tm_nxt_carbs = find_time_next_carbs(bg_trace, carbstream)
    pre_meal_flg = add_pre_meal_flag(tm_nxt_carbs)
    post_meal_flg = add_post_meal_flag(tm_lst_carbs)
    val_lst_bolus = find_val_last_bolus(bg_trace, bolusstream)
    tm_lst_bolus = find_time_last_bolus(bg_trace, bolusstream)
    hi_lim_val = finding_high_limit(tm_lst_carbs, levels[2])
    state = finding_states(bg_trace, levels, hi_lim_val)
    #print len(state)
    # Generating daily totals for the carbs, basal, and bolus.
    # The basal needs to use the trace as the raw data does not give duration
    # directly, only records changes applied.
    basal_dailys = get_daily_totals(basal_trace)
    bolus_dailys = get_daily_totals(bolusstream)
#    carb_dailys = get_daily_totals(carbstream)
    bg_day_min, bg_day_max, bg_day_mean, bg_day_std = daily_stats(bg_trace)
    state_streams = generate_state_streams(bg_trace, state)    
    fracs = calc_fractions(state_streams)
    
#    figure(5)
#    plot(basal_dailys[0], basal_dailys[1])
#    plot(bolus_dailys[0], bolus_dailys[1])
#    plot(carb_dailys[0], carb_dailys[1])
#    figure(6)
    figure(7)
    ax1 = axes([0.1, 0.5, 0.4, 0.45])
    ax1.plot(bg_day_min[0], bg_day_min[1], 'r')
    ax1.plot(bg_day_max[0], bg_day_max[1], 'b')
    ax1.plot(bg_day_mean[0], bg_day_mean[1], 'ko')
    ax1.set_ylabel('Blood Glucose (mg/mmol)')
    ax1.set_title('Daily values')
    st1 = remove_nan_from_stream(bgstream)
    st2 = remove_nan_from_stream(state_streams[0])
    ax2 = subplot(222)
    hold(True)
    ax2.plot(st1[0], st1[1])
    ax2.fill_between(st2[0], st2[1], y2=4.0, facecolor='yellow')
    ax2.fill_between(st2[0], st2[1], y2=3.7, facecolor='red')    
#    ax2.fill_between(st2[0], st2[1], 8.0, facecolor='blue') 
    ax2.set_xlim(st1[0][0], st1[0][0])
    hold(False)
    ax2.set_ylabel('Blood Glucose (mg/mmol)')
    ax2.set_title('Blood glucose over time')
    ax2.set_xlabel('Time')
    ax3 = subplot(223)
    data_len = len(bg_day_mean[0])
    hold(True)
    for  ihp in range(data_len):
        col_val = ((data_len - (ihp-1))/data_len) * 0.6 + 0.4
        sze = numpy.floor(((data_len - ihp)/data_len) * 7) + 3
        ax3.plot(bg_day_std[1][ihp], bg_day_mean[1][ihp], 'o', \
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
    light_filter_pie(ax4, fracs)
    ax4.set_title('Fraction of time in each state')
    
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
top()