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
#<<<<<<< HEAD
    timestamps = data_in[0][2:]
    values = data_in[11][2:]
    cal_flag = data_in[15][2:]
    # convert to floats from strings
    cal_flag = map(float, cal_flag)
    values = map(float, values)
    timestamps = map(float, timestamps)
    # correct the time stamp
    timestamps = map(convert_timestamps, timestamps)
    #ind1 = numpy.nonzero(not timestamps)
    #ind2 = numpy.nonzero(not values)
    ind1 = numpy.nonzero(numpy.array(values) < 4.)
    ind2 = numpy.nonzero(numpy.array(cal_flag) == 0.0)  
    ind = numpy.concatenate((ind1[0],ind2[0]), axis=0)   
    #ind = union(list(ind1), list(ind2))
    #ind = union(ind, ind3)
    ind = numpy.unique(ind)
#=======
#    timestamps = data_in[0][2:]
#    values = data_in[11][2:]
#    # shows when the cal cycle is on and data is not valid
#    cal_flag = data_in[15][2:]
#    # convert to floats from strings
#    values = map(numpy.float64, values)
#    timestamps = map(numpy.float64, timestamps)
#    cal_flag = map(numpy.int, cal_flag)
#    ind1 = numpy.nonzero(not timestamps)
#    ind2 = numpy.nonzero(not values)
#    ind3 = numpy.nonzero(values < 4)
#    ind4 = numpy.nonzero(cal_flag == 0)
#    ind = union(ind1, ind2)
#    ind = union(ind, ind3)
#    ind = union(ind, ind4)
#    ind.sort()
#>>>>>>> 97b95ee51caa8ce5ab8ad4630ba6fff30fdb136c
    # Makes sure the indicies are deleated from the bottom up.
    ind = ind[::-1]
    for ne in range(len(ind)):   
        del timestamps[ind[ne]]
        del values[ind[ne]]
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
    return [numpy.array(timestamps), numpy.array(values)], \
            device_name, device_id
    

def convert_units(a):
#<<<<<<< HEAD
    ''' converts from mg/dL to mm/L'''
    return a / 18.02
    
def convert_timestamps(a):
    ''' converts input timestamps to python timestamps
     The original data is in fractional days from 1/1/1900
     need to convert to number of seconds passed since 1/1/1970 '''
    return 86400 * (a - 25569)