# -*- coding: utf-8 -*-
"""
Created on Fri Jun 15 21:34:27 2012

@author: alun
"""

#from optparse import make_option
from django.core.management.base import LabelCommand, CommandError
from analysis.models import DataFile, CGM
from datetime import datetime
import os
import csv

class Command(LabelCommand):
    args = '<path/to/datafiles/>'
    help = 'Imports the contents of the specified directory of spreadsheets and CSV files into the database'
    #option_list = LabelCommand.option_list + (
    #    make_option('--merge', action='store', dest='merge',
    #        default=False, help='Use this option to add this data to exisiting data, thus summing counts for records.'),
    #)

    def __init__(self):
        # Toggle debug statements on/off
        self.debug = False
        # Record basic information about the import process for reporting
        self.import_stats = {}
        super(Command, self).__init__()

    def _list_files(self, path):
        file_list = []
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.lower()[-4:] == ".tab":
                    file_list.append(os.path.abspath(os.path.join(root)+"/"+file)) # Yes, unix specific hack
        print "Files found: " + str(file_list)
        return file_list

    def handle_label(self, path, **options):
        print "Import started at " + str(datetime.utcnow()) + "\n"

        # Scan directory for files, compare them to names in the existing LogFile list. Import the first X new files.
        found_files_list = self._list_files(path)
        print "{} files have been found. Importing them now.".format(len(found_files_list))
        for filename in found_files_list:
            datafile_obj, created = self._datafile(filename)
            if created:
                print "\n\nImporting from %s" % filename

                # Start the parsing with the summary sheet
                self._parsefile(datafile_obj)
            else:
                print "\n\n%s - has already been imported" % filename

#            # Data imported, now do summary analysis
#            self._data_analysis()

        print "\nImport finished at " + str(datetime.utcnow())
        return None

    def _datafile(self, filename):
        """Get or create a LogFile record for the given filename"""
        datafile = {}

        # Test the log_service option is valid. Use the same list as LogFile.SOURCE_NAME_CHOICES
        # Guess the service based on the filename
        try:
            df = filename[filename.rindex('/')+1:]
        except ValueError:
            # Likely path doesn't feature any directories... so improvise
            df = filename
        if df.lower().find('.tab') > 0:
            datafile['source_name'] = 'cgmdf'
        else:
            raise CommandError("The source can not be determined from the filename.")

        try:
            datafile['file_name'] = filename[filename.rindex('/')+1:]
            datafile['file_path'] = filename[:filename.rindex('/')+1]
        except ValueError:
            # Likely path doesn't feature any directories... so improvise
            datafile['file_name'] = filename
            datafile['file_path'] = "./"

        datafile['last_updated'] = datetime.utcnow()

        obj, created = DataFile.objects.get_or_create(
            source_name = datafile.get('source_name'),
            file_name = datafile.get('file_name'),
            file_path = datafile.get('file_path'),
            defaults = datafile)

        obj.save()

        return obj, created

    def _parsefile(self, datafile_obj):
        filename = datafile_obj.file_path + datafile_obj.file_name

        datareader = csv.reader(open(filename), delimiter=';')
        # The data structure changes over time, and new columns are added (and perhaps removed) so map each file to a dictionary
        column_headers = []
        for i,row in enumerate(datareader):
#            if i > 1000:
#                continue

#            print "_parsefile(): line " + str(i) + ": " + str(row)
            if row[0].lower() == "DATEEVENT":
                for col, title in enumerate(row):
                    column_headers.append(title.lower())
            elif len(column_headers) > 2 and len(row[0])>8:
#                print column_headers
                row_dict = dict()
                for col, title in enumerate(column_headers):
                    row_dict[title] = row[col]
                self._parseline(row_dict, datafile_obj)

        return None

    def _parseline(self, entrydict, datafile_obj):
#        print "_parseline() called with: " + str(entrydict)
        cgm = dict()
        cgm["data_file"] = datafile_obj
        cgm["datetime"] = self._parse_timestamp(entrydict.get('DATEEVENT'))
        cgm["timeslot"] = self._cast('int', entrydict.get('I1'))
        cgm["event_type"] = self._cast('int', entrydict.get('I1'))
        cgm["device_model"] = entrydict.get('DEVICE_MODEL')
        cgm["device_id"] = entrydict.get('DEVICE_ID')
        cgm["v_ev_type"] = self._cast('int', entrydict.get('VENDOR_EVENT_TYPE_ID'))
        cgm["v_ev_id"] = entrydict.get('VENDOR_EVENT_ID')
        cgm["key0"] = self._cast('int', entrydict.get('KEY0'))
        cgm["key1"] = self._cast('int', entrydict.get('KEY1'))
        cgm["key2"] = self._cast('int', entrydict.get('KEY2'))
        cgm["I0"] = self._cast('int', entrydict.get('I0'))
        cgm["blood_glucose"] = self._cast('int', entrydict.get('I1'))
        cgm["I2"] = self._cast('int', entrydict.get('I2'))
        cgm["I3"] = self._cast('int', entrydict.get('I3'))
        cgm["I4"] = self._cast('int', entrydict.get('I4'))
        cgm["cal_flag"] = self._cast('int', entrydict.get('I5'))
        cgm["I6"] = self._cast('int', entrydict.get('I6'))
        cgm["I7"] = self._cast('int', entrydict.get('I7'))
        cgm["I8"] = self._cast('int', entrydict.get('I8'))
        cgm["I9"] = self._cast('int', entrydict.get('I9'))
        cgm["C0"] = entrydict.get('C0')
        cgm["C1"] =entrydict.get('C1')
        cgm["C2"] = self._cast('int', entrydict.get('C2'))
        cgm["ismanual"] = self._cast('int', entrydict.get('ISMANUAL'))
        cgm["comment"] = entrydict.get('COMMENT')

        created, obj = CGM.objects.get_or_create(
            datetime = cgm.get("datetime"),
            defaults = cgm
        )
        if created:
            obj.save()
        else:
            print "_parseline(): Duplicate record being imported"
            if obj.blood_glucose != cgm.get("blood_glucose"):
                print "The sky is falling! Blood Glucose does not match {0} vs {1}".format(
                    obj.blood_glucose,
                    cgm.get("blood_glucose")
                )

        return None

    def _cast(self, type, in_val):
        inputstring = str(in_val)
        if inputstring == 'None':
            return None
        elif inputstring.isspace():
            return None
        elif len(inputstring) > 0:
            if type == 'float':
                return float(inputstring.strip())
            else:
                return int(inputstring.strip())
        else:
            return None

    def _parse_timestamp(self,dt):
        ''' converts input timestamps to python timestamps
         The original data is in fractional days from 1/1/1900
         need to convert to number of seconds passed since 1/1/1970 '''
        num_since_epoc = 86400 * (dt - 25569)
        dt = datetime.fromtimestamp(num_since_epoc)
        return dt #"{0:%Y-%m-%d %H:%M:%S}".format(ts)

    def _convert_blood_glucose_uk(self, bg):
        val = self._cast('float',bg)
        if val:
            return val / 18.02
        else:
            return None