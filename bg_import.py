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
from cgm_import import convert_units, 

def BG_data_extraction(data_in):
    '''Conditioning the extracted raw CGM data into a datastream.'''
    #remove data with empty timestamps, empty data, or 
    # where the value is < 4 as this is a bogus placeholder.
    dates = data_in[0][8:]
    times = data_in[1][8:]
    bg = data_in[2][8:]
    pen_doses = [3][8:]
    bolus = [6][8:]
    basal = [53][8:]
    carbs = [9][8:]
    
    # convert to floats from strings
    values = map(float, values)
    timestamps = map(float, timestamps)
    # correct the time stamp
    timestamps = map(convert_timestamps, timestamps)
    ind1 = numpy.nonzero(numpy.array(values) < 4.)
    ind2 = numpy.nonzero(numpy.array(cal_flag) == 0.0)  
    ind = numpy.concatenate((ind1[0],ind2[0]), axis=0)   
    ind = numpy.unique(ind)

    # Makes sure the indicies are deleated from the bottom up.
    ind = ind[::-1]
    for ne in range(len(ind)):   
        del timestamps[ind[ne]]
        del values[ind[ne]]
    # convert from mg/dL to mm/L
    values = map(convert_units, values)
    return [timestamps, values, device_name, device_id]
    
def get_BG_data(dir_path):
    '''Extract raw data from the file.'''
    lst = dir_list_gen(dir_path,'csv')
    #for kn in range(len(lst)):
    out = []
    with open(lst[0],'rb') as f:
        reader = csv.reader(f, delimiter=';')
        for row in reader:
            out.append(row)
        out = [[row[i] for row in out] for i in range(len(out[0]))]  
    timestamps, values, device_name, device_id = \
     CGM_data_extraction(out)
    return numpy.vstack((numpy.array(timestamps), numpy.array(values))), \
            device_name, device_id
    