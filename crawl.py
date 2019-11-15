import json
import numpy as np
import pandas as pd
from edgar.financials import FinancialReportEncoder
from edgar.stock import Stock
'''
https://www.pingshiuanchua.com/blog/post/intro-to-colaboratory-and-linking-it-to-google-sheets
https://www.pingshiuanchua.com/blog/post/overpower-your-google-sheets-with-python

'''

def getData(ticket, type, period='annual', year=20188, quarter=0):
    # period = 'annual' # or 'quarterly', which is the default
    # year = 2018 # can use default of 0 to get the latest
    # quarter = 1 # 1, 2, 3, 4, or default value of 0 to get the latest

    stock = Stock(ticket)
    try:
        filing = stock.get_filing(period, year, quarter)
    except:
        print('Invalid input')
        return None, False

    # financial reports (contain data for multiple years)
    if type == 'income_statements':
        statements = filing.get_income_statements()
    elif type == "balance_sheets":
        statements = filing.get_balance_sheets()
    elif type == "cash_flows":
        statements = filing.get_cash_flows()

    jsonstr = FinancialReportEncoder().encode(statements)
    data = json.loads(jsonstr)

    # print(data.keys())  # dict_keys(['company', 'date_filed', 'reports'])

    listreports = data['reports']

    columns = []
    data = []

    map_keys = []

    for report in listreports:
        # print(report.keys())  # dict_keys(['date', 'months', 'map']): string, int, dict

        for report_key in report.keys():
            if report_key == 'map':
                for map_key in report['map'].keys():
                    map_keys.append(map_key)
                    # print(map_key, report['map'][map_key].keys())  # dict_keys(['label', 'value'])
                    for key in report['map'][map_key].keys():
                        # print(key, report['map'][map_key][key])
                        if key == 'label':
                            columns.append(report['map'][map_key][key])
                        else:
                            data.append(report['map'][map_key][key])

    sec_data = pd.DataFrame([data], columns=columns)
    sec_data = sec_data.append(pd.Series(), ignore_index=True)
    sec_data = sec_data.transpose()

    map_data = pd.Series(map_keys)
    return sec_data, True


final_df = pd.DataFrame()
cmpList = ['AAL', 'AAPL', 'ADBE', 'ADI', 'ADP', 'ADSK', 'ALGN', 'ALXN', 'AMAT', 'AMGN', 'AMZN', 'ASML', 'ATVI', 'AVGO',
           'BIDU', 'BIIB', 'BKNG', 'BMRN', 'CA', 'CDNS', 'CELG', 'CERN', 'CHKP', 'CHTR', 'CMCSA', 'COST', 'CSCO', 'CSX',
           'CTAS', 'CTRP', 'CTSH', 'CTXS', 'DISH', 'DLTR', 'EA', 'EBAY', 'ESRX', 'EXPE', 'FAST', 'FB', 'FISV', 'FOX',
           'FOXA', 'GILD', 'GOOG', 'HAS', 'HOLX', 'HSIC', 'IDXX', 'ILMN', 'INCY', 'INTC', 'INTU', 'ISRG', 'JBHT', 'JD',
           'KHC', 'KLAC', 'LBTYA', 'LBTYK', 'LRCX', 'MAR', 'MCHP', 'MDLZ', 'MELI', 'MNST', 'MSFT', 'MU', 'MXIM', 'MYL',
           'NFLX', 'NTES', 'NVDA', 'ORLY', 'PAYX', 'PCAR', 'PYPL', 'QCOM', 'QRTEA', 'REGN', 'ROST', 'SBUX', 'SHPG',
           'SIRI', 'SNPS', 'STX', 'SWKS', 'SYMC', 'TMUS', 'TSLA', 'TTWO', 'TXN', 'ULTA', 'VOD', 'VRSK', 'VRTX', 'WBA',
           'WDAY', 'WDC', 'WYNN', 'XLNX', 'XRAY']

cmpList = ['AAL']

print('Total companies', len(cmpList))

types = ['income_statements', 'balance_sheets', 'cash_flows']
years = [2019, 2018, 2017, 2016]

for cmp in cmpList:
    cmp_df = pd.DataFrame()
    cmp_df['ind'] = np.arange(len(cmp_df))
    cmp_df.set_index("ind", inplace=True)
    for type in types:
        writer = pd.ExcelWriter('results/results.xlsx', engine='xlsxwriter')
        for yr in years:
            typedf, valid = getData(cmp, type, year = yr)
            if valid:
                typedf['ind'] = np.arange(len(typedf))
                typedf.set_index("ind", inplace=True)
                print('concat', cmp_df.shape, typedf.shape)
                # cmp_df = pd.concat([cmp_df,typedf], ignore_index=True, axis = 1)
                cmp_df.merge(typedf, how="outer", left_index=True, right_index=True)
                print('concat done', cmp_df.shape)
    cmp_df.to_excel(writer, sheet_name=cmp)
    writer.save()
    writer.close()
