from django.contrib import admin
from .models import Loan, Contribution, Payment, shares, Claimed, LoanAccount, LoanPayment, Total_Amount, contributionsPayments, LoanPaymentII, loanPaymentsreceipts

# Register your models here.
admin.site.register(Loan)
admin.site.register(Contribution)
admin.site.register(contributionsPayments)
admin.site.register(Payment)
admin.site.register(shares)
admin.site.register(Claimed)
admin.site.register(LoanAccount)
admin.site.register(LoanPayment)
admin.site.register(LoanPaymentII)
admin.site.register(loanPaymentsreceipts)
admin.site.register(Total_Amount)
