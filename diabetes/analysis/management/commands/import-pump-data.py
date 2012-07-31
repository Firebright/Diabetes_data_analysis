#from optparse import make_option
from django.core.management.base import LabelCommand, CommandError
from django.db.models import Avg, Count, Max, Min, StdDev, Sum, Variance

from analysis.models import DataFile, Pump, DailySummary, Events
from datetime import datetime, timedelta
import os
import time
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

            # Data imported, now do summary analysis
            self._data_analysis()

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
#            if i > 1000:
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
        if entrydict.get('bg control') == "X":
            return None

        pump = dict()
        pump["data_file"] = datafile_obj
        pump["datetime"] = self._parse_timestamp(entrydict.get('date'), entrydict.get('time'))
        pump["blood_glucose"] = self._cast('int', entrydict.get('bg (mg/dl)'))
        pump["bolus_pen"] = self._cast('float', entrydict.get('insulin1 (units)'))
        pump["insulin2"] = self._cast('float', entrydict.get('insulin2 (units)'))
        pump["insulin3"] = self._cast('float', entrydict.get('insulin3 (units)'))
        pump["bolus_pump"] = self._cast('float', entrydict.get('insulin pump (units)'))
        pump["control_solutions"] = entrydict.get('bg control')
        pump["bg_lab"] = self._cast('int', entrydict.get('bg lab (mg/dl)'))
        pump["carbs"] = self._cast('int', entrydict.get('carbohydrates (g)'))
        pump["system_defined_events"] = entrydict.get('system-defined events')
        pump["hba1c"] = self._cast('float', entrydict.get('hba1c (percent)'))
        pump["hba1"] = self._cast('float', entrydict.get('hba1 (percent)'))
        pump["ketones"] = self._cast('float', entrydict.get('ketones'))
        pump["weight"] = self._cast('float', entrydict.get('weight (kg)'))
        pump["height"] = self._cast('float', entrydict.get('height (cm)'))
        pump["blood_pressure_systolic"] = self._cast('int', entrydict.get('blood pressure (systolic) (kpa)'))
        pump["blood_pressure_diastolic"] = self._cast('int', entrydict.get('blood pressure (diastolic) (kpa)'))
        pump["pulse"] = self._cast('int', entrydict.get('pulse (bpm)'))
        pump["basal"] = self._cast('float', entrydict.get('insulin rate (units/hour)'))
        pump["insulin_tdd"] = self._cast('float', entrydict.get('insulin tdd (units)'))

        obj, created = Pump.objects.get_or_create(
            datetime = pump.get("datetime"),
            defaults = pump
        )
        if created:
            obj.save()
        else:
            print "_parseline(): Duplicate record being imported"
            if obj.blood_glucose != pump.get("blood_glucose"):
                print "The sky is falling! Blood Glucose does not match {0} vs {1}".format(
                    obj.blood_glucose,
                    pump.get("blood_glucose")
                )
            if obj.bolus_pen != pump.get("bolus_pen"):
                print "Different values of bolus. Leaving for now until we get a better idea how to deal with this."
            if obj.bolus_pump != pump.get("bolus_pump"):
                print "Different values of bolus. Leaving for now until we get a better idea how to deal with this."

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

    def _parse_timestamp(self,d, f):
        """Adjust timestamp supplied to GMT and returns a datetime object"""
#
#        class UTC(datetime.tzinfo):
#            """UTC"""
#
#            def utcoffset(self, dt):
#                return ZERO
#
#            def tzname(self, dt):
#                return "UTC"
#
#            def dst(self, dt):
#                return ZERO


        initialstring = d + ' ' + f
        print "_parse_timestamp():" + initialstring
        input_format = "%m/%d/%Y %H:%M:%S"
        base_time = time.strptime(initialstring,input_format)
        dt = datetime.utcfromtimestamp(time.mktime(base_time)) #.replace(tzinfo=UTC)
        return dt #"{0:%Y-%m-%d %H:%M:%S}".format(ts)

    def _data_analysis(self):
        """
        Describe what's going on here....
        """
        self._generate_daily_summaries()
        self._generate_events()
        return None

    def _generate_daily_summaries(self):
        # Find the earliest date(time) in the dataset, use this as our Day 0
        # Create a loop of dates
        try:
            day0 = Pump.objects.order_by('datetime')[0]
            day_end = Pump.objects.order_by('-datetime')[0]
        except IndexError:
            return None
        start_date = day0.datetime.replace(hour=0, minute=0,second=0,microsecond=0)
        end_date = start_date + timedelta(days = 1)

        while day_end.datetime > end_date:
#            print "_generate_daily_summaries(): start date: {0} - {1}".format(start_date, end_date)
            ds_obj = DailySummary()
            ds_obj.date = start_date
            ds_obj.carbs_consumed = self._cast(
                'int',
                Pump.objects.filter(
                    datetime__lt=end_date,
                    datetime__gt=start_date,
                    carbs__isnull=False
                ).aggregate(
                    Sum('carbs')
                ).get('carbs__sum')
            )
            ds_obj.bolus_pen = self._cast(
                'float',
                Pump.objects.filter(
                    datetime__lt=end_date,
                    datetime__gt=start_date,
                    bolus_pen__isnull=False
                ).aggregate(
                    Sum('bolus_pen')
                ).get('bolus_pen__sum')
            )
            ds_obj.bolus_pump = self._cast(
                'float',
                Pump.objects.filter(
                    datetime__lt=end_date,
                    datetime__gt=start_date,
                    bolus_pump__isnull=False
                ).aggregate(
                    Sum('bolus_pump')
                ).get('bolus_pump__sum')
            )
            ds_obj.basal = self._basal_total_calc(start_date, end_date)
            ds_obj.bg_max = self._convert_blood_glucose_uk(
                Pump.objects.filter(
                    datetime__lt=end_date,
                    datetime__gt=start_date,
                    blood_glucose__isnull=False
                ).aggregate(
                    Max('blood_glucose')
                ).get('blood_glucose__max')
            )
            ds_obj.bg_min = self._convert_blood_glucose_uk(
                Pump.objects.filter(
                    datetime__lt=end_date,
                    datetime__gt=start_date,
                    blood_glucose__isnull=False
                ).aggregate(
                    Min('blood_glucose')
                ).get('blood_glucose__min')
            )
            ds_obj.bg_mean = self._convert_blood_glucose_uk(
                Pump.objects.filter(
                    datetime__lt=end_date,
                    datetime__gt=start_date,
                    blood_glucose__isnull=False
                ).aggregate(
                    Avg('blood_glucose')
                ).get('blood_glucose__avg')
            )
            ds_obj.bg_std = self._convert_blood_glucose_uk(
                Pump.objects.filter(
                    datetime__lt=end_date,
                    datetime__gt=start_date,
                    blood_glucose__isnull=False
                ).aggregate(
                    StdDev('blood_glucose')
                ).get('blood_glucose__stddev')
            )
            ds_obj.number_of_datapoints = self._cast(
                'int',
                Pump.objects.filter(
                    datetime__lt=end_date,
                    datetime__gt=start_date
                ).aggregate(
                    Count('datetime')
                ).get('datetime__count')
            )
            ds_obj.number_of_bg_test = self._cast(
                'int',
                Pump.objects.filter(
                    datetime__lt=end_date,
                    datetime__gt=start_date,
                    blood_glucose__isnull=False
                ).aggregate(
                    Count('blood_glucose')
                ).get('blood_glucose__count')
            )
            ds_obj.number_of_bolus_pen = self._cast(
                'int',
                Pump.objects.filter(
                    datetime__lt=end_date,
                    datetime__gt=start_date,
                    bolus_pen__isnull=False
                ).aggregate(
                    Count('bolus_pen')
                ).get('bolus_pen__count')
            )
            ds_obj.number_of_bolus_pump = self._cast(
                'int',
                Pump.objects.filter(
                    datetime__lt=end_date,
                    datetime__gt=start_date,
                    bolus_pump__isnull=False
                ).aggregate(
                    Count('bolus_pump')
                ).get('bolus_pump__count')
            )
            ds_obj.save()

            start_date = end_date
            end_date = start_date + timedelta(days = 1)

        return None

    def _basal_total_calc(self,sd, ed):
        """
        Calculate the basal total for the day, but make it accurate to the second, rather than microsecond.
        """
        basal_list = []
        for record in Pump.objects.filter(datetime__lt=ed, datetime__gt=sd, basal__isnull=False).order_by('datetime'):
            basal_list.append((record.datetime.replace(microsecond=0), record.basal))
        try:
            obj = Pump.objects.filter(datetime__lt=sd, basal__isnull=False).order_by('-datetime')[0]
            basal_list.insert(0, (obj.datetime.replace(microsecond=0), obj.basal))
        except IndexError:
            return 0.0
        # 86400 seconds in a day
        if len(basal_list) < 2:
            return 0.0
        previous = basal_list[1]
        hours_so_far = 0
        basal_so_far = 0.0
        for item in basal_list[2:]:
            duration = (item[0]-previous[0]).total_seconds()/3600.
            basal_so_far += float(previous[1] * duration)
            hours_so_far += duration
            previous = item
#            print 'basal_total_calc(): in loop item {0} duration {1} basal so for {2} hours so far {3}'.format(item, duration, basal_so_far, hours_so_far)
        # now calculate the duration of the last datapoint
        duration = (ed - basal_list[-1][0]).total_seconds()/3600.
        basal_so_far += basal_list[-1][1] * duration
        hours_so_far += duration
#        print 'basal_total_calc() last point:  item {0} duration {1} basal so for {2} hours so far {3}'.format(basal_list[-1], duration, basal_so_far, hours_so_far)
        # now add on the basal from the previous day's last value for the remaining time
        basal_so_far += float(basal_list[0][1] * (24-hours_so_far))
#        print 'basal_total_calc() first point: basal_so_far {0}, remaining duration {1}'.format(basal_so_far, 24-hours_so_far)
        return float(basal_so_far)

    def _convert_blood_glucose_uk(self, bg):
        val = self._cast('float',bg)
        if val:
            return val / 18.02
        else:
            return None

    def _generate_events(self):
        return None
