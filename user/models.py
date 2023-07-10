from django.db import models
from django.contrib.auth.models import User

# Create your models here.
gender =(
    ('Male', 'Male'), 
    ('Female', 'Female'),
    ('Not Specify', 'Not Specify'),)

title =(
    ('Mr', 'Mr'), 
    ('Mrs', 'Mrs'),
    ('Miss', 'Miss'),
    ('Ms', 'Ms'),
    ('Dr', 'Dr'),
    ('Prof', 'Prof'),
    ('Rev', 'Rev'),)
wkStatus =(
    ('Employee', 'Employee'), 
    ('Goverment Employee', 'Goverment Employee'),
    ('Private Employee', 'Private Employee'),
    ('Owner', 'Owner'),
    ('Student', 'Student'),
    ('Overseas worker', 'Overseas worker'),
    ('Pensioner', 'Pensioner'),
    ('Unemployed', 'Unemployed'),
    )

class ScannedFile(models.Model):
    file = models.FileField(upload_to='scanned_files/')

class Officer(models.Model):
    firstName = models.CharField(max_length=100)
    secondName = models.CharField(max_length=100)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True )
    ld_id = models.IntegerField(unique=True)
    gender = models.CharField(max_length=50, choices=gender, null=True)
    phone = models.IntegerField()
    mail = models.EmailField()
    dob = models.DateField(null=True)

    def __str__(self):
        return f'{self.firstName}'
    
class Member(models.Model):
    firstName = models.CharField(max_length=100)
    secondName = models.CharField(max_length=100)
    te_id = models.IntegerField(unique=True)
    gender = models.CharField(max_length=50, choices=gender, null=True)
    title = models.CharField(max_length=50, choices=title, null=True)
    phone = models.IntegerField(unique=True)
    mail = models.EmailField(null=True, unique=True)
    dob = models.DateField(null=True)
    address = models.CharField(max_length=150, null=True)
    city = models.CharField(max_length=150, null=True)
    province = models.CharField(max_length=150, null=True)
    landlinePhone = models.IntegerField(null=True, blank=True)
    workStatus = models.CharField(max_length=50, choices=wkStatus, null=True)
    borrowerPhoto = models.ImageField(upload_to='photos/',null=True, blank=True)
    desc = models.TextField(null=True)
    borrowerFiles = models.ManyToManyField('ScannedFile', null=True, blank=True)
    officer = models.ForeignKey(Officer, on_delete=models.CASCADE, null=True,  related_name='Oficers')

        
    def __str__(self):
        return  f'{self.firstName} {self.secondName}'
