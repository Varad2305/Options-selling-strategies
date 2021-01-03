from flask import Flask,jsonify
from flask_restful import Resource, Api
from flask_cors import CORS
import pandas as pd
import numpy as np
from datetime import date,time,timedelta
from nsepy import get_history
import copy

app = Flask(__name__)
CORS(app)
api = Api(app)

def process():
    end_date = date.today().strftime("%d-%m-%Y")

    data = pd.read_csv("CF-Insider-Trading-equities-30-09-2020-to-30-12-2020.csv")

    new_columns = []

    for col in data.columns:
        new_columns.append(col.split(" \n")[0])

    data.columns = new_columns
    data = data[data["CATEGORY OF PERSON"].isin(["Promoters", "Promoter Group"])]
    data_last_txn = copy.deepcopy(data)
    data_promoter_sell = data[data["MODE OF ACQUISITION"] == "Market Sale"]
    data = data[data["MODE OF ACQUISITION"] == "Market Purchase"]

    data = data[["SYMBOL", "VALUE OF SECURITY (ACQUIRED/DISPLOSED)", "NO. OF SECURITIES (ACQUIRED/DISPLOSED)"]]
    data_promoter_sell = data_promoter_sell[["SYMBOL", "VALUE OF SECURITY (ACQUIRED/DISPLOSED)", "NO. OF SECURITIES (ACQUIRED/DISPLOSED)"]]
    data_last_txn = data_last_txn[["SYMBOL", "NAME OF THE ACQUIRER/DISPOSER", "VALUE OF SECURITY (ACQUIRED/DISPLOSED)", 
                                                     "NO. OF SECURITIES (ACQUIRED/DISPLOSED)", "MODE OF ACQUISITION",
                                                    "DATE OF ALLOTMENT/ACQUISITION TO"]]

    data_last_txn["DATE OF ALLOTMENT/ACQUISITION TO"].iloc[0]

    ser1 = data["VALUE OF SECURITY (ACQUIRED/DISPLOSED)"].astype("float")
    ser2 = data["NO. OF SECURITIES (ACQUIRED/DISPLOSED)"].astype("float")

    ser3 = data_promoter_sell["VALUE OF SECURITY (ACQUIRED/DISPLOSED)"].astype("float")
    ser4 = data_promoter_sell["NO. OF SECURITIES (ACQUIRED/DISPLOSED)"].astype("float")

    ser5 = data_last_txn["VALUE OF SECURITY (ACQUIRED/DISPLOSED)"].astype("float")
    ser6 = data_last_txn["NO. OF SECURITIES (ACQUIRED/DISPLOSED)"].astype("float")
    ser7 = pd.to_datetime(pd.Series(data_last_txn["DATE OF ALLOTMENT/ACQUISITION TO"]), format="%d-%b-%Y")


    data["VALUE OF SECURITY (ACQUIRED/DISPLOSED)"] = ser1
    data["NO. OF SECURITIES (ACQUIRED/DISPLOSED)"] = ser2

    data_promoter_sell["VALUE OF SECURITY (ACQUIRED/DISPLOSED)"] = ser3
    data_promoter_sell["NO. OF SECURITIES (ACQUIRED/DISPLOSED)"] = ser4

    data_last_txn["VALUE OF SECURITY (ACQUIRED/DISPLOSED)"] = ser5
    data_last_txn["NO. OF SECURITIES (ACQUIRED/DISPLOSED)"] = ser6
    data_last_txn["DATE OF ALLOTMENT/ACQUISITION TO"] = ser7

    data = data.groupby('SYMBOL')[['VALUE OF SECURITY (ACQUIRED/DISPLOSED)','NO. OF SECURITIES (ACQUIRED/DISPLOSED)']].sum().reset_index()
    data_promoter_sell = data_promoter_sell.groupby('SYMBOL')[['VALUE OF SECURITY (ACQUIRED/DISPLOSED)','NO. OF SECURITIES (ACQUIRED/DISPLOSED)']].sum().reset_index()
    data.sort_values(by = "VALUE OF SECURITY (ACQUIRED/DISPLOSED)", ascending=False, inplace = True)

    data_promoter_sell.sort_values(by = "VALUE OF SECURITY (ACQUIRED/DISPLOSED)", ascending=False, inplace = True)

    data.rename(columns = {"VALUE OF SECURITY (ACQUIRED/DISPLOSED)" : "Net Acquired Value", "NO. OF SECURITIES (ACQUIRED/DISPLOSED)": "Net Acquired Qty"}, inplace=True)

    data_promoter_sell.rename(columns = {"VALUE OF SECURITY (ACQUIRED/DISPLOSED)" : "Net Disposed Value", "NO. OF SECURITIES (ACQUIRED/DISPLOSED)": "Net Disposed Qty"}, inplace = True)

    merged_data = pd.merge(data,data_promoter_sell, how = "left").fillna(0)

    merged_data["Net Value Acquired"] = merged_data["Net Acquired Value"] - merged_data["Net Disposed Value"]

    merged_data["Net Qty Acquired"] = merged_data["Net Acquired Qty"] - merged_data["Net Disposed Qty"]

    merged_data.sort_values(by = "Net Value Acquired", ascending = False, inplace = True)

    merged_data["Avg buy price"] = round(merged_data["Net Value Acquired"]/merged_data["Net Qty Acquired"],2)

    merged_data = merged_data[["SYMBOL", "Net Value Acquired", "Net Qty Acquired", "Avg buy price"]]

    merged_data = merged_data[merged_data["Net Value Acquired"] >= 10000000]


    ltp = []
    i = 0
    for sym in merged_data["SYMBOL"]:
        try:
            ltp.append(get_history(sym,date.today() - timedelta(5), date.today())["Close"][-1:][0])
        except:
            print("ERROR FOR ", sym)
            ltp.append(0)
        print(i, sym)
        i+=1


    merged_data["LTP"] = ltp

    merged_data["% diff"] = round((merged_data["LTP"] - merged_data["Avg buy price"])/merged_data["Avg buy price"],2)

    merged_data = merged_data[merged_data["LTP"]!=0]


    merged_data.sort_values(by = ["% diff", "Net Value Acquired"], ascending=[True, False], inplace = True)


    merged_data.sort_values(by = "Net Value Acquired", ascending=False)[:25]


    txns = {}
    for i in range(len(merged_data)):
        sym = merged_data.iloc[i]["SYMBOL"]
        curr_txns = data_last_txn[data_last_txn["SYMBOL"] == sym]
        txns[sym] = curr_txns
        txns[sym]["Avg. txn price"] = round(txns[sym]["VALUE OF SECURITY (ACQUIRED/DISPLOSED)"]/txns[sym]["NO. OF SECURITIES (ACQUIRED/DISPLOSED)"],2)



    merged_data[merged_data["% diff"] <= 0.05].sort_values(by = "Net Value Acquired", ascending=False)
    return merged_data,txns

df = pd.DataFrame()
txns = {}

class SendList(Resource):
    def get(self):
        global df
        global txns
        df,txns = process()
        
        ret_json = {'data' : []}

        for _,row in df.iterrows():
            ret_json['data'].append(list(row))

        return jsonify(ret_json)

class SendTxns(Resource):
    def get(self,symbol):
        global txns
        ret_json = {'txns' : []}
        df = txns[symbol]
        for _,row in df.iterrows():
            ret_json['txns'].append(list(row))
        
        return jsonify(ret_json)

api.add_resource(SendList, '/sendList/')
api.add_resource(SendTxns, '/sendTxns/<string:symbol>')

if __name__ == '__main__':
    app.run(debug=True)