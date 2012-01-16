# -*- coding: utf-8 -*-
"""
Created on Mon Jan 16 17:06:12 2012

@author: afdm76
"""
from locate_data import dir_list_gen
import numpy

def CGM_data_extraction(data_in):
    wj = 1
    dl = len(data_in)
    
    timestamp_in = data_in[0:2:-1]
    CGM_in = data_in[1:2:-1]
    
    # setting up the intial vectors
    timestamp_data = numpy.zeros((dl/2,1))
    CGM_values = numpy.zeros((dl/2,1))
    
    for rh in range(dl/2):
        if not data_in[rh]:
            continue
        if timestamp_in[rh]:
            # good time data
            # conditioning the timestamp
            timestamp_data[wj] = (timestamp_in[rh]) + 693961
            # getting the CGM values (if valid)
            if (CGM_in[rh]):
                # convert from mg/dL to mm/L
                mm = (CGM_in[rh])/18.02
                if mm> 0.2:
                    CGM_values[wj] = mm
            wj = wj +1
    # sorting to make sure timestamps are only increasing
    # [timestamp_data, sorting_ind] = sort(timestamp_data)
    # carbs_values = carbs_values(sorting_ind)
    
    # removing the data times which have no bg data
    CGM_values[numpy.isnan(timestamp_data)==1] =[]
    timestamp_data[numpy.isnan(timestamp_data)==1] =[]
    timestamp_data[numpy.isnan(CGM_values)==1] =[]
    CGM_values[numpy.isnan(CGM_values)==1] =[]
    # taking the unique timestamps
    timestamp_data, CGM_ind = numpy.unique(timestamp_data)
    CGM_values = CGM_values(CGM_ind)
    return [timestamp_data, CGM_values]
    
def get_CGM_data(dir_path):
    lst = dir_list_gen(dir_path,'TAB')
    out = []
    for kn in range(len(lst)):
        [temp[:,0],temp[:,1]]= textread(lst[kn],['#f',\
            '#*s#*s#*s#*s#*s#*s#u#*s#*s#*s#*s#*s#*s#*s#*s#*s#*s#*s#*s#*s',\
            '#*s#*s#*s#*s#*s#*s#*s#*s#*s#*s#*s#*s#*s#*s#*s'],\
            'headerlines',2, 'delimiter','\t')
        out = concatenate(1,out,temp)
    
    #remove data with empty timestamps, empty data, or 
    # where the value is <3 as this is a bogus placeholder.
    ind1 = numpy.nonzero(not out[:,0])
    ind2 = numpy.nonzero(not out[:,1])
    ind3 = numpy.nonzero(out[:,1]< 4)
    ind = numpy.union(ind1,ind2)
    ind = numpy.union(ind,ind3)
    out[ind,:] = []
    # convert from mg/dL to mm/L
    out[:,1] = out[:,1]/18
    # correct the time stamp need to add 1900 to the year and subtract one day
    a = datevec(out[:,0])
    a[:,0] = a[:,0] + 1900
    a[:,2] = a[:,2] - 1
    
    out[:,0] = datenum(a)
    return out