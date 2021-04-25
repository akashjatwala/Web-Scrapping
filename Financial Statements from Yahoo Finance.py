# Scrapping Financial Statements from Yahoo Finance, and saving the data in CSV
# The stock symbol must be as per Yahoo Finance


from lxml import html
import requests
import numpy as np
import pandas as pd
from tkinter import messagebox


def parse_rows(table_rows): # extracting values from the table rows
    parsed_rows=[]
    for table_row in table_rows:
        parsed_row=[]
        el=table_row.xpath("./div")
        none_count=0
        for rs in el:
            try:
                (text,)=rs.xpath('.//span/text()[1]')
                parsed_row.append(text)
            except ValueError:
                parsed_row.append(np.NaN)
                none_count+=1
        if (none_count<4):
            parsed_rows.append(parsed_row)
    return pd.DataFrame(parsed_rows)

def clean_data(df): # cleaning the table
    df.columns=df.iloc[0]
    df=df.iloc[1:,]
    df=df.T
    df.columns=df.iloc[0]
    df.drop(df.index[0],inplace=True)
    df.index.name="" 
    return df

def scrape_table(url): # scrapping data
    page=requests.get(url)
    tree=html.fromstring(page.content)
    table_rows=tree.xpath("//div[contains(@class, 'D(tbr)')]")  
    df=parse_rows(table_rows)
    df=clean_data(df)
    return df

def convert_to_numeric(column):
    first_col=[i.replace(',','') for i in column]
    second_col=[i.replace('-','') for i in first_col]
    final_col=pd.to_numeric(second_col)
    return final_col

def save(file_type): 
    response=messagebox.askquestion("Save","Do you want to save the "+file_type+"?")
    if(response=='yes'):
        return True
    else:
        return False

symbol=input("Please enter the Symbol: ")


# financial statements

url_is="https://finance.yahoo.com/quote/"+symbol+"/financials?p="+symbol
url_bs="https://finance.yahoo.com/quote/"+symbol+"/balance-sheet?p="+symbol
url_cf="https://finance.yahoo.com/quote/"+symbol+"/cash-flow?p="+symbol

df_income_statement=scrape_table(url_is)
df_income_statement=df_income_statement.fillna('-')

df_balance_sheet=scrape_table(url_bs)
df_balance_sheet=df_balance_sheet.fillna('-')

df_cashflow_statement=scrape_table(url_cf)
df_cashflow_statement=df_cashflow_statement.fillna('-')


income_st_print=df_income_statement.T
print("Income Statement:")
print(income_st_print)

c=save("Income Statement")
if(c==True):
    income_st_print.to_csv("Income Statement.csv")
    
balance_sht_print=df_balance_sheet.T
print("\nBalance Sheet:")
print(balance_sht_print)

c=save("Balance Sheet")
if(c==True):
    income_st_print.to_csv("Balance Sheet.csv")
    
cashflow_st_print=df_cashflow_statement.T
print("\nCash Flow Statement:")
print(cashflow_st_print)

c=save("Cash Flow Statement")
if(c==True):
    cashflow_st_print.to_csv("Cash Flow Statement.csv")
    

# converting dataframes to numeric values

headers=list(df_income_statement.columns) 
for column in headers:
    df_income_statement[column]=convert_to_numeric(df_income_statement[column])
        
balance_sheet_columns=list(df_balance_sheet.columns)
if("Deferred revenues" in balance_sheet_columns):
    df_balance_sheet=df_balance_sheet.drop("Deferred revenues",1)   
headers=list(df_balance_sheet.columns) 
for column in headers:
    df_balance_sheet[column]=convert_to_numeric(df_balance_sheet[column])
    
headers=list(df_cashflow_statement.columns) 
for column in headers:
    df_cashflow_statement[column]=convert_to_numeric(df_cashflow_statement[column]) 
    
