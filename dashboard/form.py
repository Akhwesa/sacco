from django import forms
from .models import Loan


class add_loan_form(forms.ModelForm):   
    class Meta:
        model = Loan
        fields = ['loanProduct', 'disbursedby', 'principal', 
                  'release_date', 'interestRate', 'loanInterest', 'loanDuration',
                   'durationPer', 'repayment_cycle', 'processingFee', 'desc']
        labels = {'loanProduct':'Loan Product:',
                  'disbursedby':'Loan Disbursement Platform:',
                  'principal':'Loan Principal Amount:',
                  'release_date':'Loan Release date:',
                  'interestRate':'Interest Rate Type:',
                  'loanInterest':'Interest Rate Per Annual:',
                  'loanDuration':'Loan Duration:',
                  'durationPer':'Duration Per:',
                  'repayment_cycle':'Repayment cycle:',
                  'processingFee':'Loan Processing Fee:',
                  'desc':'Loan Description:',
                  }

class upate_loan_form(forms.ModelForm):   
    class Meta:
        model = Loan
        fields = [ 'loanNo',  'principal', 'loanInterest', 'loanDuration', 'durationPer', 'repayment_cycle','processingFee', 'release_date' ]
        labels = {
                  'loanNo':'Loan Number:',
                  'principal':'Loan Principal Amount:',
                  'loanInterest':'Interest Rate Per Annual:',
                  'loanDuration':'Loan Duration:',
                  'durationPer':'Duration Per:',
                  'repayment_cycle':'Repayment cycle:',
                  'processingFee':'Loan Processing Fee:',
                  'release_date': 'Loan Release Date:'
                  }