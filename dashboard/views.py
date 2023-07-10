from django.shortcuts import render, redirect, reverse
from .models import Loan, Contribution, shares, ScannedFile, Payment, Claimed, LoanAccount, LoanPayment, Total_Amount, contributionsPayments, loanPaymentsreceipts, LoanPaymentII
from .logically import loan_amortization
from user.models import Member
from .form import add_loan_form, upate_loan_form
from django.core.paginator import Paginator,PageNotAnInteger, EmptyPage
from django.db.models import  Sum, Min, Count
from django.db.models.functions import Concat, TruncMonth, Lower
from datetime import datetime, timedelta, date
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from decimal import Decimal
import math
from django.http import JsonResponse, HttpResponseRedirect

# Create your views here.
def index(request): 
    current_month = datetime.now().month
    current_year = datetime.now().year    

     # Get all existing Claimed objects
    existing_claimed_objs = Claimed.objects.all()
    existing_transaction_ids = set(existing_claimed_objs.values_list('transactionId', flat=True))

    # Get all Payment objects linked to member phone numbers
    member_phone_numbers = Member.objects.values_list('phone', flat=True)
    payment_objs = Payment.objects.filter(accountReference__in=member_phone_numbers)
     # Query for Payment objects not linked to member phone numbers
    non_member_payment_objs = Payment.objects.exclude(accountReference__in=member_phone_numbers)

    # Iterate over the Payment objects
    for payment_obj in payment_objs:
        # Check if the transactionId already exists in Claimed objects
        if payment_obj.transactionId in existing_transaction_ids:
            pass
            # Update the existing Claimed object's status to 'claimed'
           # existing_claimed_objs.filter(transactionId=payment_obj.transactionId).update(status='claimed')
        else:
                if payment_obj.phoneNumber in member_phone_numbers:
                # Create a new Claimed object with status as 'unclaimed'
                    claimed1 = Claimed.objects.create(
                        accountReference=payment_obj.accountReference,
                        paidAmount=payment_obj.paidAmount,
                        paymentDate=payment_obj.paymentDate,
                        transactionId=payment_obj.transactionId,
                        phoneNumber=payment_obj.phoneNumber,
                        fullName=payment_obj.fullName,
                        invoiceName=payment_obj.invoiceName,
                        externalReference=payment_obj.externalReference,
                        status='claimed'
                    )
                else:
                    # Create a new Claimed object with status as 'claimed'
                    claimed1 = Claimed.objects.create(
                        accountReference=payment_obj.accountReference,
                        paidAmount=payment_obj.paidAmount,
                        paymentDate=payment_obj.paymentDate,
                        transactionId=payment_obj.transactionId,
                        phoneNumber=payment_obj.phoneNumber,
                        fullName=payment_obj.fullName,
                        invoiceName=payment_obj.invoiceName,
                        externalReference=payment_obj.externalReference,
                        status='claimed'
                    )
                    if claimed1.invoiceName == 'savings':
                        T_savings = Total_Amount.objects.get(name = 'savings')
                        savings = T_savings.amount
                        payment = claimed1.paidAmount
                        savings += payment
                        T_savings.save()
                        
                    elif claimed1.invoiceName == 'loan':
                        T_savings = Total_Amount.objects.get(name = 'loans')
                        savings = T_savings.amount
                        payment = claimed1.paidAmount
                        savings += payment
                        T_savings.save()
                    elif claimed1.invoiceName == 'shares':
                        T_savings = Total_Amount.objects.get(name = 'shares')
                        savings = T_savings.amount
                        payment = claimed1.paidAmount
                        savings += payment
                        T_savings.save()
                    else:
                        claimed1.invoiceName = 'savings'
                        claimed1.save()
              
    # Iterate over the Payment objects
    for non_member_payment_obj in non_member_payment_objs:
        # Check if the transactionId already exists in Claimed objects
        if non_member_payment_obj.transactionId in existing_transaction_ids:
            pass
            # Update the existing Claimed object's status to 'claimed'
           # existing_claimed_objs.filter(transactionId=non_member_payment_obj.transactionId).update(status='claimed')
        else:
            if non_member_payment_obj.phoneNumber in member_phone_numbers:
            # Create a new Claimed object with status as 'unclaimed'
                claimed1 = Claimed.objects.create(
                    accountReference=non_member_payment_obj.accountReference,
                    paidAmount=non_member_payment_obj.paidAmount,
                    paymentDate=non_member_payment_obj.paymentDate,
                    transactionId=non_member_payment_obj.transactionId,
                    phoneNumber=non_member_payment_obj.phoneNumber,
                    fullName=non_member_payment_obj.fullName,
                    invoiceName=non_member_payment_obj.invoiceName,
                    externalReference=non_member_payment_obj.externalReference,
                    status='unclaimed'
                )
            else:
                # Create a new Claimed object with status as 'unclaimed'
                claimed1 = Claimed.objects.create(
                    accountReference=non_member_payment_obj.accountReference,
                    paidAmount=non_member_payment_obj.paidAmount,
                    paymentDate=non_member_payment_obj.paymentDate,
                    transactionId=non_member_payment_obj.transactionId,
                    phoneNumber=non_member_payment_obj.phoneNumber,
                    fullName=non_member_payment_obj.fullName,
                    invoiceName=non_member_payment_obj.invoiceName,
                    externalReference=non_member_payment_obj.externalReference,
                    status='unclaimed'
                )
                if claimed1.invoiceName == 'savings':
                    T_savings = Total_Amount.objects.get(name = 'savings')
                    savings = T_savings.amount
                    payment = claimed1.paidAmount
                    savings += payment
                    T_savings.save()
                    
                elif claimed1.invoiceName == 'loan':
                    T_savings = Total_Amount.objects.get(name = 'loans')
                    savings = T_savings.amount
                    payment = claimed1.paidAmount
                    savings += payment
                    T_savings.save()
                elif claimed1.invoiceName == 'shares':
                    T_savings = Total_Amount.objects.get(name = 'shares')
                    savings = T_savings.amount
                    payment = claimed1.paidAmount
                    savings += payment
                    T_savings.save()
                else:
                    claimed1.invoiceName = 'savings'
                    claimed1.save()
                
    cl = Claimed.objects.filter(status = 'claimed')
    manambaz = cl.values_list('accountReference', flat=True).distinct()
    mb = Member.objects.filter(phone__in = manambaz)
    
    for item in mb:
        contribution = Contribution.objects.filter(contributor=item).first()
        loan_account = LoanAccount.objects.filter(contributor=item).first()
        shares_model = shares.objects.filter(contributor=item).first()
        item_loan = Loan.objects.filter(borrower=item).first()

       
        ctt1 = cl.filter(accountReference=item.phone, invoiceName='savings')
        ctt_count = ctt1.count()        

        if contribution:
            
            existing_cp_objs = contributionsPayments.objects.filter(accountReference = item.phone)
            cp_transaction_ids = set(existing_cp_objs.values_list('transactionId', flat=True))
            # Query for Claimed_Payment objects not linked to contribution Payments
            notLinkedPayments = ctt1.exclude(transactionId__in=cp_transaction_ids)
            nlp_count = notLinkedPayments.count()


            if nlp_count > 0:
                
                for i in notLinkedPayments:
                    cb = contributionsPayments.objects.create(
                    paidAmount = i.paidAmount,
                    accountReference=i.accountReference,
                    paymentDate = i.paymentDate,
                    transactionId = i.transactionId
                    )
                    cb.contributor.add(item)
                    
                cpt = contributionsPayments.objects.filter(accountReference = item.phone)

                #ctt = cpt.filter( paymentDate__month=current_month, paymentDate__year=current_year)
                # Get the earliest date in each month
                #distinct_dates = cpt.values('paymentDate__month').annotate(min_date=Min('paymentDate')).order_by('min_date')

                # Get the earliest value in terms of date for each month
                #earliest_values = [cpt.filter(paymentDate=date['min_date']).first() for date in distinct_dates]
                
                # Annotate the queryset to extract the month from the paymentDate field
                payments = cpt.annotate(month=TruncMonth('paymentDate'))

                # Aggregate the queryset to count the number of occurrences of each month
                unique_months = payments.values('month').annotate(month_count=Count('month'))

                contribution_amount = cpt.aggregate(total_contribution=Sum('paidAmount'))['total_contribution'] or 0.00
                ctt_count1 = unique_months.count()
                insuarance = 300 * ctt_count1 or 0.00  # Assuming a fixed insurance amount of 300 per month
                saving = Decimal(contribution_amount) - Decimal(insuarance)  

                contribution.contributionAmount = contribution_amount
                contribution.insuaranceAmount = insuarance
                contribution.savingAmount = saving
                contribution.save()           
        else:
            cl1 = Contribution.objects.create(
                contributionAmount=0,
                insuaranceAmount=0,
                savingAmount=0,
                contributor=item
            )

            for i in ctt1:
                cb = contributionsPayments.objects.create(
                    paidAmount = i.paidAmount,
                    accountReference=i.accountReference,
                    paymentDate = i.paymentDate,
                    transactionId = i.transactionId
                    )
                cb.contributor.add(item)
            cpt = contributionsPayments.objects.filter(accountReference = item.phone)
            
                # Annotate the queryset to extract the month from the paymentDate field
            payments = cpt.annotate(month=TruncMonth('paymentDate'))

                # Aggregate the queryset to count the number of occurrences of each month
            unique_months = payments.values('month').annotate(month_count=Count('month'))

            #ctt = cpt.filter( paymentDate__month=current_month, paymentDate__year=current_year)
            # Get the earliest date in each month
            #distinct_dates = ctt.values('paymentDate__month').annotate(min_date=Min('paymentDate')).order_by('min_date')
            # Get the earliest value in terms of date for each month
            #earliest_values = [ctt.filter(paymentDate=date['min_date']).first() for date in distinct_dates]

            contribution_amount = cpt.aggregate(total_contribution=Sum('paidAmount'))['total_contribution'] or 0
            ctt_count1 = unique_months.count()
            insuarance = 300 * ctt_count1  # Assuming a fixed insurance amount of 300 per month
            saving = Decimal(contribution_amount) - Decimal(insuarance) 

            cl1.contributionAmount = contribution_amount
            cl1.insuaranceAmount = insuarance
            cl1.savingAmount = saving
            cl1.save()
        if shares_model:
            ctt = cl.filter(accountReference=item.phone)
            shares_amount = ctt.filter(invoiceName='shares').aggregate(total_contribution=Sum('paidAmount'))['total_contribution'] or 0
            shares_model.sharesAmount += shares_amount
            shares_model.save()
        """else:
            ctt = cl.filter(accountReference=item.phone)
            shares_amount = ctt.filter(invoiceName='shares').aggregate(total_contribution=Sum('paidAmount'))['total_contribution'] or 0
            shares.objects.create(
                sharesAmount=shares_amount,
                contributor=item
            ) """      
        if item_loan: 
            if item_loan.status == 'Repaying':
                if loan_account.principleAmount > 0:
                    ctt = Claimed.objects.filter(accountReference=item.phone, invoiceName= 'loans')
                    ta_interests = Total_Amount.objects.get(name = 'interests')
                    ta_loans = Total_Amount.objects.get(name = 'loans')

                    lp1 = LoanPaymentII.objects.filter(loanAccount = loan_account)
                    lp = lp1.exclude(status = 'Cleared')
                    # Sort loan payments by paymentDate in ascending order
                    lp = lp.order_by('paymentDate')
                    
                    existing_lpr_objs = loanPaymentsreceipts.objects.filter(accountReference = item.phone)
                    lpr_transaction_ids = set(existing_lpr_objs.values_list('transactionId', flat=True))
                    # Query for Claimed_Payment objects not linked to loan Payments receipts
                    notLinkedPayments = ctt.exclude(transactionId__in=lpr_transaction_ids)
                    nlp_count = notLinkedPayments.count()
                    if nlp_count > 0:                
                        for i in notLinkedPayments:
                            cb = loanPaymentsreceipts.objects.create(
                            paidAmount = i.paidAmount,
                            accountReference=i.accountReference,
                            paymentDate = i.paymentDate,
                            transactionId = i.transactionId
                            )
                            cb.contributor.add(item)
                        
                        lpr = loanPaymentsreceipts.objects.filter(accountReference = item.phone)

                        # Iterate over loan payments and deduct from paidAmount
                        for payment in lp:
                            if item_loan.repayment_cycle == 'monthly':
                                lpr_monthly = lpr.filter(paymentDate__month=payment.paymentDate.month)
                                total_paid = lpr_monthly.aggregate(total_paid=Sum('paidAmount'))['total_paid'] or 0
                            elif item_loan.repayment_cycle == 'daily':
                                lpr_monthly = lpr.filter(paymentDate__day=payment.paymentDate.day)
                                total_paid = lpr_monthly.aggregate(total_paid=Sum('paidAmount'))['total_paid'] or 0
                            elif item_loan.repayment_cycle == 'weekly':
                                lpr_monthly = lpr.filter(paymentDate__weekday=payment.paymentDate.weekday)
                                total_paid = lpr_monthly.aggregate(total_paid=Sum('paidAmount'))['total_paid'] or 0
                            elif item_loan.repayment_cycle == 'yearly':
                                lpr_monthly = lpr.filter(paymentDate__year=payment.paymentDate.year)
                                total_paid = lpr_monthly.aggregate(total_paid=Sum('paidAmount'))['total_paid'] or 0

                            current_date = timezone.localdate()  # Get the current date in the timezone defined in Django settings
                            if payment.paymentDate < current_date:
                                if total_paid == payment.MonthlyPayment:
                                    loan_account.principleAmount -= payment.MonthlyPayment
                                    loan_account.loan.principal -= payment.principlePayment
                                    payment.balance = 0
                                    payment.status = 'Cleared'
                                    ta_interests.amount += payment.interest
                                    ta_loans.amount -= payment.principlePayment
                                elif total_paid > payment.MonthlyPayment:
                                    payment.balance =  total_paid - payment.MonthlyPayment
                                    loan_account.principleAmount -= payment.MonthlyPayment                            
                                    loan_account.amountDue += payment.balance
                                    payment.status = 'Cleared'
                                    ta_interests.amount += payment.interest
                                    ta_loans.amount -= payment.principlePayment
                                    payment.balance = 0
                                elif total_paid == 0:
                                    laa = loan_account.amountDue
                                    payment.status = 'Missed'
                                    payment.balance = payment.MonthlyPayment - total_paid 
                                    pb = payment.balance
                                    loan_account.amountDue -= payment.balance
                                    payment.balance -= laa
                                    if loan_account.amountDue >= 0:
                                        payment.status = 'Cleared'
                                        ta_interests.amount += payment.interest
                                        ta_loans.amount -= payment.principlePayment
                                        loan_account.principleAmount -= payment.MonthlyPayment 
                                        payment.balance = 0.0
                                    elif payment.balance < pb and loan_account.amountDue < 0 :
                                        payment.status = 'Arrears'
                                elif total_paid < payment.MonthlyPayment:
                                    if payment.status == 'Arrears':
                                        laa = loan_account.amountDue
                                        payment.balance = payment.MonthlyPayment - total_paid 
                                        pb = payment.balance
                                        loan_account.amountDue -= payment.balance
                                        payment.balance -= laa
                                        if loan_account.amountDue >= 0:
                                            payment.status = 'Cleared'
                                            ta_interests.amount += payment.interest
                                            ta_loans.amount -= payment.principlePayment
                                            loan_account.principleAmount -= payment.MonthlyPayment 
                                            payment.balance = 0.0
                                        elif payment.balance < pb and loan_account.amountDue < 0 :
                                            payment.status = 'Arrears'

                                    else:
                                        payment.status = 'Arrears'
                                        payment.balance = payment.MonthlyPayment - total_paid 
                                        loan_account.amountDue -= payment.balance
                                """       
                                else:
                                    payment.status = 'Missed'"""
                            elif payment.paymentDate == current_date:
                                if total_paid == payment.MonthlyPayment:
                                    loan_account.principleAmount -= payment.MonthlyPayment
                                    loan_account.loan.principal -= payment.principlePayment
                                    payment.balance = 0
                                    payment.status = 'Cleared'
                                    ta_interests.amount += payment.interest
                                    ta_loans.amount -= payment.principlePayment
                                elif total_paid > payment.MonthlyPayment:
                                    payment.balance =  total_paid - payment.MonthlyPayment
                                    loan_account.principleAmount -= payment.MonthlyPayment                            
                                    loan_account.amountDue += payment.balance
                                    payment.status = 'Cleared'
                                    ta_interests.amount += payment.interest
                                    ta_loans.amount -= payment.principlePayment
                                    payment.balance = 0

                            payment.save()
                        loan_account.save()
                    

                else: 
                    item_loan.status == 'Cleared'
                    item_loan.save()
            

    contribute = Contribution.objects.all()
    contributeCount = contribute.count()
    contribution = contribute.aggregate(total_contribution=Sum('contributionAmount'))['total_contribution'] or 0
    Savings = contribute.aggregate(total_contribution=Sum('savingAmount'))['total_contribution'] or 0
    insured = contribute.aggregate(total_contribution=Sum('insuaranceAmount'))['total_contribution'] or 0
    
    share = shares.objects.all()
    share_count = share.count()
    shares_amount = share.aggregate(total_shares=Sum('sharesAmount'))['total_shares'] or 0

    loans = Loan.objects.all()
    loans_count = loans.count()
    loanIssued = loans.filter(status = 'Repaying')
    loanClosed = loans.filter(status = 'Cleared')

    issuedLoansCount = loanIssued.count()
    closedLoansCount = loanClosed.count()
    total_disbursed = []
    for l in loanIssued:
        principal = l.principal
        p_fee = l.processingFee
        convert_fee = p_fee / 100
        fee = principal * convert_fee
        disburse_Amount = principal - fee
        total_disbursed.append({
            'disburse_Amount':disburse_Amount,
        })

    disburse_sum = sum(item['disburse_Amount'] for item in total_disbursed) 

    montlhyloanIssued = loanIssued.filter(release_date__month = current_month, release_date__year = current_year )
    montlhyloanClosed = loanClosed.filter(release_date__month = current_month, release_date__year = current_year ) 

    montlhyloanIssuedCount = montlhyloanIssued.count()
    montlhyloanClosedCount = montlhyloanClosed.count()
    total_monthly_disbursed = []
    for l in montlhyloanIssued:
        principal = l.principal
        p_fee = l.processingFee
        convert_fee = p_fee / 100
        fee = principal * convert_fee
        disburse_monthly_Amount = principal - fee
        total_monthly_disbursed.append({
            'disburse_monthly_Amount':disburse_monthly_Amount,
        })

    monthly_disburse_sum = sum(item['disburse_monthly_Amount'] for item in total_monthly_disbursed) 

    members = Member.objects.all()
    memberCount = members.count()

    cl7 = Claimed.objects.filter(status = 'claimed')
    manambaz3 = cl7.values_list('accountReference', flat=True).distinct()
    mb = Member.objects.filter(phone__in = manambaz3)

    applicant=[]
    for i in mb:

        ctt = Contribution.objects.get(contributor = i)
        savings = ctt.savingAmount or 0
        
        ln = Loan.objects.filter(borrower = i).first()
        if ln:
            principalLoan = ln.principal or 0
            
            monthly_rate = ln.loanInterest / 100
        else:
            principalLoan = 0.0
            monthly_rate = 0.0    
        LoanInt = principalLoan * monthly_rate
        currentLoan = principalLoan + LoanInt or 0
        limit = savings * 3 or 0
        loan_limit = Decimal(limit) - Decimal(currentLoan) or Decimal(0)

        if loan_limit > 300:
            applicant.append({
                'pk' : i.pk,
                })
            apply = len(applicant)

    claims = Claimed.objects.all()
    totalclaims = claims.aggregate(total_claims=Sum('paidAmount'))['total_claims'] or 0
    unclaimed = claims.filter(status = 'unclaimed')
    total_unclaimed = unclaimed.aggregate(total_claims=Sum('paidAmount'))['total_claims'] or 0
    total_claimed = cl7.aggregate(total_claims=Sum('paidAmount'))['total_claims'] or 0
    loanStr = 'loan'
    loansPayment = Claimed.objects.filter(invoiceName__iexact =loanStr)
    total_loansPayment = loansPayment.aggregate(total_claims=Sum('paidAmount'))['total_claims'] or 0
    savingsPayment = contributionsPayments.objects.all()
    total_savingsPayment = savingsPayment.aggregate(total_claims=Sum('paidAmount'))['total_claims'] or 0

    
    t_a = Total_Amount.objects.all()
    t_interest = t_a.get(name = 'interests')
    t_interest_am = t_interest.amount
    t_P_fee = t_a.get(name = 'p_fee')
    t_P_fee_am = t_P_fee.amount

    #monthly contributions
    cp = contributionsPayments.objects.all()
    mcp = cp.filter( paymentDate__month=current_month, paymentDate__year=current_year)
    t_mcp = mcp.aggregate(total_monthlyContribution=Sum('paidAmount'))['total_monthlyContribution'] or 0

    mcpi = mcp.values('accountReference').distinct().count()
    mcpInsuarance = mcpi * 300
    mcpsavings = t_mcp - mcpInsuarance
    #Payments percentange calculations
    tc = total_claimed/totalclaims
    tcd = round(tc, 2)
    tcp = tcd * 100
    tuc = total_unclaimed/totalclaims
    tucd = round(tuc, 2)
    tucp = tucd * 100
    tlp = total_loansPayment/totalclaims
    tlpd = round(tlp, 2)
    tlpp = tlpd * 100
    tsp = total_savingsPayment/totalclaims
    tspd = round(tsp, 2)
    tspp = tspd * 100

    context = {
        'cl':cl,
        'contribute':contribute,
        'contribution':contribution,
        'loans_count':loans_count,
        'Savings':Savings,
        'insured':insured,
        'share_count':share_count,
        'shares_amount':shares_amount,
        'issuedLoansCount':issuedLoansCount,
        'montlhyloanIssuedCount':montlhyloanIssuedCount,
        'montlhyloanClosedCount':montlhyloanClosedCount,
        'disburse_sum':disburse_sum,
        'monthly_disburse_sum':monthly_disburse_sum,
        'closedLoansCount':closedLoansCount,
        'memberCount':memberCount,
        'contributeCount':contributeCount,
        'apply':apply,
        'totalclaims':totalclaims,
        'total_unclaimed':total_unclaimed,
        'total_claimed':total_claimed,
        'total_loansPayment':total_loansPayment,
        'total_savingsPayment':total_savingsPayment,
        't_interest_am':t_interest_am,
        't_P_fee_am':t_P_fee_am,
        'tcp':tcp,
        'tucp':tucp,
        'tlpp':tlpp,
        'tspp':tspp,
        't_mcp':t_mcp,
        'mcpsavings':mcpsavings,
        'mcpInsuarance':mcpInsuarance,
        'current_month':current_month,

    }
    return render(request,'dashboard/index.html', context)

def update_current_month(request):
    if request.method == 'POST' and request.is_ajax():
        current_month = request.POST.get('current_month')
        current_year = request.POST.get('current_year')

        # Update the session variables or any other appropriate data storage method
        request.session['current_month'] = current_month
        request.session['current_year'] = current_year

        return JsonResponse({'success': True, 'current_month': current_month, 'current_year': current_year})
    else:
        return JsonResponse({'success': False})

def monthly_contribute(request, current_month):
    current_year = datetime.now().year
    current_month = int(current_month)

    if request.method == 'POST':
        option = request.POST.get('options')
        if option == '2':
            current_month -= 1  # Subtract 1 for Last Month
        elif option == '3':
            current_month -= 2  # Subtract 2 for Past Two Months

    # Handle wrap-around to the previous year
        if current_month <= 0:
            current_month += 12
            current_year -= 1
        return HttpResponseRedirect(reverse('dashboard-monthly-contribute', args=[current_month]))
    

    
    members = Member.objects.all()
    # Monthly contributions
    cp = contributionsPayments.objects.all()
    mcp = cp.filter(paymentDate__month=current_month, paymentDate__year=current_year)
    account_references = mcp.values_list('accountReference', flat=True)
    mb = members.filter(phone__in=account_references)
    
    contributors = []
    for item in mb:
        fullName = f'{item.title} {item.firstName} {item.secondName}'
        wkstatus = item.workStatus
        N_id = item.te_id
        PhoneNo = item.phone
        mb_mcp = mcp.filter(accountReference=item.phone)
        total_mb_mcp = mb_mcp.aggregate(total_monthlyContribution=Sum('paidAmount'))['total_monthlyContribution'] or 0
        insured = 300
        savings = total_mb_mcp - insured
        contributors.append({
            'fullName': fullName,
            'wkstatus': wkstatus,
            'N_id': N_id,
            'PhoneNo': PhoneNo,
            'total_mb_mcp': total_mb_mcp,
            'insured': insured,
            'savings': savings,
            'pk' : item.pk,
        })

    total_mcp = mcp.aggregate(total_monthlyContribution=Sum('paidAmount'))['total_monthlyContribution'] or 0
    #mb_phone = mb.values_list('phone', flat=True)
    individual_cp = mcp.filter(accountReference__in=mb.values_list('phone', flat=True)).values('accountReference').distinct()
    icp_count = individual_cp.count()
    insurance = icp_count * 300 or 0
    saving = total_mb_mcp - insurance
    
    context = {
        'contributors':contributors,
        'total_mcp':total_mcp, 
        'insurance':insurance,
        'saving':saving,
        'current_month':current_month,

    }

    return render(request,'dashboard/monthly_contribute.html', context )

def monthly_receipt(request, pk):
    current_year = datetime.now().year
    current_month = datetime.now().month
    cl = Claimed.objects.all()
    member = Member.objects.get(pk=pk)
    cpt = contributionsPayments.objects.filter(paymentDate__month=current_month, paymentDate__year=current_year)
    m_cpt = cpt.filter(accountReference = member.phone)
    transaction_list = m_cpt.values_list('transactionId', flat=True)
    payments = cl.filter(transactionId__in=transaction_list).order_by('paymentDate')

    context = {
        'payments':payments,
    }

    return render(request,'dashboard/monthly_receipt.html', context )

def monthly_loan(request): 
    current_month = datetime.now().month
    current_year = datetime.now().year 
    loan = Loan.objects.all()
    monthlyLoan = loan.filter(release_date__month = current_month, release_date__year = current_year )

    loanView = []
    for l in monthlyLoan:
        mb = Member.objects.get(pk = l.borrower.pk)
        fullName = f'{mb.title} {mb.firstName} {mb.secondName}'
        pricipal = l.principal
        interest = l.loanInterest
        try:
            lc = LoanAccount.objects.get(loan=l)
            balance = lc.principleAmount
            due = lc.amountDue
        except LoanAccount.DoesNotExist:
            lc = LoanAccount.objects.create(
                contributor=l.borrower,
                loan=l,
                principleAmount=0.0,
                amountDue=0.0
            )
            balance = 0.0
            due = 0.0
        try:
            lpr = loanPaymentsreceipts.objects.get(accountReference=l.borrower.phone)
            lastObject = lpr.latest('paymentDate')
            lastPayment = lastObject.paidAmount
            total_lpr = lpr.aggregate(total_Paidloan=Sum('paidAmount'))['total_Paidloan'] or 0
        except loanPaymentsreceipts.DoesNotExist:
            lastPayment = 0.0
            total_lpr = 0.0

        pricipal = l.principal
        interest = l.loanInterest
        ln_No = l.loanNo
        date = l.release_date
        stats = l.status
        
        loanView.append({
            'balance':balance,
            'due':due,
            'pk':l.pk,
            'fullName':fullName,
            'pricipal':pricipal,
            'interest':interest,
            'ln_No':ln_No,
            'date':date,
            'stats':stats,
            'total_lpr':total_lpr,
            'lastPayment':lastPayment,

        })

    try:
        loan_acc = LoanAccount.objects.all()
        lpr2 = loanPaymentsreceipts.objects.filter(paymentDate__month = current_month, paymentDate__year = current_year)
        total_lpr2 = lpr2.aggregate(total_Paidloan=Sum('paidAmount'))['total_Paidloan'] or 0
        loan_accDue = loan_acc.aggregate(total_due=Sum('amountDue'))['total_due'] or 0
        loan_accBal = loan_acc.aggregate(total_due=Sum('principleAmount'))['total_due'] or 0
        
    except LoanAccount.DoesNotExist:
        total_lpr2 = 0.0
        loan_accDue = 0.0
        loan_accBal = 0.0

    totalPrincipal = loan.aggregate(total_principal=Sum('principal'))['total_principal'] or 0

    context = {
        'totalPrincipal':totalPrincipal,
        'total_lpr2':total_lpr2,
        'loan_accDue':loan_accDue,
        'loan_accBal':loan_accBal,
        'loanView':loanView,
    }
    return render(request,'dashboard/monthly_loan.html', context)

def view_loan(request): 
    loan = Loan.objects.all()

    loanView = []
    for l in loan:
        mb = Member.objects.get(pk = l.borrower.pk)
        fullName = f'{mb.title} {mb.firstName} {mb.secondName}'
        pricipal = l.principal
        interest = l.loanInterest
        try:
            lc = LoanAccount.objects.get(loan=l)
            balance = lc.principleAmount
            due = lc.amountDue
        except LoanAccount.DoesNotExist:
            lc = LoanAccount.objects.create(
                contributor=l.borrower,
                loan=l,
                principleAmount=0.0,
                amountDue=0.0
            )
            balance = 0.0
            due = 0.0
        try:
            lpr = loanPaymentsreceipts.objects.filter(accountReference=l.borrower.phone)
            lastObject = lpr.latest('paymentDate')
            lastPayment = lastObject.paidAmount
            total_lpr = lpr.aggregate(total_Paidloan=Sum('paidAmount'))['total_Paidloan'] or 0
        except loanPaymentsreceipts.DoesNotExist:
            lastPayment = 0.0
            total_lpr = 0.0
        ln_No = l.loanNo
        date = l.release_date
        stats = l.status
        
        loanView.append({
            'balance':balance,
            'pk':l.pk,
            'due':due,
            'pricipal':pricipal,
            'interest':interest,
            'ln_No':ln_No,
            'date':date,
            'stats':stats,
            'fullName':fullName,
            'total_lpr':total_lpr,
            'lastPayment':lastPayment,

        })
    
    loan_acc = LoanAccount.objects.all()
    lpr2 = loanPaymentsreceipts.objects.all()
    total_lpr2 = lpr2.aggregate(total_Paidloan=Sum('paidAmount'))['total_Paidloan'] or 0
    loan_accDue = loan_acc.aggregate(total_due=Sum('amountDue'))['total_due'] or 0
    loan_accBal = loan_acc.aggregate(total_due=Sum('principleAmount'))['total_due'] or 0
    totalPrincipal = loan.aggregate(total_principal=Sum('principal'))['total_principal'] or 0

    paginator = Paginator(loanView, 18)  # 18 rows per page
    page_number = request.GET.get('page', 1)  # Get the current page number
    page_obj = paginator.get_page(page_number)

    context = {
        'totalPrincipal':totalPrincipal,
        'total_lpr2':total_lpr2,
        'loan_accDue':loan_accDue,
        'loan_accBal':loan_accBal,
        'page_obj':page_obj,
        'paginator':paginator,
    }
    return render(request,'dashboard/view_loan.html', context)

def add_loan(request, pk): 
    member = Member.objects.get(pk=pk)
    ctt = Contribution.objects.get(contributor=member)
    savings = ctt.savingAmount or 0
    Fname = member.firstName
    Sname = member.secondName
    Title = member.title
    FullName = f'{Title}. {Fname} {Sname}'

    ln = Loan.objects.filter(borrower=member).first()
    if ln:
        principalLoan = ln.principal 
        monthly_rate = ln.loanInterest / 100
    else:
        principalLoan = 0.0
        monthly_rate = 0.0

    LoanInt = principalLoan * monthly_rate
    currentLoan = principalLoan + LoanInt or 0
    limit = savings * 3 or 0
    loan_limit = Decimal(limit) - Decimal(currentLoan)

    if request.method == 'POST':
        addLoan = add_loan_form(request.POST)
        if addLoan.is_valid():
            principal_value = addLoan.cleaned_data['principal']

            if principal_value > loan_limit:
                addLoan.add_error('principal', f'The value should be less than or equal to {loan_limit}.')
                
            else:
                loan = addLoan.save(commit=False)
                loan.borrower = member
                loan.status = 'Open'
                loan.save()
                return redirect('dashboard-loan-shedule', pk=loan.pk)
    else:
        addLoan = add_loan_form()

    context = {
        'addLoan': addLoan,
        'loan_limit': loan_limit,
        'FullName': FullName,
    }

    return render(request, 'dashboard/add_loan.html', context)

def loan_shedule(request, pk):
    items = Loan.objects.get(id=pk)
    interestRate = items.loanInterest
    principal = items.principal
    duration = items.durationPer
    br = items.borrower
    fullName = f'{br.title} {br.firstName} {br.secondName}'
    cycle = items.repayment_cycle

    ctt = Contribution.objects.get(contributor=br)
    savings = ctt.savingAmount or 0

    if duration == 'year' and cycle == 'monthly': 
        num_payment = items.loanDuration
        num_payments = num_payment * 12
    elif duration == 'year' and cycle == 'yearly':   
        num_payment = items.loanDuration
    elif duration == 'year' and cycle == 'weekly':
        num_payment = items.loanDuration
        num_payments = num_payment * 52
    elif duration == 'year' and cycle == 'daily':
        num_payment = items.loanDuration
        num_payments = num_payment * 365
    elif duration == 'month' and cycle == 'monthly':
        num_payment = items.loanDuration
        num_payments = num_payment 
    elif duration == 'month' and cycle == 'yearly':
        num_payment = items.loanDuration
        num_payments = math.ceil(num_payment / 12)
    elif duration == 'month' and cycle =='weekly':
        num_payment = items.loanDuration
        num_payments = num_payment * 4
    elif duration == 'month' and cycle == 'daily':
        num_payment = items.loanDuration
        num_payments = num_payment * 30
    else:
        num_payment = items.loanDuration
        num_payments = num_payment * 12
    #deduct processing fee
    fee = items.processingFee
    #convert fee from % to decimal
    mal = fee / 100
    p_fee = principal * mal
    dis_principal = principal - p_fee

    limit = savings * 3 or 0
    loan_limit = Decimal(limit) 

    updateForm = upate_loan_form(instance=items)
    if request.method == 'POST':
        updateForm = upate_loan_form(request.POST, instance=items)
        if updateForm.is_valid():
            principal_value = updateForm.cleaned_data['principal']
            
            if principal_value > loan_limit:
                updateForm.add_error('principal', f'The value should be less than or equal to {loan_limit}.')
            else:
                updateForm.save()            
                return redirect('dashboard-loan-shedule', pk=pk)
        else:
            # Refresh button was clicked
            updateForm = upate_loan_form(instance=items)   

    schedule = loan_amortization(principal, interestRate, num_payments)
    paginator = Paginator(schedule, 20)  # 21 rows per page
    page_number = request.GET.get('page', 1)  # Get the current page number
    page_obj = paginator.get_page(page_number)

    context = {
        'schedule':schedule,
        'loan_limit':loan_limit,
        'dis_principal':dis_principal,
        'br':br,
        'fullName':fullName,
        'p_fee':p_fee,
        'principal':principal,
        'page_obj':page_obj,
        'paginator':paginator,
        'updateForm':updateForm,
        'items':items,
        }

    return render(request, 'dashboard/loan_shedule.html', context)

def decline_loan(request, pk):
    item = Loan.objects.get(id=pk)
    item.delete()
    return redirect('dashboard-applicants')

def save_loan(request, pk,):
    item = Loan.objects.get(id=pk)
    item.status = 'Processing'
    item.save()
    return redirect('dashboard-approve-loan')

def approve_loan(request):
    items = Loan.objects.filter(status__in = ['Approved', 'Processing'])
    processLoan = []
    for i in items:
        principle = i.principal
        fee = i.processingFee
        convertFee = fee/100
        p_fee = principle * convertFee
        disbursed = principle - p_fee
        FirstName = i.borrower.firstName 
        SecondName = i.borrower.secondName
        Title = i.borrower.title
        Email = i.borrower.mail
        PhoneNumber = i.borrower.phone
        FullName = f'{Title}. {FirstName} {SecondName}'
        loanNumber = i.loanNo
        processLoan.append({
            'pk':i.pk,
            'loanNumber':loanNumber,
            'principle':principle,
            'fee':fee,
            'p_fee':p_fee,
            'FullName':FullName,
            'Email':Email,
            'PhoneNumber':PhoneNumber,
            'disbursed':disbursed,


        })

    context = {
        'processLoan':processLoan,
    }
    return render(request, 'dashboard/approve_loan.html', context)

def process_loan(request, pk):
    
    # Logic for processing the loan
    loan = Loan.objects.get(id = pk)    
    duration = loan.durationPer
    cycle = loan.repayment_cycle

    if duration == 'year' and cycle == 'monthly': 
        num_payment = loan.loanDuration
        num_payments = num_payment * 12
        # Get the release date and calculate the next payment date
        release_date = loan.release_date
        next_payment_date = release_date + relativedelta(months=1, day=5)  # Assuming the 5th day of the month

    elif duration == 'year' and cycle == 'yearly':   
        num_payment = loan.loanDuration
        # Get the release date and calculate the next payment date
        release_date = loan.release_date
        next_payment_date = release_date + relativedelta(year=1, months=1)  # Assuming the 5th day of the month

    elif duration == 'year' and cycle == 'weekly':
        num_payment = loan.loanDuration
        num_payments = num_payment * 52
        # Get the release date and calculate the next payment date
        release_date = loan.release_date
        next_payment_date = release_date + relativedelta(week=1, weekday=7)  # Assuming the 5th day of the month

    elif duration == 'year' and cycle == 'daily':
        num_payment = loan.loanDuration
        num_payments = num_payment * 365
        # Get the release date and calculate the next payment date
        release_date = loan.release_date
        next_payment_date = release_date + relativedelta(days=1, day=1)  # Assuming the 5th day of the month

    elif duration == 'month' and cycle == 'monthly':
        num_payment = loan.loanDuration
        num_payments = num_payment 
        # Get the release date and calculate the next payment date
        release_date = loan.release_date
        next_payment_date = release_date + relativedelta(months=1, day=5)  # Assuming the 5th day of the month

    elif duration == 'month' and cycle == 'yearly':
        num_payment = loan.loanDuration
        num_payments = math.ceil(num_payment / 12)
        # Get the release date and calculate the next payment date
        release_date = loan.release_date
        next_payment_date = release_date + relativedelta(year=1, month=1)  # Assuming the 5th day of the month

    elif duration == 'month' and cycle =='weekly':
        num_payment = loan.loanDuration
        num_payments = num_payment * 4
        # Get the release date and calculate the next payment date
        release_date = loan.release_date
        next_payment_date = release_date + relativedelta(week=1, weekday=7)  # Assuming the 5th day of the month

    elif duration == 'month' and cycle == 'daily':
        num_payment = loan.loanDuration
        num_payments = num_payment * 30
        # Get the release date and calculate the next payment date
        release_date = loan.release_date
        next_payment_date = release_date + relativedelta(day=1, days=1)  # Assuming the 5th day of the month

    else:
        num_payment = loan.loanDuration
        num_payments = num_payment * 12
        # Get the release date and calculate the next payment date
        release_date = loan.release_date
        next_payment_date = release_date + relativedelta(months=1, day=5)  # Assuming the 5th day of the month

    schedule = loan_amortization(loan.principal, loan.loanInterest, num_payments)
    loan.status = 'Approved'
    loan.save()
    # Calculate monthly interest rate
    monthly_rate = loan.loanInterest / 12 / 100

    # Calculate monthly payment
    monthly_payment = (loan.principal * monthly_rate) / (1 - (1 + monthly_rate) ** -num_payments)

    # Initialize variables
    principal1 = monthly_payment * num_payments

    try:
        loan_account = LoanAccount.objects.get(loan = loan)
        loan_account.principleAmount = principal1
        
        loan_account = loan_account.save()
    except LoanAccount.DoesNotExist:
        loan_account = LoanAccount.objects.create(
            contributor=loan.borrower,
            principleAmount=principal1,
            amountDue=0,
            loan = loan  # Assign the loan to the loan account    
        )

    for payment in schedule:
        payment_date = next_payment_date        
        # Calculate the next payment date based on the repayment cycle
        if loan.repayment_cycle == 'monthly':
            next_payment_date += relativedelta(months=1)
        elif loan.repayment_cycle == 'yearly':
            next_payment_date += relativedelta(years=1)
        elif loan.repayment_cycle == 'weekly':
            next_payment_date += timedelta(weeks=1)
        elif loan.repayment_cycle == 'daily':
            next_payment_date += timedelta(days=1)
        
        LoanPaymentII.objects.create(
            MonthlyPayment=payment['monthly_payment'],
            loanAccount=loan_account,
            interest=payment['interest'],
            principlePayment=payment['principal_payment'],
            paymentDate=payment_date,
            balance = 0.0,
            status='Open'
        )
    loan_payment = LoanPaymentII.objects.filter(loanAccount=loan_account)
    
    context = {
        'loan_payment':loan_payment,
        'loan':loan,
        'loan_account':loan_account
    }
    return redirect('dashboard-disburse-loan', pk=loan.pk)

def disburse_loan(request, pk):
    loan = Loan.objects.get(id=pk)
    principal = loan.principal
    p_fee = loan.processingFee 
    convert_fee = p_fee / 100
    fee = principal * convert_fee
    disburse_Amount = principal - fee

    loan_account = LoanAccount.objects.get(loan=loan)
    payment_schedule = LoanPaymentII.objects.filter(loanAccount = loan_account)
    paginator = Paginator(payment_schedule, 17)  # 17 rows per page
    page_number = request.GET.get('page', 1)  # Get the current page number
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj':page_obj,
        'loan':loan,
        'fee':fee,
        'disburse_Amount':disburse_Amount,
        'loan_account':loan_account,
    }
    return render(request, 'dashboard/disburse_loan.html', context)

def delete_loan(request, pk):
    item = Loan.objects.get(id=pk)
    if request.method=='POST':
        item.delete()
        return redirect('dashboard-approve-loan')
    
    context = {
        'item': item
    }
    return render(request, 'dashboard/delete_loan.html', context)

def receipt(request):
     # Get all existing Claimed objects
    existing_claimed_objs = Claimed.objects.all()
    existing_transaction_ids = set(existing_claimed_objs.values_list('transactionId', flat=True))

    # Get all Payment objects linked to member phone numbers
    member_phone_numbers = Member.objects.values_list('phone', flat=True)
    payment_objs = Payment.objects.filter(accountReference__in=member_phone_numbers)
     # Query for Payment objects not linked to member phone numbers
    non_member_payment_objs = Payment.objects.exclude(accountReference__in=member_phone_numbers)

    # Iterate over the Payment objects
    for payment_obj in payment_objs:
        # Check if the transactionId already exists in Claimed objects
        if payment_obj.transactionId in existing_transaction_ids:
            pass
            # Update the existing Claimed object's status to 'claimed'
           # existing_claimed_objs.filter(transactionId=payment_obj.transactionId).update(status='claimed')
        else:
                if payment_obj.phoneNumber in member_phone_numbers:
                # Create a new Claimed object with status as 'unclaimed'
                    claimed1 = Claimed.objects.create(
                        accountReference=payment_obj.accountReference,
                        paidAmount=payment_obj.paidAmount,
                        paymentDate=payment_obj.paymentDate,
                        transactionId=payment_obj.transactionId,
                        phoneNumber=payment_obj.phoneNumber,
                        fullName=payment_obj.fullName,
                        invoiceName=payment_obj.invoiceName,
                        externalReference=payment_obj.externalReference,
                        status='claimed'
                    )
                else:
                    # Create a new Claimed object with status as 'claimed'
                    claimed1 = Claimed.objects.create(
                        accountReference=payment_obj.accountReference,
                        paidAmount=payment_obj.paidAmount,
                        paymentDate=payment_obj.paymentDate,
                        transactionId=payment_obj.transactionId,
                        phoneNumber=payment_obj.phoneNumber,
                        fullName=payment_obj.fullName,
                        invoiceName=payment_obj.invoiceName,
                        externalReference=payment_obj.externalReference,
                        status='claimed'
                    )
                    if claimed1.invoiceName == 'savings':
                        T_savings = Total_Amount.objects.get(name = 'savings')
                        savings = T_savings.amount
                        payment = claimed1.paidAmount
                        savings += payment
                        T_savings.save()
                        
                    elif claimed1.invoiceName == 'loan':
                        T_savings = Total_Amount.objects.get(name = 'loans')
                        savings = T_savings.amount
                        payment = claimed1.paidAmount
                        savings += payment
                        T_savings.save()
                    elif claimed1.invoiceName == 'shares':
                        T_savings = Total_Amount.objects.get(name = 'shares')
                        savings = T_savings.amount
                        payment = claimed1.paidAmount
                        savings += payment
                        T_savings.save()
                    else:
                        claimed1.invoiceName = 'savings'
                        claimed1.save()
                

    # Iterate over the Payment objects
    for non_member_payment_obj in non_member_payment_objs:
        # Check if the transactionId already exists in Claimed objects
        if non_member_payment_obj.transactionId in existing_transaction_ids:
            pass
            # Update the existing Claimed object's status to 'claimed'
           # existing_claimed_objs.filter(transactionId=non_member_payment_obj.transactionId).update(status='claimed')
        else:
            if non_member_payment_obj.phoneNumber in member_phone_numbers:
            # Create a new Claimed object with status as 'unclaimed'
                claimed1 = Claimed.objects.create(
                    accountReference=non_member_payment_obj.accountReference,
                    paidAmount=non_member_payment_obj.paidAmount,
                    paymentDate=non_member_payment_obj.paymentDate,
                    transactionId=non_member_payment_obj.transactionId,
                    phoneNumber=non_member_payment_obj.phoneNumber,
                    fullName=non_member_payment_obj.fullName,
                    invoiceName=non_member_payment_obj.invoiceName,
                    externalReference=non_member_payment_obj.externalReference,
                    status='unclaimed'
                )
            else:
                # Create a new Claimed object with status as 'claimed'
                claimed1 = Claimed.objects.create(
                    accountReference=non_member_payment_obj.accountReference,
                    paidAmount=non_member_payment_obj.paidAmount,
                    paymentDate=non_member_payment_obj.paymentDate,
                    transactionId=non_member_payment_obj.transactionId,
                    phoneNumber=non_member_payment_obj.phoneNumber,
                    fullName=non_member_payment_obj.fullName,
                    invoiceName=non_member_payment_obj.invoiceName,
                    externalReference=non_member_payment_obj.externalReference,
                    status='unclaimed'
                )
                if claimed1.invoiceName == 'savings':
                    T_savings = Total_Amount.objects.get(name = 'savings')
                    savings = T_savings.amount
                    payment = claimed1.paidAmount
                    savings += payment
                    T_savings.save()
                    
                elif claimed1.invoiceName == 'loan':
                    T_savings = Total_Amount.objects.get(name = 'loans')
                    savings = T_savings.amount
                    payment = claimed1.paidAmount
                    savings += payment
                    T_savings.save()
                elif claimed1.invoiceName == 'shares':
                    T_savings = Total_Amount.objects.get(name = 'shares')
                    savings = T_savings.amount
                    payment = claimed1.paidAmount
                    savings += payment
                    T_savings.save()
                else:
                    claimed1.invoiceName = 'savings'
                    claimed1.save()
                

    # Retrieve all Claimed objects after the updates ordered by date
    cl = Claimed.objects.order_by('-paymentDate')

    paginator = Paginator(cl, 23)  # 20 rows per page
    page_number = request.GET.get('page', 1)  # Get the current page number
    page_obj = paginator.get_page(page_number)

    context = {
        'payment_obj': payment_objs,
        'cl': cl,
        'page_obj':page_obj,
    }

    return render(request, 'dashboard/receipt.html', context)

def contribute(request):
    ctt = Contribution.objects.all()
    contribution = ctt.aggregate(total_contribution=Sum('contributionAmount'))['total_contribution'] or 0
    Savings = ctt.aggregate(total_contribution=Sum('savingAmount'))['total_contribution'] or 0
    insured = ctt.aggregate(total_contribution=Sum('insuaranceAmount'))['total_contribution'] or 0

    context = {
       'ctt':ctt, 
       'contribution':contribution,
       'Savings':Savings,
       'insured':insured,
    }    
    return render(request, 'dashboard/contribute.html', context)

def applicants(request):
    cl = Claimed.objects.filter(status = 'claimed')
    manambaz = cl.values_list('accountReference', flat=True).distinct()
    mb = Member.objects.filter(phone__in = manambaz)

    applicant=[]
    for i in mb:
        FirstName = i.firstName
        SecondName = i.secondName
        Title = i.title
        mail = i.mail
        WorkStatus = i.workStatus
        fullName = f'{Title}. {FirstName} {SecondName}'
        PhoneNumber = i.phone
        nationID = i.te_id
        ctt = Contribution.objects.get(contributor = i)
        savings = ctt.savingAmount or 0
        
        lon = Loan.objects.all()
        ln = lon.filter(borrower = i).first()
        if ln:
            principalLoan = ln.principal or 0
            monthly_rate = ln.loanInterest / 100
            pk2 = ln.pk
        else:
            principalLoan = 0.0
            monthly_rate = 0.0  
            pk2 = 'None'  
        LoanInt = principalLoan * monthly_rate
        currentLoan = principalLoan + LoanInt or 0
        limit = savings * 3 or 0
        loan_limit = Decimal(limit) - Decimal(currentLoan) or Decimal(0)

        applicant.append({
            'pk' : i.pk,
            'pk2' : pk2,
            'FullName':fullName,
            'PhoneNumber': PhoneNumber,
            'savings':savings,
            'WorkStatus':WorkStatus,
            'loan_limit':loan_limit,
            'currentLoan':currentLoan,
            'nationID':nationID,
            'mail':mail,

        })
        context ={
            'applicant':applicant,
        }

    return render(request, 'dashboard/applicants.html', context)

def claimat(request, pk):
    member = Member.objects.all()
    cl = Claimed.objects.get(id=pk)

    context = {
        'member':member,
        'cl':cl,
        
    }

    return render(request, 'dashboard/claimat.html', context)

def repaying_loan(request, pk):
    ta_loans = Total_Amount.objects.get(name = 'loans')
    ta_p_fee = Total_Amount.objects.get(name = 'p_fee')
    loan = Loan.objects.get(pk = pk)
    loan.status = 'Repaying'
    loan.save()
    
    ta_loans.amount += loan.principal

    fee = loan.processingFee
    #convert fee from % to decimal
    mal = fee / 100
    p_fee = loan.principal * mal
    ta_p_fee.amount += Decimal(p_fee)
    ta_loans.save()
    ta_p_fee.save()


    return redirect('dashboard-view-loan')

def save_claim(request, pk,pk1, type):
    cl = Claimed.objects.get(id=pk)
    mb = Member.objects.get(id = pk1)

    if type == 'shares':
        cl.invoiceName = 'shares'
        cl.accountReference = mb.phone
        cl.status = 'claimed'
    elif type == 'loan':
        cl.invoiceName = 'loan'
        cl.accountReference = mb.phone
        cl.status = 'claimed'

    elif type == 'savings':
        cl.invoiceName = 'savings'
        cl.accountReference = mb.phone
        cl.status = 'claimed'
    # Save the modified claim object
    cl.save()

    return redirect('dashboard-receipt')

def saving(request, pk):
    mb = Member.objects.get(pk = pk)
    fullname = f'{mb.title} {mb.firstName} {mb.secondName}'
    claim = Claimed.objects.filter(status = 'claimed', invoiceName = 'savings')

    mbClaims = claim.filter(accountReference = mb.phone)
    try:
        ctt = Contribution.objects.get(contributor=pk)
        
    except Contribution.DoesNotExist:
        ctt = 0
    
    paginator = Paginator(mbClaims, 24)  # 24 rows per page
    page_number = request.GET.get('page', 1)  # Get the current page number
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj':page_obj,
        'ctt':ctt,
        'fullname':fullname,
    }
    return render(request, 'dashboard/saving.html', context)

def see_loan(request, pk):
    loan = Loan.objects.get(pk = pk)
    if loan.status == 'Open':
        return redirect('dashboard-loan-shedule', pk=pk)
    elif loan.status == 'Processing':
        return redirect('dashboard-approve-loan')
    elif loan.status == 'Approved':
        return redirect('dashboard-disburse-loan', pk=pk)
    elif loan.status == 'Repaying':
        return redirect('dashboard-payment-plan', pk=pk)
    elif loan.status == 'Cleared':
        return redirect('dashboard-payment-plan', pk=pk)

def payment_plan(request, pk):
    loan = Loan.objects.get(pk = pk)
    item = loan.borrower
    loan_no = loan.loanNo
    FullName = f'{loan.borrower.title} {loan.borrower.firstName} {loan.borrower.secondName}'
    loan_account = LoanAccount.objects.get(loan = loan)

    lap = loan_account.principleAmount
    laDue = loan_account.amountDue
    lp = LoanPaymentII.objects.filter(loanAccount = loan_account)
    # Sort loan payments by paymentDate in ascending order
    lp = lp.order_by('paymentDate')
    lp_count = lp.count()

    if loan_account.principleAmount > 0:
        ctt = Claimed.objects.filter(accountReference=item.phone, invoiceName= 'loan')
        ta_interests = Total_Amount.objects.get(name = 'interests')
        ta_loans = Total_Amount.objects.get(name = 'loans')

        lp1 = LoanPaymentII.objects.filter(loanAccount = loan_account)
        lp = lp1.exclude(status = 'Cleared')
        # Sort loan payments by paymentDate in ascending order
        lp = lp.order_by('paymentDate')
        
        existing_lpr_objs = loanPaymentsreceipts.objects.filter(accountReference = item.phone)
        lpr_transaction_ids = set(existing_lpr_objs.values_list('transactionId', flat=True))
        # Query for Claimed_Payment objects not linked to loan Payments receipts
        notLinkedPayments = ctt.exclude(transactionId__in=lpr_transaction_ids)
        nlp_count = notLinkedPayments.count()
        if nlp_count > 0:                
            for i in notLinkedPayments:
                cb = loanPaymentsreceipts.objects.create(
                paidAmount = i.paidAmount,
                accountReference=i.accountReference,
                paymentDate = i.paymentDate,
                transactionId = i.transactionId
                )
                cb.contributor.add(item)
            
            lpr = loanPaymentsreceipts.objects.filter(accountReference = item.phone)

            # Iterate over loan payments and deduct from paidAmount
            for payment in lp:
                if loan.repayment_cycle == 'monthly':
                    lpr_monthly = lpr.filter(paymentDate__month=payment.paymentDate.month)
                    total_paid = lpr_monthly.aggregate(total_paid=Sum('paidAmount'))['total_paid'] or 0
                elif loan.repayment_cycle == 'daily':
                    lpr_monthly = lpr.filter(paymentDate__day=payment.paymentDate.day)
                    total_paid = lpr_monthly.aggregate(total_paid=Sum('paidAmount'))['total_paid'] or 0
                elif loan.repayment_cycle == 'weekly':
                    lpr_monthly = lpr.filter(paymentDate__weekday=payment.paymentDate.weekday)
                    total_paid = lpr_monthly.aggregate(total_paid=Sum('paidAmount'))['total_paid'] or 0
                elif loan.repayment_cycle == 'yearly':
                    lpr_monthly = lpr.filter(paymentDate__year=payment.paymentDate.year)
                    total_paid = lpr_monthly.aggregate(total_paid=Sum('paidAmount'))['total_paid'] or 0

                current_date = timezone.localdate()  # Get the current date in the timezone defined in Django settings
                if payment.paymentDate < current_date:
                    if total_paid == payment.MonthlyPayment:
                        loan_account.principleAmount -= payment.MonthlyPayment
                        loan_account.loan.principal -= payment.principlePayment
                        payment.balance = 0
                        payment.status = 'Cleared'
                        ta_interests.amount += payment.interest
                        ta_loans.amount -= payment.principlePayment
                    elif total_paid > payment.MonthlyPayment:
                        payment.balance =  total_paid - payment.MonthlyPayment
                        loan_account.principleAmount -= payment.MonthlyPayment                            
                        loan_account.amountDue += payment.balance
                        payment.status = 'Cleared'
                        ta_interests.amount += payment.interest
                        ta_loans.amount -= payment.principlePayment
                        payment.balance = 0
                    elif total_paid == 0:
                        laa = loan_account.amountDue
                        payment.status = 'Missed'
                        payment.balance = payment.MonthlyPayment - total_paid 
                        pb = payment.balance
                        loan_account.amountDue -= payment.balance
                        payment.balance -= laa
                        if loan_account.amountDue >= 0:
                            payment.status = 'Cleared'
                            ta_interests.amount += payment.interest
                            ta_loans.amount -= payment.principlePayment
                            loan_account.principleAmount -= payment.MonthlyPayment 
                            payment.balance = 0.0
                        elif payment.balance < pb and loan_account.amountDue < 0 :
                            payment.status = 'Arrears'
                    elif total_paid < payment.MonthlyPayment:
                        if payment.status == 'Arrears':
                            laa = loan_account.amountDue
                            payment.balance = payment.MonthlyPayment - total_paid 
                            pb = payment.balance
                            loan_account.amountDue -= payment.balance
                            payment.balance -= laa
                            if loan_account.amountDue >= 0:
                                payment.status = 'Cleared'
                                ta_interests.amount += payment.interest
                                ta_loans.amount -= payment.principlePayment
                                loan_account.principleAmount -= payment.MonthlyPayment 
                                payment.balance = 0.0
                            elif payment.balance < pb and loan_account.amountDue < 0 :
                                payment.status = 'Arrears'

                        else:
                            payment.status = 'Arrears'
                            payment.balance = payment.MonthlyPayment - total_paid 
                            loan_account.amountDue -= payment.balance
                    """       
                    else:
                        payment.status = 'Missed'"""
                elif payment.paymentDate == current_date:
                    if total_paid == payment.MonthlyPayment:
                        loan_account.principleAmount -= payment.MonthlyPayment
                        loan_account.loan.principal -= payment.principlePayment
                        payment.balance = 0
                        payment.status = 'Cleared'
                        ta_interests.amount += payment.interest
                        ta_loans.amount -= payment.principlePayment
                    elif total_paid > payment.MonthlyPayment:
                        payment.balance =  total_paid - payment.MonthlyPayment
                        loan_account.principleAmount -= payment.MonthlyPayment                            
                        loan_account.amountDue += payment.balance
                        payment.status = 'Cleared'
                        ta_interests.amount += payment.interest
                        ta_loans.amount -= payment.principlePayment
                        payment.balance = 0

                payment.save()
            loan_account.save()
        else:
            lpr = loanPaymentsreceipts.objects.filter(accountReference = item.phone)
            # Iterate over loan payments and deduct from paidAmount
            for payment in lp:
                if loan.repayment_cycle == 'monthly':
                    lpr_monthly = lpr.filter(paymentDate__month=payment.paymentDate.month)
                    total_paid = lpr_monthly.aggregate(total_paid=Sum('paidAmount'))['total_paid'] or 0
                elif loan.repayment_cycle == 'daily':
                    lpr_monthly = lpr.filter(paymentDate__day=payment.paymentDate.day)
                    total_paid = lpr_monthly.aggregate(total_paid=Sum('paidAmount'))['total_paid'] or 0
                elif loan.repayment_cycle == 'weekly':
                    lpr_monthly = lpr.filter(paymentDate__weekday=payment.paymentDate.weekday)
                    total_paid = lpr_monthly.aggregate(total_paid=Sum('paidAmount'))['total_paid'] or 0
                elif loan.repayment_cycle == 'yearly':
                    lpr_monthly = lpr.filter(paymentDate__year=payment.paymentDate.year)
                    total_paid = lpr_monthly.aggregate(total_paid=Sum('paidAmount'))['total_paid'] or 0

                current_date = timezone.localdate()  # Get the current date in the timezone defined in Django settings
                if payment.paymentDate < current_date:
                    if total_paid == payment.MonthlyPayment:
                        loan_account.principleAmount -= payment.MonthlyPayment
                        loan_account.loan.principal -= payment.principlePayment
                        payment.balance = 0
                        payment.status = 'Cleared'
                        ta_interests.amount += payment.interest
                        ta_loans.amount -= payment.principlePayment
                    elif total_paid > payment.MonthlyPayment:
                        payment.balance =  total_paid - payment.MonthlyPayment
                        loan_account.principleAmount -= payment.MonthlyPayment                            
                        loan_account.amountDue += payment.balance
                        payment.status = 'Cleared'
                        ta_interests.amount += payment.interest
                        ta_loans.amount -= payment.principlePayment
                        payment.balance = 0
                    elif total_paid == 0:
                        laa = loan_account.amountDue
                        payment.status = 'Missed'
                        payment.balance = payment.MonthlyPayment - total_paid 
                        pb = payment.balance
                        loan_account.amountDue -= payment.balance
                        payment.balance -= laa
                        if loan_account.amountDue >= 0:
                            payment.status = 'Cleared'
                            ta_interests.amount += payment.interest
                            ta_loans.amount -= payment.principlePayment
                            loan_account.principleAmount -= payment.MonthlyPayment 
                            payment.balance = 0.0
                        elif payment.balance < pb and loan_account.amountDue < 0 :
                            payment.status = 'Arrears'
                    elif total_paid < payment.MonthlyPayment:
                        if payment.status == 'Arrears':
                            laa = loan_account.amountDue
                            payment.balance = payment.MonthlyPayment - total_paid 
                            pb = payment.balance
                            loan_account.amountDue -= payment.balance
                            payment.balance -= laa
                            if loan_account.amountDue >= 0:
                                payment.status = 'Cleared'
                                ta_interests.amount += payment.interest
                                ta_loans.amount -= payment.principlePayment
                                loan_account.principleAmount -= payment.MonthlyPayment 
                                payment.balance = 0.0
                            elif payment.balance < pb and loan_account.amountDue < 0 :
                                payment.status = 'Arrears'

                        else:
                            payment.status = 'Arrears'
                            payment.balance = payment.MonthlyPayment - total_paid 
                            loan_account.amountDue -= payment.balance
                    """       
                    else:
                        payment.status = 'Missed'"""
                elif payment.paymentDate == current_date:
                    if total_paid == payment.MonthlyPayment:
                        loan_account.principleAmount -= payment.MonthlyPayment
                        loan_account.loan.principal -= payment.principlePayment
                        payment.balance = 0
                        payment.status = 'Cleared'
                        ta_interests.amount += payment.interest
                        ta_loans.amount -= payment.principlePayment
                    elif total_paid > payment.MonthlyPayment:
                        payment.balance =  total_paid - payment.MonthlyPayment
                        loan_account.principleAmount -= payment.MonthlyPayment                            
                        loan_account.amountDue += payment.balance
                        payment.status = 'Cleared'
                        ta_interests.amount += payment.interest
                        ta_loans.amount -= payment.principlePayment
                        payment.balance = 0

                payment.save()
            loan_account.save()

    else: 
        loan.status == 'Cleared'
        loan.save()

    paginator = Paginator(lp, 14)  # 14 rows per page
    page_number = request.GET.get('page', 1)  # Get the current page number
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj':page_obj,
        'paginator':paginator,
        'loan_no':loan_no,
        'FullName':FullName,
        'lap':lap,
        'laDue':laDue,
        'lp_count':lp_count,
    }
    return render(request, 'dashboard/payment_plan.html', context)
    
    
   