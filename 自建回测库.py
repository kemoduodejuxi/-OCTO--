#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'DongJie'
import datetime
import matplotlib.dates as dates
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class Api(object):
    def __init__(self,balance=1000000,trade_fee = 2,lever = 10):
        self.position =[]
        self.balance_list = []  # 平仓后利润的list,用来制图
        self.account = {"balance_total":balance,"balance_valuable":balance,"balance_frozen":balance}
        # 定义持仓
        self.trade_data = []    # 交易记录
        self.trade_fee = trade_fee  # 双边都收
        self.needle = 0  # 定义推进下标指针
        self.lever = lever # 默认X10，X1为无杠杆比率
        self.trade_time_needle_list = []    # 一个戳
    def trade(self,amount,direction):

        if direction == "open_buy" or direction =="open_sell":
            self.position.append(
                {"datetime":self.quote["datetime"],"symbol": self.symbol, "open_price": self.klines.open[self.needle + 1], "amount": str(amount),
                 "direction": direction})
            self.account["balance_frozen"] = self.account["balance_frozen"]+ 1 # 用1来占位
            self.account["balance_valuable"] = self.account["balance_valuable"] -1 # 同上 #简易demo里面先动total
            self.account["balance_total"] = self.account["balance_total"] - self.trade_fee  # 减去手续费

            self.trade_data.append(self.position[-1])
        else:   # 否则就平仓
            # 同上，资金变动
            self.trade_data.append({"datetime":self.quote["datetime"],"symbol": self.symbol, "close_price": self.klines.open[self.needle + 1], "amount": amount,
                 "direction": direction})
            self.account["balance_total"] = self.account["balance_total"] - self.trade_fee  # 减去手续费
            self.open_price = self.position[-1]["open_price"]
            self.position =[] # 清空仓位，假装的。。。假装只能开一个仓位
            self.trade_time_needle_list.append(self.needle) # close的时候记录时间戳
            if direction == "close_sell":
                # 平空
                self.account["balance_total"] = self.account["balance_total"] +amount*self.lever*(self.open_price-self.klines["open"][self.needle+1])
            else:
                # 平多
                self.account["balance_total"] = self.account["balance_total"] -amount*self.lever*(self.open_price-self.klines["open"][self.needle+1])
            self.balance_list.append(self.account["balance_total"]) # 加入平仓后资金总量

    def cancel (self):
        pass
    def get_data(self,url):
        self.url = url
        self.symbol =url
        csv_file = self.url+".csv"
        csv_data = pd.read_csv(csv_file, low_memory=False)  # 防止弹出警告
        self.klines =pd.DataFrame(csv_data)
        self.klines.columns=(["datetime", "open", "high", "low", "close", "volume", "open_oi", "close_oi"])

        return self.klines    # 用来获得K线数据
    def get_position(self):
        return self.position
        pass    # 用来获得持仓
    def updata(self):
        # 返回一个bool 是否完成
        if self.needle < len(self.klines)-1:

            self.needle = self.needle+1 # 指针加一
            self.quote = self.klines.iloc[self.needle]   #可以调用里面的dateframe
            return False
        else:
            print("回测完成！账户权益："+str(self.account["balance_total"]))
            print(self.trade_data)
            return True
        pass
    def print_plt(self):
        # 该方法用来画出收益图
        if self.trade_data !=[]:
            plt.plot(self.trade_time_needle_list,self.balance_list)
            plt.show()
        else:
            pass