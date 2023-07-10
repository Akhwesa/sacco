

def loan_amortization(principal, interestRate, num_payments):
    
    # Calculate monthly interest rate
    monthly_rate = interestRate / 12 / 100

    # Calculate monthly payment
    monthly_payment = (principal * monthly_rate) / (1 - (1 + monthly_rate) ** -num_payments)

    # Initialize variables
    principal1 = monthly_payment * num_payments
    remaining_principal = monthly_payment * num_payments
    month = 0
    amortization_schedule = []

    for _ in range(num_payments):
        # Calculate interest for the current period
        interest = remaining_principal * monthly_rate

        # Calculate principal repayment for the current period
        principal_payment = monthly_payment - interest

        # Update the remaining principal
        remaining_principal = remaining_principal - monthly_payment

        #update month
        month += 1

        # Add the current period's details to the amortization schedule
        amortization_schedule.append({            
            'monthly_payment':monthly_payment, 
            'interest':interest,
            'month':month, 
            'principal_payment':principal_payment, 
            'remaining_principal':remaining_principal,
        })    
    return amortization_schedule