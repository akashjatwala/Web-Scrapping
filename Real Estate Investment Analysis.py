# Scrapping Property Listing Data from Remax Canada, and Zoopla UK, and Performing Real-Estate Investment Analysis


from requests import get
from bs4 import BeautifulSoup
import pandas as pd
import datetime 
import numpy as np
import re
from collections import OrderedDict
from dateutil.relativedelta import *


def invalid():
    print("You had entered an Invalid Data") 

def property_price_remax(url): # getting price from the url
    response=get(url)
    response_text=response.text
    html_soup=BeautifulSoup(response_text,'html.parser')
    price=html_soup.find('h2',{'class':'price'}).text
    price=(float)(''.join(re.findall('\d+', price)))
    return price
    
def property_price_zoopla(url): # getting price from the url
    response=get(url)
    html_soup=BeautifulSoup(response,'html.parser')
    price=html_soup.find('p', {'class': 'ui-pricing__main-price ui-text-t4'}).text
    price=(float)(''.join(re.findall('\d+', price)))
    return price

def net_operating_income(rent,tax_rate,price,mortgage,property_rep,property_vac,insurance): # monthly net operating income
    prop_managment=rent*property_main
    prop_tax=price*(tax_rate/12)
    prop_repairs=(price*property_rep)/12
    vacancy=(rent*property_vac)
    net_income=rent-prop_managment-prop_tax-prop_repairs-vacancy-(insurance/12)-mortgage
    net_expenses=rent-net_income
    return net_income,net_expenses

def valid_date(year,month,day): # checking whether a date is valid or not
    isvaliddate=True
    try:
        datetime.date(int(year),int(month),int(day))
    except ValueError:
        isvaliddate=False
    if(isvaliddate):
        return True
    else:
        return False  

def amortization(principal,int_rate,years,pmt,addl_principal,start_date): # calculating amortization 
    p=1
    beg_balance=principal
    end_balance=principal
    while(end_balance>0):
        # recalculating the interest based on the current balance
        interest=round(((int_rate/12)*beg_balance),2)
        
        # determining whether the payment of this period will pay off the loan
        pmt=min(pmt,beg_balance+interest)
        principal=pmt-interest
        
        # adjusting additional principal payments
        addl_principal=min(addl_principal,beg_balance-principal)
        end_balance=beg_balance-(principal+addl_principal)

        yield OrderedDict([('Month',start_date),
                           ('Period',p),
                           ('Begining Balance',beg_balance),
                           ('Monthly Mortgage',pmt),
                           ('Principal',principal),
                           ('Interest',interest),
                           ('Additional Payment',addl_principal),
                           ('End Balance',end_balance)])
        
        # incrementing the period, balance and date
        p+=1
        start_date+=relativedelta(months=1)
        beg_balance=end_balance

def amortization_table(principal,int_rate,years,addl_principal,start_date):    
    # calculating emi
    payment=-round(np.pmt(int_rate/12,years*12,principal),2)
    
    # generating the amortization schedule
    schedule=pd.DataFrame(amortization(principal,int_rate,years,payment,addl_principal,start_date))
    schedule=schedule[["Period","Month","Begining Balance","Monthly Mortgage","Principal","Interest","Additional Payment","End Balance"]]
    schedule["Month"]=pd.to_datetime(schedule["Month"])
    
    # creating a summary statistics table
    payoff_date=schedule["Month"].iloc[-1]
    payoff_date=datetime.datetime.date(payoff_date)
    stats=pd.Series([payoff_date,schedule["Period"].count(),int_rate,years,principal,payment,addl_principal,schedule["Interest"].sum()],
                    index=["Mortgage Payoff Date","Number of Payments","Mortgage Interest Rate","Mortgage Years","Principal Payment",
                    "Monthly Mortgage Payment","Additional Principal Payment","Total Interest Payment"])
    
    return schedule,stats


# getting inputs from the user

# property url
print("Please Select your Property Listing Site:")
print("1. Remax Canada")
print("2. Zoopla UK")
while(True):
    ch=(int)(input("Please enter your choice: "))
    if(ch==1 or ch==2):
        break
    else:
        invalid()    

if(ch==1):
    url=input("Please enter the URL to the Property Listing: ")
    price=property_price_remax(url)
else:
    url=input("Please enter the URL to the Property Listing: ")
    price=property_price_zoopla(url)
    
while(True):
    downpayment_percent=(float)(input("Please enter the '%' of Down-Payment: "))
    if(downpayment_percent>0 and downpayment_percent<=80):
        break
    else:
        invalid()

while(True): # mortgage years
    mortgage_years=(int)(input("Please enter the Mortgage Years: "))
    if(mortgage_years<=5):
        invalid()
    else:
        break

while(True): # mortgage interest rate
    mortgage_int=(float)(input("Please enter the Mortgage Rate P.A. (%): "))
    if(mortgage_int>0 and mortgage_int<=15):
        break
    else:
        invalid()

additional_pay=(float)(input("Please enter the Additional Principal Payment: ")) # additional principal payment

while(True): # mortgage payment start date
    date_entry=input("Please enter the Mortgage Start Date in YYYY-MM-DD format: ")
    year,month,day=map(int,date_entry.split('-'))
    date_validity=valid_date(year,month,day)
    if(date_validity==True):
        start=datetime.date(year,month,day)
        if(start>=(datetime.date.today()-datetime.timedelta(days=365*mortgage_years)) and start<=datetime.date.today()):
            break
        else:
            invalid()

while(True): # property tax
    property_tax=(float)(input("Please enter the Property Tax Rate P.A. (%): "))
    if(property_tax>0 and property_tax<=30):
        break
    else:
        invalid()

while(True): # property insurance
    property_insurance=float(input("Please enter the Annual Property Insurance Premium: "))
    if(property_insurance>0):
        break
    else:
        invalid()

while(True): # monthly rental income
    rent_amt=(float)(input("Please enter the Monthly Rent Income: "))
    if(rent_amt<0):
        invalid()
    else:
        break
        
while(True): # property managing expense
    property_main=(float)(input("Please enter the Property Managing Expenses P.M. (%): "))
    if(property_main>=0 and property_main<=10):
        break
    else:
        invalid()

while(True): # property repairs
    property_rep=(float)(input("Please enter the Property Repairs Expenses P.A. (%): "))
    if(property_rep>=0 and property_rep<=10):
        break
    else:
        invalid()

while(True): # vacancy rate
    property_vac=(float)(input("Please enter the Property Vacancy Rate (%): "))
    if(property_vac>=0 and property_vac<=10):
        break
    else:
        invalid()

property_tax=property_tax/100
mortgage_int=mortgage_int/100
property_main=property_main/100
property_rep=property_rep/100
property_vac=property_vac/100
downpayment_percent=downpayment_percent/100


# analyzing the investment details
downpayment=price*downpayment_percent
mortgage=price-downpayment
monthly_mortgage=-np.pmt(mortgage_int/12,mortgage_years*12,mortgage)
net_income,net_expenses=net_operating_income(rent_amt,property_tax,price,monthly_mortgage,property_main,property_rep,property_vac)


# analyzing real-estate ratios
cash_flow=net_income-(monthly_mortgage+additional_pay)
rent_ratio=rent_amt/price
cap_rate=net_income/price
loan_value=mortgage/price
economic_value=net_income/cap_rate
debt_coverage=net_income/(monthly_mortgage*12)
debt_service=mortgage/net_income

# displaying the results
print("\nReal-Estate Investment Analysis:")
print("Price of the Property: ",price) 
print("Down Payment: ",downpayment)
print("Mortgage: ",mortgage)
print("Monthly Mortgage Payment: ",round(monthly_mortgage,2))
print("Monthly Rent Income: ",rent_amt)
print("Monthly Net Operating Income: ",round(net_income,2))
print("Monthly Net Operating Expenses: ",round(net_expenses,2))

print("\nReal_Estate Ratio Analysis:")
print("Cash Flow: ",round(cash_flow,2))
print("Rent Ratio: ",round(rent_ratio,2))
print("Capitalizatio Rate: ",round(cap_rate,2))
print("Economic Value: ",round(economic_value,2))
print("Loan Value: ",round(loan_value,2))
print("Debt Coverage Ratio: ",round(debt_coverage,2))
print("Debt Service Coverage Ratio: ",round(debt_service,2))


# mortgage amortization
df,stats=amortization_table(mortgage,mortgage_int,mortgage_years,addl_principal=additional_pay,start_date=start)

print("\nMortgage Summary:")
print(stats)

print("\nMortgage Amortization Schedule:")
print(df)
print("\nMortgage Amortization Schedule has been saved by the name: 'Mortgage Amortization Schedule.csv'")
df.to_csv("Mortgage Amortization Schedule.csv")

