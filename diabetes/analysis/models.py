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