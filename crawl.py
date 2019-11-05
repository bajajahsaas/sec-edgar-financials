import json
import pandas as pd
from edgar.financials import FinancialReportEncoder
from edgar.stock import Stock


def getData(ticket, type, period='annual', year=0, quarter=0):
    # period = 'annual' # or 'quarterly', which is the default
    # year = 2018 # can use default of 0 to get the latest
    # quarter = 1 # 1, 2, 3, 4, or default value of 0 to get the latest

    stock = Stock(ticket)
    filing = stock.get_filing(period, year, quarter)

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
    map_data = pd.Series(map_keys)
    return sec_data, map_data


final_df = pd.DataFrame()
cmpList = ['AAL', 'AAPL', 'ADBE', 'ADI', 'ADP', 'ADSK', 'ALGN', 'ALXN', 'AMAT', 'AMGN', 'AMZN', 'ASML', 'ATVI', 'AVGO',
           'BIDU', 'BIIB', 'BKNG', 'BMRN', 'CA', 'CDNS', 'CELG', 'CERN', 'CHKP', 'CHTR', 'CMCSA', 'COST', 'CSCO', 'CSX',
           'CTAS', 'CTRP', 'CTSH', 'CTXS', 'DISH', 'DLTR', 'EA', 'EBAY', 'ESRX', 'EXPE', 'FAST', 'FB', 'FISV', 'FOX',
           'FOXA', 'GILD', 'GOOG', 'HAS', 'HOLX', 'HSIC', 'IDXX', 'ILMN', 'INCY', 'INTC', 'INTU', 'ISRG', 'JBHT', 'JD',
           'KHC', 'KLAC', 'LBTYA', 'LBTYK', 'LRCX', 'MAR', 'MCHP', 'MDLZ', 'MELI', 'MNST', 'MSFT', 'MU', 'MXIM', 'MYL',
           'NFLX', 'NTES', 'NVDA', 'ORLY', 'PAYX', 'PCAR', 'PYPL', 'QCOM', 'QRTEA', 'REGN', 'ROST', 'SBUX', 'SHPG',
           'SIRI', 'SNPS', 'STX', 'SWKS', 'SYMC', 'TMUS', 'TSLA', 'TTWO', 'TXN', 'ULTA', 'VOD', 'VRSK', 'VRTX', 'WBA',
           'WDAY', 'WDC', 'WYNN', 'XLNX', 'XRAY']

cmpList = ['AAL', 'AAPL', 'ADBE']

print('Total companies', len(cmpList))

types = ['income_statements', 'balance_sheets', 'cash_flows']
for type in types:
    writer = pd.ExcelWriter('results/results_' + type + '.xlsx', engine='xlsxwriter')
    writer_cols = pd.ExcelWriter('results/columns_' + type + '.xlsx', engine='xlsxwriter')
    column_size = []
    for cmp in cmpList:
        cmp_df, map_df = getData(cmp, type)
        cmp_df.to_excel(writer, sheet_name=cmp, index=False)
        map_df.to_excel(writer_cols, sheet_name=cmp, index=False, header=False)
        column_size.append((cmp, cmp_df.shape[1]))

    writer.save()
    writer.close()
    writer_cols.save()
    writer_cols.close()

    print('Column Size',type, column_size)
