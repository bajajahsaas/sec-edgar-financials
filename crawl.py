
# coding: utf-8

# In[23]:


import json
import numpy as np
import pandas as pd
from edgar.financials import FinancialReportEncoder
from edgar.stock import Stock
'''
https://www.pingshiuanchua.com/blog/post/intro-to-colaboratory-and-linking-it-to-google-sheets
https://www.pingshiuanchua.com/blog/post/overpower-your-google-sheets-with-python

'''

def getData(ticket, ty, period='annual', year=2018, quarter=0):
    # period = 'annual' # or 'quarterly', which is the default
    # year = 2018 # can use default of 0 to get the latest
    # quarter = 1 # 1, 2, 3, 4, or default value of 0 to get the latest

    stock = Stock(ticket)
    try:
        filing = stock.get_filing(period, year, quarter)
        # financial reports (contain data for multiple years)
        if ty == 'income_statements':
            statements = filing.get_income_statements()
        elif ty == "balance_sheets":
            statements = filing.get_balance_sheets()
        elif ty == "cash_flows":
            statements = filing.get_cash_flows()

        jsonstr = FinancialReportEncoder().encode(statements)
        data = json.loads(jsonstr)

        # print(data.keys())  # dict_keys(['company', 'date_filed', 'reports'])
        listreports = data['reports']
        columns = []
        data = []

        print(type(listreports), len(listreports))
        for report in listreports:
            # listreports is a list of 3 dictionaries (all have same labels with different values)
            # print(report.keys())  # dict_keys(['date', 'months', 'map']): string, int, dict

            report = report['map']
            for dict in report.values():
                # print(map_key, report['map'][map_key].keys())  # dict_keys(['label', 'value'])
                label = dict['label']
                columns.append(label)
                # print('Label', label)

                value = dict['value']
                data.append(value)
                # print('Value', value)
            break

        sec_data = pd.DataFrame([data], columns=columns)
        sec_data = sec_data.transpose()
        sec_data.reset_index(inplace=True)
        sec_data['ind'] = np.arange(len(sec_data))
        sec_data.set_index("ind", inplace=True)
        return sec_data, True

    except:
        print('Invalid company input', cmp, ty, period, year, quarter)
        return None, False


# In[24]:


final_df = pd.DataFrame()
# cmpList = ['AAL', 'AAPL', 'ADBE', 'ADI', 'ADP', 'ADSK', 'ALGN', 'ALXN', 'AMAT', 'AMGN', 'AMZN', 'ASML', 'ATVI', 'AVGO',
#            'BIDU', 'BIIB', 'BKNG', 'BMRN', 'CA', 'CDNS', 'CELG', 'CERN', 'CHKP', 'CHTR', 'CMCSA', 'COST', 'CSCO', 'CSX',
#            'CTAS', 'CTRP', 'CTSH', 'CTXS', 'DISH', 'DLTR', 'EA', 'EBAY', 'ESRX', 'EXPE', 'FAST', 'FB', 'FISV', 'FOX',
#            'FOXA', 'GILD', 'GOOG', 'HAS', 'HOLX', 'HSIC', 'IDXX', 'ILMN', 'INCY', 'INTC', 'INTU', 'ISRG', 'JBHT', 'JD',
#            'KHC', 'KLAC', 'LBTYA', 'LBTYK', 'LRCX', 'MAR', 'MCHP', 'MDLZ', 'MELI', 'MNST', 'MSFT', 'MU', 'MXIM', 'MYL',
#            'NFLX', 'NTES', 'NVDA', 'ORLY', 'PAYX', 'PCAR', 'PYPL', 'QCOM', 'QRTEA', 'REGN', 'ROST', 'SBUX', 'SHPG',
#            'SIRI', 'SNPS', 'STX', 'SWKS', 'SYMC', 'TMUS', 'TSLA', 'TTWO', 'TXN', 'ULTA', 'VOD', 'VRSK', 'VRTX', 'WBA',
#            'WDAY', 'WDC', 'WYNN', 'XLNX', 'XRAY']

cmpList = ['AAPL']

print('Total companies', len(cmpList))

# types = ['income_statements', 'balance_sheets', 'cash_flows']
# years = [2019, 2018, 2017, 2016]

types = ['income_statements']
years = [2019]

writer = pd.ExcelWriter('results/results.xlsx', engine='xlsxwriter')

for cmp in cmpList:
    columns = []
    cmp_df = pd.DataFrame()
    cmp_df['ind'] = np.arange(len(cmp_df))
    cmp_df.set_index("ind", inplace=True)
    for ty in types:
        for yr in years:
            print('Company: ', cmp)
            typedf, valid = getData(cmp, ty, year = yr)
            if valid:
                cmp_df = pd.concat([cmp_df,typedf], axis = 1)
                columns.append(str(ty) + '_' + str(yr))
                columns.append(str(ty) + '_' + str(yr))
    
    cmp_df.columns = columns
    cmp_df.to_excel(writer, sheet_name=cmp, index = False)

writer.save()
writer.close()

