# -*- coding: utf-8 -*-
"""
Created on Mon Jun 11 21:03:28 2012

@author: alun
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Jan 16 17:06:12 2012

@author: afdm76
"""
from locate_data import dir_list_gen
import numpy
import csv
from cgm_import import convert_units
from datetime import datetime
from numpy import nan
import time

def BG_data_extraction(data_in):
    '''Conditioning the extracted raw CGM data into a datastream.'''
    #remove data with empty timestamps, empty data, or 
    # where the value is < 4 as this is a bogus placeholder.
    print len(data_in)
    dates = data_in[0][8:]
    times = data_in[1][8:]
    bg = data_in[2][8:]
    pen_doses = [3][8:]
    bolus = [6][8:]
    basal = [53][8:]
    carbs = [9][8:]
    timestamps = []    
    print 'length of dates:', len(dates)
    print 'length of bolus:', len(bolus) 
    print 'length of basal:', len(basal) 
    print 'length of bg:', len(bg) 
    print 'length of pen_doses:', len(pen_doses) 
    print 'length of carbs:', len(carbs) 
    for js in range(len(dates)):
        if len(dates[js]) ==0 or len(times[js]) == 0:
            timestamps.append(nan)
        else:
            tmp = datetime.strptime(dates[js] + ' ' + times[js], '%m/%d/%Y %H:%M:%S')
            timestamps.append(time.mktime(tmp.timetuple()))
    # convert to floats from strings
    bg = convert_to_float(bg)
#    timestamps = convert_to_float(timestamps)
    pen_doses = convert_to_float(pen_doses)
    bolus = convert_to_float(bolus)
    basal = convert_to_float(basal)
    carbs = convert_to_float(carbs)
    # convert from mg/dL to mm/L
    bg = map(convert_units, bg)
    return [timestamps, bolus, basal, bg, carbs, pen_doses]
    
def convert_to_float(data):
    out = []
    for js in range(len(data)):
        try:
            out.append(float(data[js]))
        except ValueError:
            out.append(nan)
           
    return out
    
def get_BG_data(dir_path):
    '''Extract raw data from the file.'''
    lst = dir_list_gen(dir_path,'CSV')
    #for kn in range(len(lst)):
    out = []
    with open(lst[0],'rb') as f:
        reader = csv.reader(f, delimiter=';')
        for row in reader:
            out.append(row)
        print 'get_BG_data:', len(out[0])
        out = [[row[i] for row in out] for i in range(len(out[0]))]  
    timestamps, bolus, basal, bg, carbs, pen_doses = \
     BG_data_extraction(out)
    print 'length of timestamps:',  len(timestamps)
    print 'length of bolus:',  len(bolus)
    return numpy.vstack((numpy.array(timestamps), numpy.array(bolus))), \
           numpy.vstack((numpy.array(timestamps), numpy.array(basal))), \
           numpy.vstack((numpy.array(timestamps), numpy.array(bg))), \
           numpy.vstack((numpy.array(timestamps), numpy.array(carbs))), \
           numpy.vstack((numpy.array(timestamps), numpy.array(pen_doses))) \

           
    