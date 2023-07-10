from django.shortcuts import render,redirect
from django.contrib import messages
from .forms import addBorrower,updateMember
from .models import Member
from django.db.models import Sum
from dashboard.models import Loan

# Create your views here.
def view_borrower(request):

    items = Member.objects.all()
    loans = Loan.objects.all() 

    loanDetails = []
    for l in loans:
         borrower = l.borrower
         stat = l.status
         principal = l.principal
         product = l.loanProduct
         fullName = f"{borrower.firstName} {borrower.secondName}"
         title = borrower.title
         mobile = borrower.phone
         un_no = borrower.te_id
         Email = borrower.mail
         loanDetails.append({
              'name':fullName,
              'mobile':mobile,
              'mail': Email,
              'un_no':un_no,
              'status': stat,
              'principal':principal,
              'title':title,
              'product':product,
              'pk':l.borrower.pk
         })

    total_principal = loans.aggregate(total=Sum('principal'))['total']

# If total_principal is None, set it to 0
    total_principal = total_principal or 0  


    context = {
         'items':items,
         'loanDetails':loanDetails,
         'total_principal':total_principal,

    }

    return render(request, 'user/view_borrower.html', context)

def add_borrower(request):
    
    if request.method == 'POST':
            add_Borrower_form = addBorrower(request.POST)
            if add_Borrower_form.is_valid():
                add_Borrower_form.save()
                return redirect('user-view-member')
    else:
            add_Borrower_form = addBorrower()

    context = {
        'add_Borrower_form':add_Borrower_form,
    }

    return render(request, 'user/add_borrower.html', context)

def view_member(request):
    members = Member.objects.all()

    context = {
         'members':members,
    }

    return render(request,'user/view_member.html', context )

def view_borrower_group(request):


    return render(request, 'user/view_borrower_group.html')

def member_update(request, pk):
    mb = Member.objects.get(pk=pk)

    if request.method == 'POST':
        form = updateMember(request.POST, instance=mb)
        if form.is_valid():
            form.save()
            member_name = form.cleaned_data.get('firstName')
            messages.success(request, f'{member_name} profile was Updated successfully')
            return redirect('user-member-update', pk = pk)
    else:
        form = updateMember(instance=mb)

    context = {
          'mb':mb,
          'form':form
     }
    return render(request, 'user/member_update.html', context)

def member_delete(request, pk):
    item = Member.objects.get(id=pk)
    if request.method=='POST':
        item.delete()
        return redirect('dashboard-Member')
    
    context = {
        'item': item
    }
    return render(request, 'user/member_delete.html', context)