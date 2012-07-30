from django.db import models

# Create your models here.
class DataFile(models.Model):
    SOURCE_NAME_CHOICES = (
        (u'pdcsv', u'Pump csv data file'),
        (u'pdxls', u'Pump xls data file'),
        (u'cgmdf', u'CGM data file'),
        )
    source_name = models.CharField("source name associated with this log", max_length=20, choices=SOURCE_NAME_CHOICES)
    file_name = models.TextField("file name")
    file_path = models.TextField("path to file")
    last_updated = models.DateTimeField("last updated") # Acts as date of import

    def __unicode__(self):
        return self.file_name

class CGM(models.Model):
    data_file = models.ForeignKey(DataFile)
    datetime = models.DateTimeField()    #DATEEVENT
    timeslot = models.IntegerField(null=True, blank=True)#TIMESLOT
    event_type = models.IntegerField(null=True, blank=True)#EVENTTYPE
    device_model = models.CharField(null=True, blank=True, max_length=50)#DEVICE_MODEL
    device_id = models.CharField(null=True, blank=True, max_length=50)#DEVICE_ID	
    v_ev_type = models.IntegerField(null=True, blank=True)#VENDOR_EVENT_TYPE_ID	
    v_ev_id =  models.IntegerField(null=True, blank=True)#VENDOR_EVENT_ID	
    key0 = models.IntegerField(null=True, blank=True)#KEY0	
    key1 = models.IntegerField(null=True, blank=True)#KEY1	
    key2 = models.IntegerField(null=True, blank=True)#KEY2	
    I0 = models.IntegerField(null=True, blank=True)#I0	
    blood_glucose = models.IntegerField(null=True, blank=True)#I1	
    I2 = models.IntegerField(null=True, blank=True)#I2	
    I3 = models.IntegerField(null=True, blank=True)#I3	
    I4 = models.IntegerField(null=True, blank=True)#I4	
    cal_flag = models.IntegerField(null=True, blank=True)#I5	
    I6 = models.IntegerField(null=True, blank=True)#I6	
    I7 = models.IntegerField(null=True, blank=True)#I7	
    I8 = models.IntegerField(null=True, blank=True)#I8	
    I9 = models.IntegerField(null=True, blank=True)#I9	
    #D0	
    #D1	
    #D2	
    #D3	
    #D4	
    C0 = models.CharField(null=True, blank=True, max_length=50)#C0	
    C1 = models.CharField(null=True, blank=True, max_length=50)#C1	
    C2 = models.IntegerField(null=True, blank=True)    #C2	
    #C3	
    #C4	
    #C5	
    #C6	
    #C7	
    #C8	
    #C9	
    ismanual = models.IntegerField(null=True, blank=True)#ISMANUAL
    comment = models.CharField(null=True, blank=True, max_length=50)#COMMENT
    
    @property
    def blood_glucose_uk(self):
        return float(self.blood_glucose) / 18.02

        
class Pump(models.Model):
    data_file = models.ForeignKey(DataFile)
    datetime = models.DateTimeField()#    Date
#Time
    blood_glucose = models.IntegerField(null=True, blank=True)#bG (mg/dL)
    bolus_pen = models.FloatField(null=True, blank=True)#Insulin1 (units)
    insulin2 = models.FloatField(null=True, blank=True)#Insulin2 (units)
    insulin3 = models.FloatField(null=True, blank=True)#Insulin3 (units)
    bolus_pump = models.FloatField(null=True, blank=True)#Insulin Pump (units)
    control_solutions = models.CharField(null=True, blank=True, max_length=1)#bG Control
    bg_lab = models.IntegerField(null=True, blank=True)#bG Lab (mg/dL)
    carbs = models.IntegerField(null=True, blank=True)#Carbohydrates (g)
    #Exercise Duration (Minutes)
    #Exercise Intensity
    system_defined_events = models.CharField(null=True, blank=True, max_length=50)#System-Defined Events
    #User-Defined Events
    #Flags
    #Medication Name
    #Medication Dosage
    #Start Date
    #End Date
    #Comments
    #Description
    #Administered By
    #Education Comments
    #Visit Note Created Date
    #Visit Note
    #Visit Note Originated By
    #Visit Note Attachment URLs
    #Region
    #Severity
    #Symptoms 1
    #Symptoms 2
    #Symptoms 3
    #Findings
    #Comments
    #Albumin (mg/L)
    #Cholesterol (mg/dL)
    #Chol HDL (mg/dL)
    #Chol LDL (mg/dL)
    #Chol Ratio
    #Creatinine (micromols/L)
    #Fructosamine (micromols/L)
    hba1c = models.FloatField(null=True, blank=True)#HbA1c (Percent)
    hba1 = models.FloatField(null=True, blank=True)#HbA1 (Percent)
    ketones = models.FloatField(null=True, blank=True)#Ketones
    #Micral
    #Proteinuria (mg/dL)
    #Temperature (Degrees C)
    #Tryglycerides (mg/dL)
    weight = models.FloatField(null=True, blank=True)#Weight (kg)
    height = models.FloatField(null=True, blank=True)#Height (cm)
    blood_pressure_systolic = models.IntegerField(null=True, blank=True)#Blood Pressure (Systolic) (kPa)
    blood_pressure_diastolic = models.IntegerField(null=True, blank=True)#Blood Pressure (Diastolic) (kPa)
    pulse = models.IntegerField(null=True, blank=True)#Pulse (BPM)
    basal = models.FloatField(null=True, blank=True)#Insulin Rate (units/Hour)
    insulin_tdd = models.FloatField(null=True, blank=True)#Insulin TDD (units)

    @property
    def blood_glucose_uk(self):
        return float(self.blood_glucose) / 18.02


class Events(models.Model):
    """
    Events are a collection of Pump records that match a specific pattern
    """
    TYPE_CHOICES = (
        (u'bgh1', u'Blood Glucose High'),
        (u'bgh2', u'Blood Glucose Very High'),
        (u'bgh3', u'Blood Glucose Extremely High'),
        (u'bgok', u'Blood Glucose in normal range'),
        (u'bgwarn', u'Blood Glucose Low Warning'),
        (u'bgl1', u'Blood Glucose Low'),
        (u'', u''),
    )
    start = models.DateTimeField()
    stop = models.DateTimeField()
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    discovery = models.ForeignKey(Pump)
    number_of_datapoints = models.IntegerField() # Store the number of datapoints that this was calculated from

    @property
    def duration(self):
        return self.stop - self.start

    @property
    def recovery(self):
        return self.stop - self.discovery.datetime


class DailySummary(models.Model):
    """
    Records a daily summary of Pump data after analysis
    """
    date = models.DateField()
    carbs_consumed = models.IntegerField(null=True, blank=True) # Total number of grams of carbohydrate consumed in a day
    bolus_pen = models.FloatField(null=True, blank=True) # Total units of pen bolus insulin given in a day
    bolus_pump = models.FloatField(null=True, blank=True) # Total units of pump bolus insulin given in a day
    basal = models.FloatField(null=True, blank=True) # Total units of basal insulin given in a day
    bg_max = models.FloatField(null=True, blank=True) # Maximum level of Blood glucose in this day
    bg_min = models.FloatField(null=True, blank=True) # Minimum level of Blood glucose in this day
    bg_mean = models.FloatField(null=True, blank=True) # Average level of Blood glucose in this day
    bg_std = models.FloatField(null=True, blank=True) # Standard deviation of Blood glucose readings in this day
    number_of_datapoints = models.IntegerField(null=True, blank=True) # Store the number of datapoints that this was calculated from
    number_of_bg_test = models.IntegerField(null=True, blank=True) # Store the number of pump records containing bg readings
    number_of_bolus_pen = models.IntegerField(null=True, blank=True)
    number_of_bolus_pump = models.IntegerField(null=True, blank=True)
