# -*- coding: utf-8 -*-
"""
Created on Tue Mar 29 13:25:24 2022

@author: kjchen
"""


import pandas as pd

import pymysql
from sqlalchemy import create_engine
import datetime

import pythoncom   # These 2 lines are here because COM library 
import subprocess
import gc
import win32com.client
import time

def outlook(receiver,cc,body,subject,file):
    receiver = 'Craig.Hsiao@auo.com;'
    pythoncom.CoInitialize() # is not initialized in the new thread 
    #subprocess.Popen(['C:/Program Files (x86)/Microsoft Office/Office12/OUTLOOK.exe']) #自動開啟OUTLOOK
    subprocess.Popen(['C:\Program Files (x86)\Microsoft Office\Office15\OUTLOOK.EXE'])
        
    #try:
    #outlook = win32com.client.gencache.EnsureDispatch('outlook.application')
    outlook =  win32com.client.Dispatch('Outlook.Application')
    #except:
        #outlook = win32com.client.Dispatch('Outlook.Application')
    mail = outlook.CreateItem(0x0) 
    mail.To = receiver
    mail.CC = cc
    mail.Subject = subject 
    mail.HTMLBody =  body
  
    #mail.Attachments.Add(file)    
    mail.Send()
    time.sleep(10)        #不DELAY可能會來不及完成寄送而關閉不了   
    outlook.Quit()
    del outlook
    gc.collect()  
    print('Email已寄出')
    



# 整合單一mysql
def df2mysql(df0, table):  #讀取失敗將回傳字串'except'
    try:
            #回傳資料庫
        #engine = create_engine("mysql+pymysql://root:ml7ac222@localhost:3306/craig01?charset=utf8".format(DB_USER, DB_PASS, DB_HOST, DB_PORT, DATABASE))
        engine = create_engine("mysql+pymysql://craig945:ml7ac222@10.96.70.126:3306/craig01") 
        #engine = create_engine("mysql+pymysql://{}:{}@{}/{}?charset={}".format('root', 'ml7ac222', 'localhost:3306', 'craig01','utf8mb4'))
        print('create_engine ok')
        #sql = "alter table " + table +" convert to character set utf8mb4 collate utf8mb4_bin; "
        #engine.execute(sql) 
        con = engine.connect()#建立連線
        
        df0.to_sql(table, engine, if_exists='replace', index=False)
       
        print('to_sql ok')
        
        
        #delete = 'DROP TABLE IF EXISTS maint;'
        #engine.execute(delete)                 
        
        #df0.to_sql(table, engine, if_exists='replace',index=False) 
        
        engine.dispose()
        return True                      
    except:
        #return 'except'
        return False
def df2mysql_app(df0, table):  #讀取失敗將回傳字串'except'
    try:
            #回傳資料庫
        #engine = create_engine("mysql+pymysql://root:ml7ac222@localhost:3306/craig01?charset=utf8".format(DB_USER, DB_PASS, DB_HOST, DB_PORT, DATABASE))
        engine = create_engine("mysql+pymysql://craig945:ml7ac222@10.96.70.126:3306/craig01") 
        #engine = create_engine("mysql+pymysql://{}:{}@{}/{}?charset={}".format('root', 'ml7ac222', 'localhost:3306', 'craig01','utf8mb4'))
        print('create_engine ok')
        sql = "alter table " + table +" convert to character set utf8mb4 collate utf8mb4_bin; "
        engine.execute(sql) 
        con = engine.connect()#建立連線
        
        df0.to_sql(table, engine, if_exists='append', index=False)
       
        
        
        
        #delete = 'DROP TABLE IF EXISTS maint;'
        #engine.execute(delete)                 
       
        #df0.to_sql(table, engine, if_exists='replace',index=False) 
        print('to_sql ok')
        engine.dispose()
        return True
    except:
        return False


def mysql2df(table):
    try:
        #conn = pymysql.connect(host='localhost', user='root', password='root', port=3306, db='cncb', charset='utf8mb4')
        conn = pymysql.connect(host='10.96.70.126',user='craig945',password='ml7ac222',db='craig01',port=3306)
        cur = conn.cursor()
        cur.execute("SELECT * FROM "+table)  # 執行查詢語句
        # fetchall()以list的方式回傳所有資料或者是空list(無資料)
        result = cur.fetchall()  # 獲取查詢結果
        col = cur.description  # 獲取查詢結果的欄位描述
        columns=[]
        for i in range(len(col)):
            columns.append(col[i][0])  # 獲取欄位名，列表形式儲存
        df0 = pd.DataFrame(result, columns=columns)
        conn.close()
        return df0
    except:
        return pd.DataFrame()





    
def mysql2df6878(table):
    if 1:
        #conn = pymysql.connect(host='localhost', user='root', password='ml7ac222',db='craig01', port=3306, charset='utf8mb4')
        #conn = pymysql.connect(host='localhost', user='root', password='root', port=3306, db='cncb', charset='utf8mb4')
        conn = pymysql.connect(host='10.96.68.78',user='7ac27ac2',password='7ac27ac2',db='craig01',port=3306)
        cur = conn.cursor()
        cur.execute("SELECT * FROM "+table)  # 執行查詢語句
        # fetchall()以list的方式回傳所有資料或者是空list(無資料)
        result = cur.fetchall()  # 獲取查詢結果
        col = cur.description  # 獲取查詢結果的欄位描述
        columns=[]
        for i in range(len(col)):
            columns.append(col[i][0])  # 獲取欄位名，列表形式儲存
        df0 = pd.DataFrame(result, columns=columns)
        conn.close()
        return df0
    else:
        print("mysql2df_server2 except")
        return pd.DataFrame()



def df2mysql6878(df0, table):  #讀取失敗將回傳字串'except'
    if 1:
            #回傳資料庫
        #engine = create_engine("mysql+pymysql://root:ml7ac222@localhost:3306/craig01?charset=utf8".format(DB_USER, DB_PASS, DB_HOST, DB_PORT, DATABASE))
        engine = create_engine("mysql+pymysql://7ac27ac2:7ac27ac2@10.96.68.78:3306/craig01") 
        #engine = create_engine("mysql+pymysql://{}:{}@{}/{}?charset={}".format('root', 'ml7ac222', 'localhost:3306', 'craig01','utf8mb4'))
        
        #sql = "alter table " + table +" convert to character set utf8mb4 collate utf8mb4_bin; "
        #engine.execute(sql) 
        con = engine.connect()#建立連線
        
        df0.to_sql(table, engine, if_exists='replace', index=False)
       
        
        
        
        #delete = 'DROP TABLE IF EXISTS maint;'
        #engine.execute(delete)                 
        print('create_engine ok')
        #df0.to_sql(table, engine, if_exists='replace',index=False) 
        print('to_sql ok')
        engine.dispose()
                              
    else:
        return 'except'
    
def df2mysql6878_app(df0, table):  #讀取失敗將回傳字串'except'
    if 1:
            #回傳資料庫
        #engine = create_engine("mysql+pymysql://root:ml7ac222@localhost:3306/craig01?charset=utf8".format(DB_USER, DB_PASS, DB_HOST, DB_PORT, DATABASE))
        engine = create_engine("mysql+pymysql://7ac27ac2:7ac27ac2@10.96.68.78:3306/craig01") 
        #engine = create_engine("mysql+pymysql://{}:{}@{}/{}?charset={}".format('root', 'ml7ac222', 'localhost:3306', 'craig01','utf8mb4'))
        
        sql = "alter table " + table +" convert to character set utf8mb4 collate utf8mb4_bin; "
        engine.execute(sql) 
        con = engine.connect()#建立連線
        
        df0.to_sql(table, engine, if_exists='append', index=False)
       
        
        
        
        #delete = 'DROP TABLE IF EXISTS maint;'
        #engine.execute(delete)                 
        print('create_engine ok')
        #df0.to_sql(table, engine, if_exists='replace',index=False) 
        print('to_sql ok')
        engine.dispose()
                              
    else:
        return 'except'

def sql2df6878(sql):
    if 1:
        #conn = pymysql.connect(host='localhost', user='root', password='root', port=3306, db='cncb', charset='utf8mb4')
        conn = pymysql.connect(host='10.96.68.78',user='7ac27ac2',password='7ac27ac2',db='craig01',port=3306)
        cur = conn.cursor()
        cur.execute(sql)  # 執行查詢語句
        # fetchall()以list的方式回傳所有資料或者是空list(無資料)
        result = cur.fetchall()  # 獲取查詢結果
        col = cur.description  # 獲取查詢結果的欄位描述
        columns=[]
        for i in range(len(col)):
            columns.append(col[i][0])  # 獲取欄位名，列表形式儲存
        df0 = pd.DataFrame(result, columns=columns)
        conn.close()
        return df0
    else:
        print("sql except")
        return pd.DataFrame()
    
    
def sql2df(sql):
    try:
        #conn = pymysql.connect(host='localhost', user='root', password='root', port=3306, db='cncb', charset='utf8mb4')
        conn = pymysql.connect(host='10.96.70.126',user='craig945',password='ml7ac222',db='craig01',port=3306)
        cur = conn.cursor()
        cur.execute(sql)  # 執行查詢語句
        # fetchall()以list的方式回傳所有資料或者是空list(無資料)
        result = cur.fetchall()  # 獲取查詢結果
        col = cur.description  # 獲取查詢結果的欄位描述
        columns=[]
        for i in range(len(col)):
            columns.append(col[i][0])  # 獲取欄位名，列表形式儲存
        df0 = pd.DataFrame(result, columns=columns)
        conn.close()
        return df0
    except:
        print("sql except")
        return pd.DataFrame()

def dates2list(date1, date2, isDT= False):
    if "-" in date1:
        date_mode = "%Y-%m-%d"
    elif "/" in date1:
        date_mode = "%Y/%m/%d"
    else:
        date_mode = "%Y%m%d"
    start = datetime.datetime.strptime(date1, date_mode)
    end = datetime.datetime.strptime(date2, date_mode)
    dates = [start + datetime.timedelta(days=x) for x in range(0, (end-start).days+1)]
    if not isDT:
        for i in range(len(dates)):
            dates[i] = dates[i].strftime(date_mode)
    return dates


def df2mysql70126(df0, table):  #讀取失敗將回傳字串'except'
    if 1:
            #回傳資料庫
        #engine = create_engine("mysql+pymysql://root:ml7ac222@localhost:3306/craig01?charset=utf8".format(DB_USER, DB_PASS, DB_HOST, DB_PORT, DATABASE))
        engine = create_engine("mysql+pymysql://craig945:ml7ac222@10.96.70.126:3306/craig01") 
        #engine = create_engine("mysql+pymysql://{}:{}@{}/{}?charset={}".format('root', 'ml7ac222', 'localhost:3306', 'craig01','utf8mb4'))
        
        #sql = "alter table " + table +" convert to character set utf8mb4 collate utf8mb4_bin; "
        #engine.execute(sql) 
        con = engine.connect()#建立連線
        
        df0.to_sql(table, engine, if_exists='replace', index=False)
       
        
        
        
        #delete = 'DROP TABLE IF EXISTS maint;'
        #engine.execute(delete)                 
        print('create_engine ok')
        #df0.to_sql(table, engine, if_exists='replace',index=False) 
        print('to_sql ok')
        engine.dispose()
                              
    else:
        return 'except'
    
def df2mysql70126_app(df0, table):  #讀取失敗將回傳字串'except'
    if 1:
            #回傳資料庫
        #engine = create_engine("mysql+pymysql://root:ml7ac222@localhost:3306/craig01?charset=utf8".format(DB_USER, DB_PASS, DB_HOST, DB_PORT, DATABASE))
        engine = create_engine("mysql+pymysql://craig945:ml7ac222@10.96.70.126:3306/craig01") 
        #engine = create_engine("mysql+pymysql://{}:{}@{}/{}?charset={}".format('root', 'ml7ac222', 'localhost:3306', 'craig01','utf8mb4'))
        
        sql = "alter table " + table +" convert to character set utf8mb4 collate utf8mb4_bin; "
        engine.execute(sql) 
        con = engine.connect()#建立連線
        
        df0.to_sql(table, engine, if_exists='append', index=False)
       
        
        
        
        #delete = 'DROP TABLE IF EXISTS maint;'
        #engine.execute(delete)                 
        print('create_engine ok')
        #df0.to_sql(table, engine, if_exists='replace',index=False) 
        print('to_sql ok')
        engine.dispose()
                              
    else:
        return 'except'


def mysql2df70126(table):
    try:
        #conn = pymysql.connect(host='localhost', user='root', password='root', port=3306, db='cncb', charset='utf8mb4')
        conn = pymysql.connect(host='10.96.70.126',user='craig945',password='ml7ac222',db='craig01',port=3306)
        cur = conn.cursor()
        cur.execute("SELECT * FROM "+table)  # 執行查詢語句
        # fetchall()以list的方式回傳所有資料或者是空list(無資料)
        result = cur.fetchall()  # 獲取查詢結果
        col = cur.description  # 獲取查詢結果的欄位描述
        columns=[]
        for i in range(len(col)):
            columns.append(col[i][0])  # 獲取欄位名，列表形式儲存
        df0 = pd.DataFrame(result, columns=columns)
        conn.close()
        return df0
    except:
        return 'except'


def df2html(df, index_name = 'Index', isIdx=True):
    if df is None or len(df) == 0:
        return ''
    alarmBody = r""
    
    
    alarmBody += '<table border="1" style=“word-wrap:break-word;”><tr>'
    if isIdx:
        alarmBody += "<th bgcolor='#E1C4C4'>"+ index_name + "</th>"
        
        #;
    for col in df.columns:
        alarmBody += "<th bgcolor='#E1C4C4'>" + str(col) + "</th>"
    alarmBody += '</tr>'
    
    for idx in df.index:
        alarmBody += '<tr>'
        if isIdx:
            alarmBody += "<td bgcolor='#FFFFF4'>" + str(idx) + "</td>"
        for col in df.columns:
            alarmBody += "<td bgcolor='#FFFFF4'>" + str(df.loc[idx][col]) + "</td>"
        alarmBody += '</tr>'
    alarmBody += '</table></br></br>'
    return alarmBody



"""
def mysql2df(table):
    try:
        print('mysql下載中')
        conn = pymysql.connect(host='localhost',user='craig945',password='ml7ac222',db='craig01',port=3306)
        print('Conn ok')
        cur = conn.cursor()
        cur.execute("SELECT * FROM "+table)  # 執行查詢語句
        # fetchall()以list的方式回傳所有資料或者是空list(無資料)
        print('Cur ok')
        result = cur.fetchall()  # 獲取查詢結果
        col = cur.description  # 獲取查詢結果的欄位描述
        columns=[]
        for i in range(len(col)):
            columns.append(col[i][0])  # 獲取欄位名，列表形式儲存
        df0 = pd.DataFrame(result, columns=columns)
        conn.close()
        return df0
    except:
        print('mysql2df -> '+table+'  發生except')
        return 'except'




def df2mysql(df0, table):
    try:
            # pdData.index[pdData['Machine'] == 'CCCGL400'].tolist()[0]
            #回傳資料庫
        engine = create_engine("mysql+pymysql://craig945:ml7ac222@localhost:3306/craig01") 
        #delete = 'DROP TABLE IF EXISTS maint;'
        #engine.execute(delete)                 
        print('create_engine ok')
        df0.to_sql(table, engine, if_exists='replace',index=False) 
        print('to_sql ok')
        engine.dispose()
        return True
                              
    except:
        print('df2mysql -> '+table+'  發生except')
        logging.info('df2mysql -> '+table+'  發生except')
        return False


def df2mysql_append(df0, table):
    if 1:
            # pdData.index[pdData['Machine'] == 'CCCGL400'].tolist()[0]
            #回傳資料庫
        engine = create_engine("mysql+pymysql://craig945:ml7ac222@localhost:3306/craig01") 
        #delete = 'DROP TABLE IF EXISTS maint;'
        #engine.execute(delete)                 
        print('create_engine ok')
        df0.to_sql(table, engine, if_exists='append',index=False) 
        print('to_sql ok')
        engine.dispose()
        return True
                              
    else:
        print('df2mysql -> '+table+'  發生except')
        logging.info('df2mysql -> '+table+'  發生except')
        return 'except'
        return False
    

def ora2df(sql):
    pd.set_option('display.max_columns',None)
    #os.environ['path'] = r'D:\Craig\oracle\instantclient_11_2'+";"+os.environ['path']
    #dsn_tns = cx_Oracle.makedsn('tcpp201', '1521', service_name='L7AH')
    dsn_tns = cx_Oracle.makedsn('l7app154', '1553', service_name='L7AHSHA_NEW')
    conn = cx_Oracle.connect(user='L7AINT_AP', password='L7AINT$AP', dsn=dsn_tns)
    cursor = conn.cursor()
    cursor.execute(sql)
    print('yes')
    df_data = pd.DataFrame(cursor.fetchall())
    
    new_cols = [i[0] for i in cursor.description]
    old_cols = df_data.columns
    df_data.rename(columns=dict(zip(old_cols, new_cols)),inplace=True)
    return df_data








"""





#table = "openpo"
#table = "ct1_meanv"
#df0 = mysql2df_server2(table)
#print(df0)