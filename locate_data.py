# -*- coding: utf-8 -*-
"""
Created on Mon Jan 16 16:58:44 2012

@author: afdm76
"""
import os

def dir_list_gen(directory_name, file_type):
    '''Takes in a directory name and outputs the list of files
     filtered by file type. '''     
    lst = os.listdir(directory_name)
    if not lst:
        print 'Directory does not exist'
        return None
    names = []
    for fas in range(len(lst)):
        full_path = os.path.join(directory_name, lst[fas])
        if os.path.isfile(full_path) and lst[fas].endswith(file_type):
            names.append(full_path)
    return names