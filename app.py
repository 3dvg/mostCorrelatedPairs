from bs4 import BeautifulSoup
import requests
import sqlite3
import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt

def get_tickers(n): 
  resp = requests.get('https://www.slickcharts.com/sp500')
  soup = BeautifulSoup(resp.text, 'lxml')
  data = soup.find('table')
  tickers = list()
  for row in data.findAll('tr')[1:]:
      ticker = row.findAll('td')[2].text
      if ticker != 'BRK.B' and ticker != 'BF.B':
        tickers.append(ticker)
  return tickers[:n]

def compile_dfs(db, stocks, start_date, end_date):
  conn = sqlite3.connect(db) 
  dfs = pd.DataFrame()
  for stock in stocks:
    query="SELECT * FROM '{}' WHERE Date BETWEEN '{}' AND '{}'".format(stock,start_date,end_date)
    df = pd.read_sql_query(query, con=conn) 
    df.set_index('Date', inplace=True)
    df = df[['Close']] 
    df.rename(columns={'Close': stock}, inplace=True)
    dfs = dfs.join(df, how='outer')
  conn.close()
  return dfs

def correlated_df(stocks, start_date, end_date):
  df = compile_dfs(DB_NAME,stocks, start_date, end_date)
  df_corr = df.pct_change().corr()
  corr = {}
  for s in stocks:
    stock_corr = dict()
    for idx in df_corr[s].index:
      if idx != s:
        stock_corr[df_corr[s][idx]] = '{}-{}'.format(s,idx)
    max_keys = max(stock_corr.keys()) 
    corr[max_keys]= stock_corr[max_keys]

#   Ucomment the next 4 lines to see the dict in the terminal  
#   print("{")
#   for idx,val in corr.items():
#       print ("'{}':'{}'".format(idx, val))
#   print("}")
  return corr 

def visualize(d):
  data_y = sorted(d.keys())
  data_x = [d[i] for i in data_y]
  fig, ax = plt.subplots()
  plt.title('Most Correlated Pairs of the Top 100 S&P500 Components (2019 - 2020)')
  ax.tick_params(axis = 'both', which = 'major', labelsize = 10)
  plt.xticks(rotation=90)
  ax.scatter(data_x, data_y, c=data_y,cmap='RdYlGn',vmin='-1', vmax='1')
  ax.set_ylabel('Correlation')
  ax.set_xlabel('Pairs')
  plt.grid(color='#C0C0C0', linestyle='--', linewidth=0.5)
  plt.tight_layout()
  plt.show()

if __name__ == "__main__":
  DB_NAME = "stocks_data.db"
  stocks = get_tickers(100)
  start_date = '2019-01-01 00:00:00'
  end_date = '2020-01-01 00:00:00'
  corrPairs_data = correlated_df(stocks, start_date, end_date)
  visualize(corrPairs_data)