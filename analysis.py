# -*- coding: utf-8 -*-
"""
Created on Tue Aug 23 15:57:57 2011

@author: afdm76
"""
import numpy
#from matplotlib.dates import date2num, num2date
from xls_import import import_module_xls
from cgm_import import get_CGM_data
import datetime
import plotting
import calendar

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

def find_time_next(ref_data, ev_data):
    '''Finds how long until the next event in ev_data for each bg data point.'''
    tm_nxt = []
    if ev_data.shape[1] == 0:
        return None
    else:
        for ruh in range(ref_data.shape[1]):    
            # find the index of the last meal
            next_ind = numpy.nonzero(ev_data > ref_data[0, ruh])[0]
            if len(next_ind) == 0:
                tm_nxt.append(numpy.nan)
            else:
                # Time until last meal (in seconds).
                tm_nxt.append(ref_data[0, ruh] - ev_data[0, next_ind[0]])
        return numpy.array(tm_nxt)

def find_time_last(ref_data, ev_data):
    '''Finds how long ago since the last hypo for each bg data point.'''
    tm_lst = []
    if ev_data.shape[1] == 0:
        return None
    else:
        for ruh in range(ref_data.shape[1]):    
            # find the index of the last meal
            last_ind = numpy.nonzero(ev_data[0, :] < ref_data[0, ruh])[0]
            if len(last_ind) == 0:
                tm_lst.append(numpy.nan)
            else:
                # Time until last meal (in seconds).
              #  print type(ev_data[0, last_ind[-1]])
                tm_lst.append(ref_data[0, ruh] - ev_data[0, last_ind[-1]])
        return numpy.array(tm_lst)

def separate_hypo_data(bg_data, low_lim):
    '''Generate a list of hypo events'''
    hypo_data = bg_data[:, numpy.nonzero(bg_data[1, :] < low_lim)[0]]
    #print 'Size of hypo data', hypo_data.shape
    return hypo_data

def find_val_last(ref_data, ev_data):
    '''Finds the value of the last event in ev_data for each bg data point.'''
    val_lst = []
    for ruh in range(ref_data.shape[1]):    
        # find the index of the last meal
        last_ind = numpy.nonzero(ev_data[0, :] < ref_data[0, ruh])
        if len(last_ind[0]) == 0:
            val_lst.append(numpy.nan)
        else:
            val_lst.append(ev_data[1][last_ind[0][-1]])
    return numpy.array(val_lst)

def finding_high_limit(tm_lst_carbs, hi_lim):
    '''Calculating the effective high limit once recent carb intake 
    has been accounted for.'''
    ## setting the hi limit
    if tm_lst_carbs.shape[0] == 0:
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

def roundstream2minute(stream):
    '''Rounds the timestamps in a stream to the nearest minute.'''
   # print 'Round input',numpy.shape(stream)
    times = stream[0, :]
    data = stream[1, :]
    times = numpy.round(times / 60.) * 60.
    return numpy.vstack((times, data))

def find_ind(data, tik, step):
    '''Finds the index where ti is between +- step/2.'''
    low = tik - step/2.
    high = tik + step/2.
    ind1 = numpy.nonzero(numpy.array(data) > low)
    ind2 = numpy.nonzero(numpy.array(data) <= high)
    if len(ind1) == 0 or len(ind2) == 0:
        return None
    com = numpy.intersect1d(ind1[0], ind2[0])
    if len(com) == 0:
        return None
    return com[0]

def select_time_period(input_stream, start, end):
    '''Takes a stream and returns only the section between 
    the starts date and end date.'''
    print 'start', start
    print 'input', input_stream[0][0:5]
    ind1 = numpy.nonzero(input_stream[0] < start)
    print 'index', ind1[0][0:4]
    print 'end', end
    ind2 = numpy.nonzero(input_stream[0] > end)
    print 'index', ind2[0][0:4]
    #numpy.delete(input_stream, ind2[0], 1)
    return numpy.delete(input_stream, numpy.hstack((ind1[0], ind2[0])), 1)

def intialise_trace(data):
    '''Sets up the timebase of the trace and a placeholder list of nan for the 
    data to go into.'''
    #length of sample time in seconds
    data_start_time = round2minute(data[0, 0])
    data_end_time = round2minute(data[0, -1])    
    data_length = etime(data_end_time, data_start_time)
    data_time_axis = data_start_time + \
        numpy.linspace(0,data_length-1,data_length/60)
    # setting initial values
    trace = numpy.zeros((len(data_time_axis), 1))
    return numpy.vstack((data_time_axis, trace[:, 0]))

def find_interp_val(start_time, end_time, req_time, start_val, end_val):
    '''Will return the linearly interpolated value 
    at the requested timestamp.'''  
    elapsed = end_time - start_time
    sel_time = req_time - start_time
    val_change = start_val - end_val
    req_val = start_val + (sel_time / elapsed) * val_change
    return req_val

def find_interp_time(start_time, end_time, start_val, end_val, req_val):
    '''Will return the linearly interpolated time
    for the requested value.'''
    elapsed = end_time - start_time
    val_change = end_val - start_val
    sel_val = req_val - start_val    
    req_time = start_time + (sel_val / val_change) * elapsed
    return req_time

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
            if start_val != None and end_val != None and start_ind != None:
                bg_trace[start_ind + hes] = start_val + (increment * hes)
    return [data_time_axis, bg_trace]

def generate_trace(stream):
    '''Outputs the data on a minute by minute basis 
    using linear interpolation where neccessary.''' 
    if stream.shape[1] == 0:
        return None
    #print 'Stream shape', stream.shape
    trace = intialise_trace(stream)
    #print 'Trace shape', trace.shape
   # print 'time axis', data_time_axis[0]
    for mwg in range(stream.shape[1]-1):
        # find the start and end times of the current event
        start_time = stream[0, mwg]
        end_time   = stream[0, mwg + 1]
        start_val  = stream[1, mwg]
        end_val    = stream[1, mwg + 1]
        num_steps  = int(round(etime(end_time, start_time))/60.)
        step = 120
        increment = (end_val - start_val)/ num_steps
        start_ind = find_ind(trace[0, :], start_time, step/2.)
        for hes in range(num_steps):
            # Adding linearly interpolated values to the trace.
           # print start_val, end_val, hes, increment, start_ind
            if start_val != None and end_val != None and start_ind != None:
                trace[1, start_ind + hes] = start_val + (increment * hes)
    return trace

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

def get_daily_totals(stream):
    '''outputs the sum value for each day in the datastream.'''
    if stream.shape[1] == 0:
        return numpy.vstack((None, None))
    else:
        day_breaks = numpy.nonzero(
                        numpy.diff(numpy.floor(stream[0, :]/86400.)) != 0)
        for nse in range(len(day_breaks[0])):
            if nse == 0:
                day_start = 0
                day_end = day_breaks[0][nse]
                time_out = numpy.array(stream[0, day_start])            
                day_sum = numpy.array(sum(stream[1, day_start:day_end]))
            else:
                day_start = day_breaks[0][nse-1] + 1
                day_end = day_breaks[0][nse]
                time_out = numpy.hstack((time_out, stream[0, day_start]))
                day_sum = numpy.hstack(
                            (day_sum, sum(stream[1, day_start:day_end])))
    return numpy.vstack((time_out, day_sum))

def daily_stats(stream):
    '''outputs the max, min, mean, std value for each day in the datastream.'''
    if stream.shape[1] == 0:
        return numpy.vstack((None, None)), numpy.vstack((None, None)), \
               numpy.vstack((None, None)), numpy.vstack((None, None))
    else:
        day_breaks = numpy.nonzero(
                        numpy.diff(numpy.floor(stream[0, :]/86400.)) != 0)
        for nse in range(len(day_breaks[0])):
            if nse == 0:
                day_start = 0
                day_end = day_breaks[0][nse]
                time_out = numpy.array(stream[0, day_start])            
                day_max = numpy.array(max(stream[1, day_start:day_end]))
                day_min = numpy.array(min(stream[1, day_start:day_end]))
                # Generating a minute by minute trace so that the
                # std nd mean have equispaced data.
                trace = generate_trace(stream[:, day_start:day_end])
                st_dev = numpy.std(numpy.array(trace[1, :]))
                means = numpy.mean(numpy.array(trace[1, :]))
            else:
                day_start = day_breaks[0][nse-1] + 1
                day_end = day_breaks[0][nse]
                time_out = numpy.hstack((time_out, stream[0, day_start]))    
                day_max = numpy.hstack(
                            (day_max, max(stream[1, day_start:day_end])))
                day_min = numpy.hstack(
                            (day_min, min(stream[1, day_start:day_end])))
                # Generating a minute by minute trace so that the
                # std nd mean have equispaced data.
                trace = generate_trace(stream[:, day_start:day_end])
                st_dev = numpy.hstack((st_dev, numpy.std(trace[1, :])))
                means = numpy.hstack((means, numpy.mean(trace[1, :])))
    return numpy.vstack((time_out, day_min)), \
           numpy.vstack((time_out, day_max)), \
           numpy.vstack((time_out, means)), \
           numpy.vstack((time_out, st_dev))

def generate_state_streams(bg_data, state):
    '''Contructs the state data stream from the separate sub streams.'''
    t_high3, t_high2, t_high1, t_ok, t_warn, t_low, t_hyper, t_hypo = \
        separate_states(bg_data[0], state)
    high3, high2, high1, okay, warn, low, hyper, hypo = \
        separate_states(bg_data[1], state)
    return [[t_low, low], [t_warn, warn], [t_ok, okay], \
           [t_high1, high1], [t_high2, high2], [t_high3, high3],
            [t_hypo, hypo], [t_hyper, hyper]]

def combine_data_streams(samples, CGM_data):
    '''using the bg data from the monitor to pin the CGM data 
    (assumes bg monitor is more reliable than the CGM)'''
    extra_points_flag = 0
    if CGM_data.shape[1] == 0 or samples.shape[1] == 0:
        combined_data = None
    else:
        combined_data = numpy.copy(CGM_data)
        # iterating over each BG point.
        for hs in range(samples.shape[1]-1):
            sample_start = samples[0, hs]
            sample_end = samples[0, hs+1]
            # Finds the CGM datapoints either side of the BG data points.
            # TODO Check if it is valid if there are multiple BG points 
            # between CGM points. 
            [cgm_st_val, tmp_start1, tmp_end1] = find_CGM_at_BG(
                            CGM_data[1, :], CGM_data[0, :], sample_start)
            [cgm_end_val, tmp_start2, tmp_end2] = find_CGM_at_BG(
                            CGM_data[1, :], CGM_data[0, :], sample_end)
            if CGM_data[0, tmp_end1] > sample_end:
                if extra_points_flag == 0:
                    extra_points = numpy.array(samples[:,hs],ndmin=2)
                    extra_points_t = numpy.copy(samples[0,hs])
                    extra_points_d = numpy.copy(samples[1,hs])
                    extra_points_flag = 1
                else:         
                    extra_points = numpy.append(extra_points, numpy.array(samples[:,hs], ndmin=2),0)
                    extra_points_t = numpy.append(extra_points_t, samples[0,hs])
                    extra_points_d = numpy.append(extra_points_d, samples[1,hs])
            else:
                # difference between samples and CGM data
                diff1 = samples[1, hs] - cgm_st_val
                diff2 = samples[1, hs + 1] - cgm_end_val - diff1
                temp = CGM_data[1, tmp_end1:tmp_start2]
                temp_time = CGM_data[0, tmp_end1:tmp_start2]
                # initially shift everything down by diff1
                temp = temp + diff1
                #then compress so get diff2 == 0
                # Assumes difference is distributed linearly along range.
                for hm in range(len(temp)):
                    correction = diff2 * (temp_time[hm] - sample_start) / \
                                         (sample_end - sample_start)
                    combined_data[1, tmp_end1 + hm] = temp[hm] + correction
#        print 'extra points', numpy.hstack((extra_points_t, extra_points_d)), 'Combined data', combined_data       
#        extra_points = numpy.hstack((numpy.array(extra_points_t), numpy.array(extra_points_d)))        
#        numpy.array(extra_points_t).reshape((2,-1))        
#        numpy.transpose(extra_points)
#        print ' combined', numpy.shape(combined_data)
#        print 't', numpy.shape(numpy.array(extra_points_t)), 'd', numpy.shape(numpy.array(extra_points_t))  
        extra_points = numpy.vstack((numpy.array(extra_points_t), numpy.array(extra_points_d)))
#        print extra_points, numpy.shape(extra_points)   
        combined_data = numpy.hstack((combined_data, extra_points))
#        print numpy.shape(combined_data)
        ind = numpy.argsort(combined_data[0,:])  
        combined_data = combined_data[:,ind]
#        print numpy.shape(combined_data)
        return combined_data

def find_CGM_at_BG(CGM_data, CGM_times, BG_time):
    ''' Finds the CGM datapoints either side of the first BG data point 
    and then calculate the interpolated value of the CGM at the BG time
    point.'''
    tmp1 = numpy.array(numpy.nonzero(CGM_times <= BG_time))
    tmp_start = tmp1[0][-1]
    tmp2 = numpy.array(numpy.nonzero(CGM_times >= BG_time))
    tmp_end = tmp2[0][0]
    new_cgm_val = find_interp_val(CGM_times[tmp_start], 
                         CGM_times[tmp_end], BG_time,
                         CGM_data[tmp_start], 
                         CGM_data[tmp_end])
    return new_cgm_val, tmp_start, tmp_end


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

def remove_nan_from_stream(data):
    '''Remove data points where the data is nan
    (so also removes the timestamp)'''   
    inds = numpy.nonzero( numpy.isnan(data) == True)   
    print len(inds[1])
    if len(inds[1]) == 0:
        return data
    else:
        return numpy.delete(data, inds[1], 1)

def remove_nan_from_list(data_in):
    '''Removes nan from a list of numbers.'''
    data_out = []
    for dkn in data_in:
        if not numpy.isnan(dkn):
            data_out.append(dkn)
    return data_out

def calc_dur_and_rt(event_values, event_state, levels):
    '''Calculates duration of events and recovery times back to normal.'''
    # a = bg_events(4,:) - circshift(bg_events(4,:),[0 1])
    b = numpy.nonzero(event_state[:, 1] == 4)

    p1 = 1
    p2 = 1
    p3 = 1
    p5 = 1
    p6 = 1
    ph = 1
    pp = 1
    recovery_high = []
    recovery_high3 = []
    recovery_high2 = []
    recovery_high1 = []
    recovery_warn = []
    recovery_low = []
    recovery_hypo = []
    duration_high = []
    duration_high3 = []
    duration_high2 = []
    duration_high1 = []
    duration_warn = []
    duration_low = []
    duration_hypo = []
    for nw in range(len(b) -1):
        if b[nw+1] - b[nw] > 1:
            c = event_values[b[nw]+1:b[nw+1]-1, 2]
            if c[1] <= levels[4]:
                [tp, I] = min(c)
            else:
                [tp, I] = max(c)
            # find most extreeme state which has been recovered from in this
            # event
            srf = event_state[b[nw]+I, 2]
            # recovery time in hours from start of event
            rt = etime(datevec(event_state[b[nw+1], 1]),
                       datevec(event_state[b[nw]+ 1, 1]))/3600
            # duration of event in hours
            dt = etime(datevec(event_state[b[nw+1], 1]),
                       datevec(event_state[b[nw], 1]))/3600
            if srf == 6:
                recovery_low[p6] = rt
                duration_low[p6] = dt
                p6 = p6 +1
                recovery_hypo[pp] = rt
                duration_hypo[pp] = dt
                pp = pp +1
            elif srf == 5:
                recovery_warn[p5] = rt
                duration_warn[p5] = dt
                p5 = p5 +1
                recovery_hypo[pp] = rt
                duration_hypo[pp] = dt
                pp = pp +1
            elif srf == 3:
                recovery_high1[p3] = rt
                duration_high1[p3] = dt
                p3 = p3 +1
                recovery_high[ph] = rt
                duration_high[ph] = dt
                ph = ph +1
            elif srf == 2:
                recovery_high2[p2] = rt
                duration_high2[p2] = dt
                p2 = p2 +1
                recovery_high[ph] = rt
                duration_high[ph] = dt
                ph = ph +1
            elif srf == 1:
                recovery_high3[p1] = rt
                duration_high3[p1] = dt
                p1 = p1 +1
                recovery_high[ph] = rt
                duration_high[ph] = dt
                ph = ph +1
    counts = [p1, p2, p3, p5, p6, ph, pp]
    return recovery_high, recovery_high3, recovery_high2, recovery_high1, \
    recovery_warn, recovery_low, recovery_hypo, \
    duration_high, duration_high3, duration_high2, duration_high1, \
    duration_warn, duration_low, duration_hypo, counts

def event_means(recovery, duration):
    ''' Generates the mean values of the durations and recovery times, rounded to
     the nearest 0.1hr'''
    p = numpy.size(duration, 1)
    if p >= 1:
        num = len(recovery)
        mean_recovery = round(numpy.mean(recovery[1])*10)/10
        mean_duration = round(numpy.mean(duration[1])*10)/10

    else:
        mean_recovery = 0
        mean_duration = 0
        num = 0
    return num, mean_recovery, mean_duration

def generate_event_list(bg_tests, samples, states):
    states = numpy.array(states)
    oks = numpy.nonzero(states == 4)
    diffs = numpy.diff(states)
    locs = numpy.nonzero(diffs !=0)
    # indicied where move from ok to not ok    
    c = numpy.intersect1d(locs[0], oks[0])
    # indicies where you move from not ok to ok
    d = numpy.intersect1d(locs[0]+1, oks[0])  
    if len(d) ==0 or len(c) == 0:
        event_type = []
        event_duration = []
        event_recovery = []
#        event_values = []
    else:    
        # number of events
        num = len(c)
        event_type = numpy.zeros((2, num))
        event_duration = numpy.zeros((2, num))
        event_recovery = numpy.zeros((2, num))
        #event_values = []
        for lgd in range(num - 1):
            # skipping incomplete events at the begining and end.
            # automatically skips the first one as it starts at 
            #the first time the state is 4/
            st = c[lgd]
            ed = d[lgd]
            ev = samples[:, st:ed]
            # Setting the event timestamps to be the start of the event.
            event_type[0, lgd] = ev[0, 0] 
            event_duration[0, lgd] = ev[0, 0] 
            event_recovery[0, lgd] = ev[0, 0] 
           # event_values[1,lgd] = ev
            # find the max/min and get the state info from that time
            mx = ev.max(1)[1]
            if mx < 8:
                mx = ev.min(1)[1]
            if numpy.isnan(mx):
                continue
            ind = (ev[1, :] == mx).nonzero()
            event_type[1, lgd] = states[st + ind[0][0]]
            # duration of event in hours
            event_duration[1, lgd] = (ev[0, -1] - ev[0, 0] ) / 3600.
            # find the first test done after event started.
            tst1 = (bg_tests[0, :] > ev[0, 0]).nonzero()
            # recovery time in hours
            if len(tst1[0]) == 0:
                event_recovery[1, lgd] = event_duration[1, lgd]
            else:
                event_recovery[1, lgd] = (
                                ev[0, -1] - bg_tests[0, tst1[0][0]]) / 3600.
    return event_type, event_duration, event_recovery#, event_values

def top(start_date = [1, 1, 2011], end_date = [1, 2, 2011]):   
    '''Analysis of blood glucose and insulin dose data which has been 
    extracted into a xls spreadsheet from the manufacturers reporting tools.'''
    # Alarm levels
    levels = [20, 15, 8, 4, 3.7]
    #convert to timestamps
    start_date = datetime.datetime(start_date[2], start_date[1], start_date[0])
    start_date = calendar.timegm(start_date.utctimetuple())
    end_date = datetime.datetime(end_date[2], end_date[1], end_date[0])
    end_date = calendar.timegm(end_date.utctimetuple())

    # Generate a set of datastreams from the xls. each stream is a 
    # matrix with dimensions 2XN with [0] being the time and
    # [1] being the data.
    bolusstream, basalstream, basaladjustream, basaladjlstream, \
            bgstream, carbstream, eventstream\
            = import_module_xls('.')
    cgmstream, cgm_device_name, cgm_device_id = \
            get_CGM_data('./CGM_data')
    print 'Data extracted from files'
    print type(basalstream)
    bolusstream = select_time_period(bolusstream, start_date, end_date)
    basalstream = select_time_period(basalstream, start_date, end_date)
    basaladjustream = select_time_period(basaladjustream, start_date, end_date)
    basaladjlstream = select_time_period(basaladjlstream, start_date, end_date)
    bgstream = select_time_period(bgstream, start_date, end_date)
    carbstream = select_time_period(carbstream, start_date, end_date)
    eventstream = select_time_period(eventstream, start_date, end_date)
    cgmstream = select_time_period(cgmstream, start_date, end_date)
    print type(basalstream)    
    print basalstream.shape  
    basalstream = remove_nan_from_stream(basalstream)
    bolusstream = remove_nan_from_stream(bolusstream)
    bgstream = remove_nan_from_stream(bgstream) 
    cgmstream = remove_nan_from_stream(cgmstream)
    carbstream = remove_nan_from_stream(carbstream)
    #eventstream = remove_nan_from_stream(eventstream)
    basaladjustream = remove_nan_from_stream(basaladjustream)
    basaladjlstream = remove_nan_from_stream(basaladjlstream)  
    print 'Streams conditioned'
    # combining the cgm and bg monitor data to get a trace which reflects the 
    # gradient changes as seen on the CGM with the (hopefully) more acurate
    # blood glucose readings of the bg monitor.
    combinedstream = combine_data_streams(bgstream, cgmstream)
    print 'Streams combined'   
    # separate out the hypo samples and use them to calculate the time since
    # the last hypo event.
    hypostream = separate_hypo_data(bgstream, levels[4])
    tm_lst_hypo = find_time_last(combinedstream, hypostream)
    tm_nxt_hypo = find_time_next(combinedstream, hypostream)
    # using the carbstream to calculate the time since the last meal.
    tm_lst_carbs = find_time_last(combinedstream, carbstream)
    tm_nxt_carbs = find_time_next(combinedstream, carbstream)
    pre_meal_flg = add_pre_meal_flag(tm_nxt_carbs)
    post_meal_flg = add_post_meal_flag(tm_lst_carbs)
    # Calculating the high limit for each data point as this changes 
    #depending on the proximity of a meal.
    hi_lim_val = finding_high_limit(tm_lst_carbs, levels[2])
    # using the bolusstream to calculate the time since the last bolus 
    #and  its value. 
    val_lst_bolus = find_val_last(combinedstream, bolusstream)
    tm_lst_bolus = find_time_last(combinedstream, bolusstream)

    state = finding_states(combinedstream, levels, hi_lim_val)
    event_type, event_duration, event_recovery = \
    generate_event_list(bgstream, combinedstream, state)
    event_num,event_recovery_mean,event_duration_mean = \
    event_means(event_recovery, event_duration)
    # Generating daily totals for the carbs, basal, and bolus.
    # The basal needs to use the trace as the raw data does not give duration
    # directly, only records changes applied.
    #basal_dailys = get_daily_totals(basal_trace)
    bolus_dailys = get_daily_totals(bolusstream)
    carb_dailys = get_daily_totals(carbstream)
    bg_day_min, bg_day_max, bg_day_mean, bg_day_std = daily_stats(
    combinedstream)
    state_streams = generate_state_streams(combinedstream, state) 
    event_duration_streams = generate_state_streams(
                                    event_duration, event_type[1]) 
    print 'Data analysed'
    plotting.main_plot(bgstream, state_streams, combinedstream, 
              bg_day_min, bg_day_max, bg_day_mean, bg_day_std, carb_dailys, 
              bolus_dailys, event_num,event_recovery_mean,event_duration_mean,
              event_type, event_duration_streams, event_recovery)
  #  plotting.spare_plot(bgstream, basalstream, bolusstream)
    #plotting.event_plot(event_num,event_recovery_mean,event_duration_mean,
     #                   event_type, event_duration_streams, event_recovery)
    plotting.comp_plot(bgstream, combinedstream, cgmstream)
    print 'Data plotted'


top()
