from django.urls import path
from . import views

urlpatterns = [
path('dashboard/', views.index, name='dashboard-index'),
path('view/loan/', views.view_loan, name='dashboard-view-loan'),
path('add/loan/<int:pk>/', views.add_loan, name='dashboard-add-loan'),
path('delete/loan/<int:pk>/', views.delete_loan, name='dashboard-delete-loan'),
path('disburse/loan/<int:pk>/', views.disburse_loan, name='dashboard-disburse-loan'),
path('loan/shedule/<int:pk>/', views.loan_shedule, name='dashboard-loan-shedule'),
path('process/loan/<int:pk>/', views.process_loan, name='process-loan'),
path('see/loan/<int:pk>/', views.see_loan, name='see-loan'),
path('receipt/', views.receipt, name='dashboard-receipt'),
path('contribute/', views.contribute, name='dashboard-contribute'),
path('monthly/contribute/<int:current_month>/', views.monthly_contribute, name='dashboard-monthly-contribute'),
path('monthly/receipt/<int:pk>/', views.monthly_receipt, name='dashboard-monthly-receipt'),
path('payment/plan/<int:pk>/', views.payment_plan, name='dashboard-payment-plan'),
path('payment/loan/', views.monthly_loan, name='dashboard-monthly-loan'),
path('update_current_month/', views.update_current_month, name='update_current_month'),
path('applicants/', views.applicants, name='dashboard-applicants'),
path('claimat/<int:pk>/', views.claimat, name='dashboard-claimat'),
path('saving/<int:pk>/', views.saving, name='dashboard-saving'),
path('approve/loan/', views.approve_loan, name='dashboard-approve-loan'),
path('save-claim/<int:pk>/<int:pk1>/<str:type>/', views.save_claim, name='save_claim'),
path('repaying/loan/<int:pk>/', views.repaying_loan, name='dashboard-repaying-loan'),
path('save-loan/<int:pk>/', views.save_loan, name='save_loan'),
path('decline-loan/<int:pk>/', views.decline_loan, name='decline_loan'),

]