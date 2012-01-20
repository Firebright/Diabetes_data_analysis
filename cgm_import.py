# -*- coding: utf-8 -*-
"""
Created on Mon Jan 16 17:06:12 2012

@author: afdm76
"""
from locate_data import dir_list_gen
import numpy
import csv

def CGM_data_extraction(data_in):
    '''Conditioning the extracted raw CGM data into a datastream.'''
    #remove data with empty timestamps, empty data, or 
    # where the value is < 4 as this is a bogus placeholder.
    device_name = data_in[3][1]
    device_id = data_in[4][1]    
    timestamps = data_in[0][1:]
    values = data_in[11][1:]
    # convert to floats from strings
    values = map(float,values)
    timestamps = map(float, timestamps)
    ind1 = numpy.nonzero(not timestamps)
    ind2 = numpy.nonzero(not values)
    ind3 = numpy.nonzero(values < 4)
    ind = union(ind1, ind2)
    ind = union(ind, ind3)
    ind.sort()
    # Makes sure the indicies are deleated from the bottom up.
    ind.reverse()
    for ne in range(len(ind)):   
        del timestamps[ind[ne]]
        del values[ind[ne]]
    # correct the time stamp
    timestamps = map(convert_timestamps, timestamps)
    # convert from mg/dL to mm/L
    values = map(convert_units, values)
    return [timestamps, values, device_name, device_id]
    
def get_CGM_data(dir_path):
    '''Extract raw data from the file.'''
    lst = dir_list_gen(dir_path,'TAB')
    #for kn in range(len(lst)):
    out = []
    with open(lst[0],'rb') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            out.append(row)
        out = [[row[i] for row in out] for i in range(len(out[0]))]  
    timestamps, values, device_name, device_id = \
     CGM_data_extraction(out)
    return [timestamps, values], device_name, device_id
    
    
def union(a, b):
    """ return the union of two lists """
    return list(set(a) | set(b))

def convert_units(a):
    # converts from mg/dL to mm/L
    return a / 18.02
    
def convert_timestamps(a):
    # converts input timestamps to python timestamps
    # FIXME - this conversion is only approximate
    # Need to verify the CGM sorfware zero time
    return a + 41.9015 * 365 * 24 *3600