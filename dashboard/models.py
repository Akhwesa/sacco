from django.db import models
from user.models import Member
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

# Create your models here.

product = (
    ('Business Loan', 'Business Loan'),
    ('Personal Loan', 'Personal Loan'),
    ('General Loan', 'General Loan'),
    ('Student Loan', 'Student Loan'),
    ('Pensioner Loan', 'Pensioner Loan'),   
)
per = (
    ('month', 'month'),
    ('year', 'year'),
    )
disbursed = (
    ('Cash', 'Cash'),
    ('Cheque', 'Cheque'),
    ('Mpesa', 'Mpesa'),
    ('online Transfer', 'online Transfer'),
)
intRate = (
    ('Flat Rate', 'Flat Rate'),
    ('Reducing Balance - Equal Principal', 'Reducing Balance - Equal Principal'),
    
)
REPAYMENT_CYCLES = (
        ('daily', 'daily'),
        ('weekly', 'weekly'),
        ('monthly', 'monthly'),
        ('yearly', 'yearly'), 
)
loanStatus = (
    ('Open', 'Open'),
    ('Processing', 'Processing'),
    ('Approved', 'Approved'),
    ('Defaulted', 'Defaulted'),
    ('Repaying', 'Repaying'),
    ('Denied', 'Denied'),
    ('Cleared', 'Cleared'),
    ('Write Off', 'Write Off'),
    ('Debt Review', 'Debt Review'),
    ('Not Taken Up', 'Not Taken Up'),    
)
paymentStatus = (
    ('Open', 'Open'),
    ('Cleared', 'Cleared'),
    ('Missed', 'Missed'),
    ('Arrears', 'Arrears'),
)

class ScannedFile(models.Model):
    file = models.FileField(upload_to='scanned_files/')

class Loan(models.Model):
    loanProduct = models.CharField(max_length=250, choices = product)
    borrower = models.OneToOneField(Member, on_delete=models.CASCADE)
    loanNo = models.IntegerField( unique = True, null=True, blank=True)
    disbursedby = models.CharField(max_length=150, choices=disbursed)
    principal = models.IntegerField()
    release_date = models.DateField()
    interestRate = models.CharField(max_length=150, choices=intRate)
    loanInterest = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    loanDuration = models.IntegerField()
    durationPer = models.CharField(max_length=50, choices=per, default='year') 
    repayment_cycle = models.CharField(choices=REPAYMENT_CYCLES, max_length=10, default='monthly')
    processingFee = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    loanFiles = models.ManyToManyField('ScannedFile', null=True, blank=True)
    desc = models.TextField(null=True)
    status = models.CharField(choices=loanStatus, max_length=20, default='Open')

    def clean(self):
        if self.durationPer == 'month' and self.repayment_cycle == 'yearly' and self.loanDuration <= 12:
            raise ValidationError("Loan duration must be greater than 12 for yearly repayment cycle.")
    def save(self, *args, **kwargs):
        if not self.pk:  # Only generate the number if the object is being created
            last_object = Loan.objects.order_by('-loanNo').first()
            if last_object:
                last_number = last_object.loanNo
                new_number = last_number + 1
            else:
                new_number = 1000  # Starting number when no objects exist yet
            self.loanNo = new_number
        super().save(*args, **kwargs)

class Payment(models.Model):
    accountReference = models.CharField(max_length=50)
    paidAmount = models.DecimalField(max_digits=8, decimal_places=2)
    paymentDate = models.DateField()
    transactionId =  models.CharField(max_length=150, unique=True)
    phoneNumber = models.IntegerField()
    fullName = models.CharField(max_length=150)
    invoiceName = models.CharField(max_length=150)
    externalReference = models.CharField(max_length=150)

    def __str__(self):
        return f'{self.accountReference}-{self.phoneNumber}-{self.paidAmount} - {self.paymentDate}'

class Contribution(models.Model):
    contributionAmount = models.DecimalField(max_digits=12, decimal_places=2)
    insuaranceAmount = models.DecimalField(max_digits=12, decimal_places=2)
    savingAmount = models.DecimalField(max_digits=12, decimal_places=2)
    contributor = models.OneToOneField(Member, on_delete=models.CASCADE)
    
    def __str__(self) :
        return f'{self.contributor}-{self.savingAmount}'

class contributionsPayments(models.Model):
    contributor = models.ManyToManyField(Member)
    accountReference = models.CharField(max_length=50)
    paidAmount = models.DecimalField(max_digits=8, decimal_places=2)
    paymentDate = models.DateField()
    transactionId =  models.CharField(max_length=150, unique=True)

    def __str__(self):
        return f'{self.contributor} - {self.accountReference} - {self.paidAmount} - {self.paymentDate} - {self.transactionId}'
  
class shares(models.Model):
    contributor = models.OneToOneField(Member, on_delete=models.CASCADE)
    sharesAmount = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f'{self.contributor} - {self.sharesAmount}'
    
class LoanAccount(models.Model):
    contributor = models.OneToOneField(Member, on_delete=models.CASCADE)
    principleAmount = models.DecimalField(max_digits=12, decimal_places=2)
    loan = models.OneToOneField(Loan, on_delete=models.CASCADE)
    amountDue = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f'{self.contributor} - {self.principleAmount}-{self.loan} - {self.amountDue}'

class loanPaymentsreceipts(models.Model):
    contributor = models.ManyToManyField(Member)
    accountReference = models.CharField(max_length=50)
    paidAmount = models.DecimalField(max_digits=8, decimal_places=2)
    paymentDate = models.DateField()
    transactionId =  models.CharField(max_length=150, unique=True)

    def __str__(self):
        return f'{self.contributor} - {self.accountReference} - {self.paidAmount} - {self.paymentDate} - {self.transactionId}'
 
class LoanPaymentII(models.Model):
    MonthlyPayment =  models.DecimalField(max_digits=12, decimal_places=2)
    loanAccount = models.ForeignKey(LoanAccount, on_delete=models.CASCADE)
    interest = models.DecimalField(max_digits=12, decimal_places=2)
    principlePayment = models.DecimalField(max_digits=12, decimal_places=2)
    balance = models.DecimalField(max_digits=12, decimal_places=2)
    paymentDate = models.DateField()
    status = models.CharField(max_length=50, choices=paymentStatus ,default='Open')

    def __str__(self):
        return f'{self.loanAccount} - {self.MonthlyPayment} - {self.interest} - {self.paymentDate}  - {self.principlePayment} -{self.status} '


class LoanPayment(models.Model):
    MonthlyPayment =  models.DecimalField(max_digits=12, decimal_places=2)
    loanAccount = models.ForeignKey(LoanAccount, on_delete=models.CASCADE)
    interest = models.DecimalField(max_digits=12, decimal_places=2)
    principlePayment = models.DecimalField(max_digits=12, decimal_places=2)
    paymentDate = models.DateField()
    status = models.CharField(max_length=50, choices=paymentStatus ,default='Open')

    def __str__(self):
        return f'{self.loanAccount} - {self.MonthlyPayment} - {self.interest} - {self.paymentDate}  - {self.principlePayment} -{self.status} '

class Claimed(models.Model):
    accountReference = models.CharField(max_length=50)
    paidAmount = models.DecimalField(max_digits=8, decimal_places=2)
    paymentDate = models.DateField()
    transactionId =  models.CharField(max_length=150, unique=True)
    phoneNumber = models.IntegerField()
    fullName = models.CharField(max_length=150)
    invoiceName = models.CharField(max_length=150)
    externalReference = models.CharField(max_length=150)
    status = models.CharField(max_length=50, default='Unclaimed')

    def __str__(self):
        return f'{self.accountReference}-{self.phoneNumber}-{self.paidAmount} - {self.paymentDate}' 

class Total_Amount(models.Model):
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f'{self.name} - {self.amount}'