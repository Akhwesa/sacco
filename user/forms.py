from django import forms
from .models import Member

class addBorrower(forms.ModelForm):
    class Meta:
        model = Member
        fields = [
                  'firstName', 'secondName', 'te_id', 'gender',
                  'title', 'phone', 'mail', 'dob', 'address', 
                  'city', 'province', 'workStatus', 'desc',  'officer'
                  ]
        labels = {
                  'firstName':'First Name:', 'secondName': 'Second Name:', 'te_id': 'National ID', 'gender':'Gender:',
                  'title':'Title:', 'phone':'Phone Number:', 'mail':'Email:', 'dob':'Date of Birth:', 'address': 'Address:', 
                  'city':'City:', 'province':'County:',  'workStatus': 'Work Status:', 
                  'desc': 'Description:', 'officer':'Loan Officer:'
        }

class updateMember(forms.ModelForm):
    class Meta:
        model = Member
        fields = [
                  'firstName', 'secondName','borrowerPhoto', 'te_id', 'gender',
                  'title', 'phone','landlinePhone', 'mail', 'dob', 'address', 
                  'city', 'province', 'workStatus', 'desc',  'officer'
                  ]
        labels = {
                  'firstName':'First Name:', 'secondName': 'Second Name:','borrowerPhoto': 'Upload Photo', 'te_id': 'National ID', 'gender':'Gender:',
                  'title':'Title:', 'phone':'Phone Number:','landlinePhone':'Other Phone Number:', 'mail':'Email:', 'dob':'Date of Birth:', 'address': 'Address:', 
                  'city':'City:', 'province':'County:',  'workStatus': 'Work Status:', 
                  'desc': 'Description:', 'officer':'Loan Officer:'
        }

