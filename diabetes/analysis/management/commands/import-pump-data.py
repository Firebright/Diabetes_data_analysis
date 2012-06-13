#from optparse import make_option
from django.core.management.base import LabelCommand, CommandError

from analysis.models import DataFile, Pump
#from xlrd import open_workbook, biffh
from datetime import datetime
import os
import time, csv

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
                if file.lower()[-4:] == ".xls" or file.lower()[-4:] == ".csv":
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
        if df.lower().find('.csv') > 0:
            datafile['source_name'] = 'pdcsv'
        elif df.lower().find('.xls') > 0:
            datafile['source_name'] = 'pdxls'
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
#            if i > 100:
#                continue

#            print "_parsefile(): line " + str(i) + ": " + str(row)
            if row[0].lower() == "date":
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
        pump = Pump()
        pump.data_file = datafile_obj
        pump.datetime = self._parse_timestamp(entrydict.get('date'), entrydict.get('time'))
        pump.blood_glucose = self._cast('int', entrydict.get('bg (mg/dl)'))
        pump.bolus_pen = self._cast('float', entrydict.get('insulin1 (units)'))
        pump.insulin2 = self._cast('float', entrydict.get('insulin2 (units)'))
        pump.insulin3 = self._cast('float', entrydict.get('insulin3 (units)'))
        pump.bolus_pump = self._cast('float', entrydict.get('insulin pump (units)'))
        pump.control_solutions = entrydict.get('bg control')
        pump.bg_lab = self._cast('int', entrydict.get('bg lab (mg/dl)'))
        pump.carbs = self._cast('int', entrydict.get('carbohydrates (g)'))
        pump.system_defined_events = entrydict.get('system-defined events')
        pump.hba1c = self._cast('float', entrydict.get('hba1c (percent)'))
        pump.hba1 = self._cast('float', entrydict.get('hba1 (percent)'))
        pump.ketones = self._cast('float', entrydict.get('ketones'))
        pump.weight = self._cast('float', entrydict.get('weight (kg)'))
        pump.height = self._cast('float', entrydict.get('height (cm)'))
        pump.blood_pressure_systolic = self._cast('int', entrydict.get('blood pressure (systolic) (kpa)'))
        pump.blood_pressure_diastolic = self._cast('int', entrydict.get('blood pressure (diastolic) (kpa)'))
        pump.pulse = self._cast('int', entrydict.get('pulse (bpm)'))
        pump.basal = self._cast('float', entrydict.get('insulin rate (units/hour)'))
        pump.insulin_tdd = self._cast('float', entrydict.get('insulin tdd (units)'))
        pump.save(force_insert=True)

        return None


    def _cast(self, type, inputstring):
        if inputstring is None:
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


    def _parse_timestamp(self,d, f):
        """Adjust timestamp supplied to GMT and returns a datetime object"""
        initialstring = d + ' ' + f
        print "_parse_timestamp():" + initialstring
        input_format = "%m/%d/%Y %H:%M:%S"
        base_time = time.strptime(initialstring,input_format)
        dt = datetime.fromtimestamp(time.mktime(base_time))
        return dt #"{0:%Y-%m-%d %H:%M:%S}".format(ts)