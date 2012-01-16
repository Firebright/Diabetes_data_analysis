# -*- coding: utf-8 -*-
"""
Created on Mon Jan 16 16:46:16 2012

@author: afdm76
"""
import xlrd
import re
from locate_data import dir_list_gen
import numpy

def import_module_xls(dir_path):
    '''Reads in data from an xls spreadsheet and 
    returns the relavent data in lists.'''
    # Initialise return values
    bolusdates = []
    bolustimes = []
    bolusdata = []
    basaldates = []
    basaltimes = []
    basaldata = []
    basaladju = []
    basaladjl = []
    bgdates = []
    bgtimes = []
    bgdata = []
    carbsdata = []
    eventsdates = []
    eventstimes = []
    eventsdata = []
    # find the relavent files
    lst = dir_list_gen(dir_path,'xls')
    for legr in lst:
        book = xlrd.open_workbook(legr)
        sheet_list = book.sheets()
        for pages in range(len(sheet_list)):
            page = book.sheet_by_index(pages)
            n_cols = page.ncols
            n_rows = page.nrows
            temp_sheet = []    
            if n_cols > 0 and n_rows > 0:
                for col in range(n_cols):
             # generate a list of lists to represent the row and column data.
                    temp_sheet.append(
                     page.col_values(col, start_rowx=0, end_rowx=n_rows))
                loc_bolus = index(temp_sheet[0],'Bolus')
                loc_basal = index(temp_sheet[0],'Basal')
                loc_bg = index(temp_sheet[0],'Evaluated results')
                loc_events = index(temp_sheet[0],'Events')
                # find out which sets of data are on the current sheet.
                section_list = [loc_bolus, loc_basal, loc_bg, loc_events]
                section_names = ['Bolus', 'Basal', 'BG', 'Events']
                index_dict = dict(zip(section_list, section_names))
                revindex_dict = dict(zip(section_names, section_list))
                name = sorted_dict_values(index_dict)
                name_dict = dict(zip(name, [0, 1, 2, 3]))
                revname_dict = dict(zip([0, 1, 2, 3], name))
 
                if loc_bolus != None:
                    bolusdates, bolustimes, bolusdata = xls_get_bolus(
                                temp_sheet, bolusdates, bolustimes, 
                                bolusdata, page, loc_bolus, name_dict, 
                                revindex_dict, revname_dict, n_cols)   
                if loc_basal != None:
                    basaldates, basaltimes, basaldata, basaladju, basaladjl = \
                        xls_get_basal(
                                temp_sheet, basaldates, basaltimes, 
                                basaldata, basaladju, basaladjl,
                                page, loc_basal, 
                                name_dict, revindex_dict, revname_dict, n_cols)
                if loc_bg != None:
                    bgdates, bgtimes, bgdata, carbsdata = xls_get_bg(
                                temp_sheet, bgdates, bgtimes, bgdata, 
                                carbsdata, page, 
                                loc_bg, name_dict, revindex_dict, 
                                revname_dict, n_cols)
                if loc_events != None:
                    eventsdates, eventstimes, eventsdata =  xls_get_events(
                                   temp_sheet, eventsdates, eventstimes, 
                                   eventsdata, page, loc_events, 
                                   name_dict, revindex_dict, \
                                   revname_dict, n_cols)
    
    bolusstream = xls_condition_input(bolusdates, bolustimes, bolusdata)
    basalstream = xls_condition_input(basaldates, basaltimes, basaldata)
    basaladjustream = xls_condition_input(basaldates, basaltimes, basaladju)
    basaladjlstream = xls_condition_input(basaldates, basaltimes, basaladjl)
    bgstream = xls_condition_input(bgdates, bgtimes, bgdata)
    carbstream = xls_condition_input(bgdates, bgtimes, carbsdata) 
    eventstream = xls_condition_input(eventsdates, eventstimes, eventsdata)
    return bolusstream, basalstream, basaladjustream, basaladjlstream, \
            bgstream, carbstream, eventstream
            
def xls_get_bolus(temp_sheet, bolusdates, bolustimes, bolusdata, page, 
                  loc_bolus, name_dict, revindex_dict, revname_dict, n_cols):
    '''Takes the xls formatted data and outputs lists of 
    date time and bolus data.'''
    bolus_header = page.row_values(loc_bolus +2, start_colx=0, end_colx=n_cols)
    # Contains Bolus data
    section_number = name_dict['Bolus']
    try:
        next_section = revindex_dict[
                        revname_dict[section_number +1]]
    except:
        next_section = -1
    # Setting the row at which the data starts.
    bolus_data_start = loc_bolus +4
    # find the collumns containing required data
    try:
        bolusdates.extend(
         temp_sheet[index(bolus_header,'Date')]
         [bolus_data_start:next_section])
        bolustimes.extend(
         temp_sheet[index(bolus_header,'Time')]
         [bolus_data_start:next_section])
        bolusdata.extend(
         temp_sheet[index(bolus_header,'U')]
         [bolus_data_start:next_section])
    except:
        pass
    return bolusdates, bolustimes, bolusdata

def xls_get_basal(temp_sheet, basaldates, basaltimes, basaldata, basaladju, 
                  basaladjl, page, 
                  loc_basal, name_dict, revindex_dict, revname_dict, n_cols):
    '''Takes the xls formatted data and outputs lists of 
    date time and basal data.'''
    # Contains Basal data
    basal_header = page.row_values(
                loc_basal +2, start_colx=0, end_colx=n_cols)
    section_number = name_dict['Basal']
    try:
        next_section = revindex_dict[
                        revname_dict[section_number +1]]
    except:
        next_section = -1
    # Setting the row at which the data starts
    basal_data_start = loc_basal +4
    # find the collumns containing required data
    try:
        basaldates.extend(
            temp_sheet[index(basal_header,r'Date')]
            [basal_data_start:next_section])
        basaltimes.extend(
            temp_sheet[index(basal_header,r'Time')]
            [basal_data_start:next_section])
        basaldata.extend(
            temp_sheet[index(basal_header,r'Basal Rate')]
            [basal_data_start:next_section])
        basaladju.extend(
            temp_sheet[index(basal_header,r'Basal Rate')+2]
            [basal_data_start:next_section])
        basaladjl.extend(
            temp_sheet[index(basal_header,r'Basal Rate')+3]
            [basal_data_start:next_section])
    except:
        pass
    return basaldates, basaltimes, basaldata, basaladju, basaladjl

def xls_get_bg(temp_sheet, bgdates, bgtimes, bgdata, carbsdata, page, 
                  loc_bg, name_dict, revindex_dict, revname_dict, n_cols):
    '''Takes the xls formatted data and outputs lists of 
    date time blood glucose data and data on amount of carbs eaten.'''
     # Contains bg data
    bg_header = page.row_values(
                    loc_bg +2, start_colx=0, end_colx=n_cols)
    section_number = name_dict['BG']
    try:
        next_section = revindex_dict[
                        revname_dict[section_number +1]]
    except:
        next_section = -1
    # Setting the row at which the data starts.
    bg_data_start = loc_bg +4
    # find the collumns containing required data
    try:
        bgdates.extend(
            temp_sheet[index(bg_header,r'Date')]
            [bg_data_start:next_section])
        bgtimes.extend(
            temp_sheet[index(bg_header,r'Time')]
            [bg_data_start:next_section])
        bgdata.extend(
            temp_sheet[index(bg_header,r'Glucose')]
            [bg_data_start:next_section])
        carbsdata.extend(
            temp_sheet[index(bg_header,r'[g]')]
            [bg_data_start:next_section])
    except:
        pass
    return bgdates, bgtimes, bgdata, carbsdata

def xls_get_events(temp_sheet, eventsdates, eventstimes, eventsdata, page, 
                  loc_events, name_dict, revindex_dict, revname_dict, n_cols):
    '''Takes the xls formatted data and outputs lists of 
    date time and event data.'''
    # Only contains Events data
    events_header = page.row_values(
                        loc_events +2, 
                        start_colx=0, end_colx=n_cols)
    section_number = name_dict['Events']
    try:
        next_section = revindex_dict[
                        revname_dict[section_number +1]]
    except:
        next_section = -1
    # Setting the row at which the data starts.
    events_data_start = loc_events +4
    # find the collumns containing required data
    try:
        eventsdates.extend(
            temp_sheet[index(events_header,'Date')]
            [events_data_start:next_section])
        eventstimes.extend(
            temp_sheet[index(events_header,'Time')]
            [events_data_start:next_section])
        eventsdata.extend(
            temp_sheet[index(events_header,'Description')]
            [events_data_start:next_section])
    except:
        pass
    return eventsdates, eventstimes, eventsdata

def xls_convert_timestamps(xls_ts):
    '''converts from microsoft xls timestamps to python timestamps.'''
    return (xls_ts -70*365 -19)*24*3600 
    
def index(seq, func):
    """Return the index of the first item in seq where func(item) == True."""
    test = re.compile(func)
    for i in range(len(seq)):
        if test.search(seq[i]) != None:
            return i
    return None

def sorted_dict_values(adict):
    '''Sorts the keys of a dictionary and returns the values in that order.'''
    items = adict.items()
    items.sort()
    return [value for key, value in items]
    
def xls_condition_input(date_in, time_in, data_in):
    ''' Takes a vector of dates, times and input data and outputs a list
    of timestamps and data. Any entries with invalid dates, time or data
    are removed.'''
    ts_out = []
    data_out = []
#    print 'data length', len(date_in)
    for ksh in range(len(date_in)):
        # sets the empty cells of the input spreadsheet to None so that the 
        # output stream only contains valid data.
        if data_in[ksh] == '---' or data_in[ksh] == '\xa0':
            data_in[ksh] = None
        # check if there is a valid time
        if type(date_in[ksh]) != float:
            try:                                
                t_date = float(date_in[ksh])
            except:
                t_date = None
        else:
            t_date = date_in[ksh]
        if type(time_in) != float:
            try:   
                t_time = float(time_in[ksh])
            except:
                t_time = None
        else:
            t_time = time_in[ksh]
        if t_date != None and t_time != None and data_in[ksh] != None:
            ts_out.extend([xls_convert_timestamps(t_date + t_time)])  
            data_out.extend([data_in[ksh]])
    # Remove duplicate timestamps
    ts_out , indices = numpy.unique(numpy.array(ts_out), return_index=True)
    data_out = numpy.array(data_out)[indices]
    indices2 = numpy.argsort(ts_out)
    stream = [ts_out[indices2], data_out[indices2]]
    return stream