# -*- coding: utf-8 -*-
"""
"""
import pythoncom   # These 2 lines are here because COM library 
import subprocess
import gc
import win32com.client
from flask import Flask, render_template, request, redirect,flash
from flask import send_file, send_from_directory, jsonify
from flask import app
from flask import url_for
from flask import flash
import logging
from web_func01 import *
from hr import *
from laser_func import *
import oct_func as octf 
from mysql_to_df import *
#logging.info("紀錄時間:"+datetime.now().strftime("%Y-%m-%d %H:%M:%S") +",耗時:"+str(int(etime-stime))+"s")
", "", "

import time as tt
import pandas as pd
import datetime
import pymysql
from sqlalchemy import create_engine
import cx_Oracle
import os
import matplotlib.pyplot as plt


# AUOFab_PathList所需
import requests as req00
from lxml import html

app = Flask(__name__)
app.config["DEBUG"] = True
os.environ['path'] = r'D:\Craig\oracle\instantclient_11_2'+";"+os.environ['path']
    

def req2(server_path, proxies):
    #proxies = {'http':"http://10.97.4.1:8080",}
    headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9", 
    "Accept-Encoding": "gzip, deflate, br", 
    "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7", 
    "Host": "httpbin.org", 
    "Referer": "https://www.learncodewithmike.com/", 
    "Sec-Fetch-Dest": "document", 
    "Sec-Fetch-Mode": "navigate", 
    "Sec-Fetch-Site": "none", 
    "Upgrade-Insecure-Requests": "1", 
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36", 
    "X-Amzn-Trace-Id": "Root=1-619b0999-5f188bbe16f610746495b8f4"
    }
    s = req00.session()
    s.keep_alive = False
    try:
        httpRequest = s.get(server_path, proxies=proxies, headers=headers)
    except:
        print('爬蟲錯誤, '+server_path)
        logging.info('爬蟲錯誤, '+server_path)
        return ""
        
        
    return httpRequest
# Fab網域路徑 之path list
def AUOFab_PathList(web0):
    proxies = {'http':'http://10.97.4.1:8080'}
    #web0 = 'http://tcweb002.corpnet.auo.com/CCCGL1082/AOI%20Data/Defect_Image/sub1/'
    t0 = time.time()
    print('reuest中...   ', web0[25:], end='   ')
    req = req2(web0, proxies=proxies)
    print('ok!!')
    t1 = time.time()
    print('req time:',t1-t0)
    logging.info('req time: '+str(t1-t0))
    webpage = html.fromstring(req.content)
    t2 = time.time()
    print('html.fromstring : ',t2-t1)
    pathList = webpage.xpath('//a/@href')[1:]
    t3 = time.time()
    folder_list = []
    for fld in pathList:
        # 取[:-1]為去掉尾巴的'/' , 而[1]為取list的第二項(資料夾名稱)
        if fld[-1] == '/':
            folder_list.append(os.path.split(fld[:-1])[1])
        else:
            folder_list.append(os.path.split(fld)[1])
    #print(os.path.split(i[:-1]))
    return [pathList, folder_list]


print(101+int(time.strftime("%W")))
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
        logging.info('mysql2df -> '+table+'  發生except')
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
                              
    except:
        print('df2mysql -> '+table+'  發生except')
        logging.info('df2mysql -> '+table+'  發生except')
        return 'except'


def df2mysql_app(df0, table):
    try:
        # pdData.index[pdData['Machine'] == 'CCCGL400'].tolist()[0]

        #回傳資料庫
        engine = create_engine("mysql+pymysql://craig945:ml7ac222@localhost:3306/craig01") 
        #delete = 'DROP TABLE IF EXISTS maint;'
        #engine.execute(delete)                 
        print('create_engine ok')
        df0.to_sql(table, engine, if_exists='append',index=False) 
        print('to_sql ok')
        engine.dispose()
                              
    except:
        print('df2mysql -> '+table+'  發生except')
        logging.info('df2mysql -> '+table+'  發生except')
        return 'except'




def ora2df(sql):
    pd.set_option('display.max_columns',None)
    #os.environ['path'] = r'D:\Craig\oracle\instantclient_11_2'+";"+os.environ['path']
    #dsn_tns = cx_Oracle.makedsn('tcpp201', '1521', service_name='L7AH')
    dsn_tns = cx_Oracle.makedsn('l7app154', '1553', service_name='L7AHSHA_NEW')
    conn = cx_Oracle.connect(user='L7AINT_AP', password='L7AINT$AP', dsn=dsn_tns)
    
    
    #os.environ['path'] = r'D:\Craig\oracle\instantclient_11_2'+";"+os.environ['path']
    #dsn_tns = cx_Oracle.makedsn('tcpp103', '1521', 'L7BH')
    #conn = cx_Oracle.connect(user='L7BARYENG_AP', password='L7BARYENG$AP', dsn=dsn_tns)
    today0 = datetime.date.today().strftime("%Y%m%d")
    today = today0[0:4]+'/'+today0[4:6]+'/'+today0[6:8]
    # 修正版oracle 與法
    #Product_code = 'T430HVN01'
    #TOOL_ID = 'CCCGL508'
    cursor = conn.cursor()
    cursor.execute(sql)
    print('yes')
    df_data = pd.DataFrame(cursor.fetchall())
    
    new_cols = [i[0] for i in cursor.description]
    old_cols = df_data.columns

    df_data.rename(columns=dict(zip(old_cols, new_cols)),inplace=True)
    return df_data




    """
    mysql = "select t.mfg_day, t.model_no, t.test_user,count(*)as TOT"
    mysql = mysql + ",round(100*sum(decode(t.grade,'G',1,0))/count(*),1) as GO_Ratio"
    mysql = mysql + ",round(100*sum(decode(t.defect_code_desc,'OTHER ALIGN DEFECT',1,0))/count(*),1) as OAD"
    mysql = mysql + ",round(100*sum(decode(t.defect_code_desc,'OTHER APPEAR DEFECT',1,0))/count(*),1) as OPAD" #原O_A_D
    mysql = mysql + ",round(100*sum(decode(t.defect_code_desc,'OTHER GLASS DEFECT',1,0))/count(*),1) as OGD"
    mysql = mysql + ",round(100*sum(decode(t.defect_code_desc,'OTHER LINE DEFECT ',1,0))/count(*),1) as OLD" #原O_L_D
    mysql = mysql + ",round(100*sum(decode(t.defect_code_desc,'BP',1,0))/count(*),1) as BP"
    mysql = mysql + ",round(100*sum(decode(t.defect_code_desc,'V-OPEN-BL',1,0))/count(*),1) as V_OPEN_BL"
    mysql = mysql + ",round(100*sum(decode(t.defect_code_desc,'V-OPEN',1,0))/count(*),1) as V_OPEN"
    mysql = mysql + ",round(100*sum(decode(t.defect_code_desc,'V-LINE',1,0))/count(*),1) as V_LINE"
    mysql = mysql + ",round(100*sum(decode(t.defect_code_desc,'H-OPEN',1,0))/count(*),1) as H_OPEN"
    mysql = mysql + ",round(100*sum(decode(t.defect_code_desc,'H-LINE',1,0))/count(*),1) as H_LINE"
    mysql = mysql + ",round(100*sum(decode(t.defect_code_desc,'X-SHORT',1,0))/count(*),1) as X_SHORT"
    mysql = mysql + ",round(100*sum(decode(t.defect_type,'LINE DEFECT',1,0))/count(*),1) as LINE"
    mysql = mysql + ",round(100*sum(decode(t.defect_code_desc,'WHITE SPOT',1,0))/count(*),1) as WHITE_SPOT"
    mysql = mysql + ",round(100*sum(decode(t.defect_code_desc,'BLACK SPOT',1,0))/count(*),1) as BLACK_SPOT"
    mysql = mysql + ",round(100*sum(decode(t.defect_code_desc,'WHITE MURA',1,0))/count(*),1) as WHITE_MURA"
    mysql = mysql + ",round(100*sum(decode(t.defect_code_desc,'BLACK MURA',1,0))/count(*),1) as BLACK_MURA"
    mysql = mysql + ",round(100*sum(decode(t.defect_code_desc,'AROUND GAP MURA',1,0))/count(*),1) as AGM"
    mysql = mysql + ",round(100*sum(decode(t.defect_code_desc,'ABNORMAL DISPLAY',1,0))/count(*),1) as A_D"
    mysql = mysql + ",round(100*sum(decode(t.defect_code_desc,'DP',decode(t.grade,'W',1,0),0))/count(*),1) as DP_W"
    mysql = mysql + ",round(100*sum(decode(t.defect_code_desc,'DP-PAIR',decode(t.grade,'W',1,0),0))/count(*),1) as DPP_W"
    mysql = mysql + ",round(100*sum(decode(t.defect_code_desc,'DP-CLUSTER',1,0))/count(*),1) as DP_CLUSTER"
    mysql = mysql + ",round(100*sum(decode(t.defect_code_desc,'OTHER TFT DEFECT',1,0))/count(*),1) as OTD"
    mysql = mysql + ",round(100*sum(decode(t.defect_code_desc,'3DP-ADJ',1,0))/count(*),1) as DP_ADJ"
    mysql = mysql + ",round(100*sum(decode(t.defect_code_desc,'POINT-COUNT',1,0))/count(*),1) as POINT_COUNT"
    mysql = mysql + ",round(100*sum(decode(t.defect_code_desc,'DP-NEAR',1,0))/count(*),1) as DP_NEAR"
    mysql = mysql + ",round(100*sum(decode(t.defect_code_desc,'H-BAND MURA',1,0))/count(*),1) as H_BAND_MURA"
    mysql = mysql + ",round(100*sum(decode(t.defect_code_desc,'3BP-ADJ',decode(t.grade,'W',1,0),0))/count(*),1) as BP_ADJ"
    mysql = mysql + ",round(100*sum(decode(t.defect_code_desc,'3BP-DP-ADJ',decode(t.grade,'W',1,0),0))/count(*),1) as BP_DP_ADJ"
    mysql = mysql + ",round(100*sum(decode(t.defect_code_desc,'BP-CLUSTER',decode(t.grade,'W',1,0),0))/count(*),1) as BP_CLUSTER"
    mysql = mysql + ",round(100*sum(decode(t.defect_code_desc,'BP-DP-PAIR',1,0))/count(*),1) as BPDP"
    mysql = mysql + ",round(100*sum(decode(t.defect_code_desc,'POINT-CLUSTER',1,0))/count(*),1) as POINT_CLUSTER"
    mysql = mysql + ",round(100*sum(decode(t.defect_code_desc,'LC TWIST NG',1,0))/count(*),1) as LC_TWIST_NG"
    mysql = mysql + ",round(100*sum(decode(t.defect_code_desc,'NIKON MASK MURA',1,0))/count(*),1) as NMM"
    #mysql = mysql + ",'" + Start_Day + "' as Start_Day,'" + End_Day + "' as End_Day "
    mysql = mysql + " from celods.h_dax_fbk_test_ods t where t.op_id='CGL' "
    mysql = mysql + " and t.mfg_day between to_date('" + Start_Day + "','yyyy/mm/dd') and to_date('" + End_Day + "','yyyy/mm/dd')"
    mysql = mysql + " group by (t.mfg_day, t.model_no, t.test_user) order by t.test_user"
    """

def ct1Summ2(user,name, auth, shift, date1, date2):
    
    sectShow = 'ct1Summ2'
    
    today0 = datetime.date.today().strftime("%Y%m%d")
    today = today0[0:4]+'-'+today0[4:6]+'-'+today0[6:8]
    now = datetime.datetime.now().strftime("%Y%m%d%H%M")
    # 下載保養資料
    table = 'maint'
    maint_list = mysql2df(table)
    if type(maint_list) == 'str':
        return '<h1>讀取資料庫MAINT失敗，請重新進入</h1>'
   
    # 下載日常點檢資料
    table = 'nor_check'
    nor_check = mysql2df(table)
    if type(nor_check) == 'str':
        return '<h1>讀取資料庫nor_check失敗，請重新進入</h1>'
            

    lines = ['CT1', 'OCT', 'LASER']
    
    fliterCT1 = (maint_list["Class"] == "CT1")
    ct1Data = maint_list[fliterCT1]
    
    fliterOCT = (maint_list["Class"] == "OCT")
    octData = maint_list[fliterOCT]
    fliterLSR = (maint_list["Class"] == "LASER")
    lsrData = maint_list[fliterLSR]
    
    min_Done = [min(ct1Data.loc[:, 'Done']), min(octData.loc[:, 'Done']), min(lsrData.loc[:, 'Done'])]
    print('主頁面reload')
    notify='哈囉有收到嗎'
    
    # 修正版oracle 與法
    
    Start_Day = date1[0:4]+'/'+date1[5:7]+'/'+date1[8:10]
    End_Day = date2[0:4]+'/'+date2[5:7]+'/'+date2[8:10]
    
    mysql = "select t.mfg_day, t.model_no, t.test_user as LINE, count(*)as TOT"
    mysql = mysql + ",round(100*sum(decode(t.grade,'G',1,0))/count(*),1) as GO"
    mysql = mysql + ",round(100*sum(decode(t.defect_code_desc,'V-OPEN-BL',1,0))/count(*),2) as VOBL" #原V_OPEN_BL
    mysql = mysql + ",round(100*sum(decode(t.defect_code_desc,'OTHER ALIGN DEFECT',1,0))/count(*),2) as OAD"
    mysql = mysql + ",round(100*sum(decode(t.defect_code_desc,'OTHER APPEAR DEFECT',1,0))/count(*),2) as OAPD" #原O_A_D
    mysql = mysql + ",round(100*sum(decode(t.defect_code_desc,'OTHER GLASS DEFECT',1,0))/count(*),2) as OGD"
    #mysql = mysql + ",round(100*sum(decode(t.defect_code_desc,'OTHER LINE DEFECT ',1,0))/count(*),1) as OLD" #原O_L_D
    #mysql = mysql + ",round(100*sum(decode(t.defect_code_desc,'BP',1,0))/count(*),1) as BP"

    #mysql = mysql + ",'" + Start_Day + "' as Start_Day,'" + End_Day + "' as End_Day "
    
    mysql = mysql + " from celods.h_dax_fbk_test_ods t where t.op_id='CGL' "
    mysql = mysql + " and t.mfg_day between to_date('" + Start_Day + "','yyyy/mm/dd') and to_date('" + End_Day + "','yyyy/mm/dd')"
    
    mysql = mysql + " group by (t.mfg_day, t.model_no, t.test_user) order by t.test_user"
    
    
    ct1_summ2_date12 = [date1, date2]
    
    ct1_summ2 = ora2df(mysql)
    #mach = [ [0,'CCCGL1082',1], [1,'CCCGL1083',0], [2,'CCCGL2082', 1], [3,'CCCGL2083', 0] ]st.values.tolist(), maint_showIdx=maint_showIdx, mi 
    
    return render_template('userMain.html', user=str(user),name=name, auth=auth, shift=shift, today=today, maint_list = maint_list.values.tolist(), min_Done=min_Done, nor_check=nor_check, sectShow=sectShow, ct1_summ2=ct1_summ2, ct1_summ2_date12=ct1_summ2_date12)

def datesListStr(start_date, end_date):

    start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    date_generated = [start + datetime.timedelta(days=x) for x in range(0, (end-start).days+1)]
    date_list=[]
    for date in date_generated:
        date_list.append(date.strftime("%Y-%m-%d"))

    return date_list

def outlook(receiver,cc,body,subject,file):
    pythoncom.CoInitialize() # is not initialized in the new thread 
    subprocess.Popen(['C:/Program Files (x86)/Microsoft Office/Office12/OUTLOOK.exe']) #自動開啟OUTLOOK
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
    tt.sleep(10)        #不DELAY可能會來不及完成寄送而關閉不了   
    outlook.Quit()
    del outlook
    gc.collect()  
    print('Email已寄出')
    
def mailCraig(subject, body):
    pythoncom.CoInitialize() # is not initialized in the new thread 
    subprocess.Popen(['C:/Program Files (x86)/Microsoft Office/Office12/OUTLOOK.exe']) #自動開啟OUTLOOK
    receiver = 'Craig.Hsiao@auo.com;'
    cc = 'Craig.Hsiao@auo.com;'
    file = []
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
    time.sleep(6)        #不DELAY可能會來不及完成寄送而關閉不了   
    outlook.Quit()
    del outlook
    gc.collect()  
    print('Email已寄出')

#loc = r'\\tw100039213\kjchen-pc02\web v3\WebApplication1\L7AC2 IDL\00 L7AC2部門公用資料夾\10 系統Auto Data\003_Maint_record'
#receiver = 'Craig.Hsiao@auo.com;'
#receiver2 = 'Alex.XC.Pan@auo.com;'+'Yida.Tsai@auo.com;'+ 'Calvin.Wang@auo.com;'+ 'Roger.CH.Hsu@auo.com;'+ 'Jh.Hsu@auo.com;'+'Craig.Hsiao@auo.com;'
#receiver1 = 'Alex.XC.Pan@auo.com;'+'Yida.Tsai@auo.com;'+ 'Calvin.Wang@auo.com;'+ 'Roger.CH.Hsu@auo.com;'+ 'Jh.Hsu@auo.com;'+'Craig.Hsiao@auo.com;'+'KJ.Chen@auo.com;'
#cc = 'Craig.Hsiao@auo.com;'#CC

# checkbox value值轉str
def v2s(s):
    if s is None:
        return '0'
    else:
        return s

def notDate(date):
    try:
        datetime.datetime.strptime(date, "%Y%m%d")
    except:
        return True
    else:
        return False
    
#　Test_Time轉MFG DateTime
def testTime2MFG(test_time):
    date = test_time[0:10]
    time0 = test_time[11:16]
    print(date, time0)
    
    if int(time0[0:2]) < 7 or (int(time0[0:2]) == 7 and int(time0[3:5]) < 30):
        date2 = datetime.datetime.strptime(date, "%Y-%m-%d")
        date = (date2+datetime.timedelta(-1)).strftime("%Y-%m-%d")
        return date
    else:
        return date
    
@app.route('/')
def main():
    return 'hi no'

@app.route('/login', methods=['GET', 'POST'])
def login():
    
    if request.method == 'POST':
        # 謥登入進來的
        if request.form.get('goLogin') is not None and request.values['goLogin']=='goLogin':
            return render_template('login3.html')
    else:
        return render_template('login3.html')
    


@app.route('/dailycheckform', methods=['GET', 'POST'])
def dailycheckform():
    return render_template('dailycheckform.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
     if request.method == 'POST':
        # 謥登入進來的
        
        
            
            
        if request.form.get('reg') is not None and request.values['reg']=='register':
            
            return render_template('register.html', notify='hihi') 
    
        # 從自己進來的
        elif request.form.get('regOK') is not None and request.values['regOK']=='registerOK':
            user = request.form.get('userNum')
            pw1 = request.form.get('pw1')
            pw2 = request.form.get('pw2')
            
            if pw1 != pw2 :
                return render_template('register.html', notify='Error!!二次輸入密碼不同') 
            
            if len(user) != 7: 
                return render_template('register.html', notify='Error!!工號須為7碼') 
            try:
                print(str(user)+'進行註冊中...')
                conn = pymysql.connect(host='localhost',user='craig945',password='ml7ac222',db='craig01',port=3306)
                cur = conn.cursor()
            
                cur.execute("SELECT * FROM user_data")  # 執行查詢語句
                # fetchall()以list的方式回傳所有資料或者是空list(無資料)
                result = cur.fetchall()  # 獲取查詢結果
                col = cur.description  # 獲取查詢結果的欄位描述
                columns=[]
                for i in range(len(col)):
                    columns.append(col[i][0])  # 獲取欄位名，列表形式儲存
                userData = pd.DataFrame(result, columns=columns)
                conn.close()
                #print(maint_list)
            except:
                return render_template('register.html', notify='Error!!下載資料庫失敗，請重新送出or聯絡管理員') 
            
            try:
                for i in range(len(userData)):
                    if int(user) == int(userData.loc[i]['Number']):
                        userData.loc[i, 'PW'] = pw1
                         
 
                        #回傳資料庫
                        engine = create_engine("mysql+pymysql://craig945:ml7ac222@localhost:3306/craig01") 
                        #delete = 'DROP TABLE IF EXISTS maint;'
                        #engine.execute(delete)                 
                        print('  create_engine ok')
                        userData.to_sql('user_data', engine, if_exists='replace',index=False) 
                        print('  to_sql ok')
                        engine.dispose()
                        return render_template('register.html', notify='註冊成功!!!請按"返回登入"!!!') 
            except:
                         #engine.dispose()
                return render_template('register.html', notify='Error!!上傳資料庫失敗，請重新送出or聯絡管理員') 
            
            
            
                
      # 取得/login中選擇人物 
     
", "", "#跳入機台選單，攜帶變數
         


@app.route('/para/<user>')
def index(user):
    return render_template('ccc.html', user_template=user)


    
@app.route('/user/<uName>')
def userName(uName):
    return 'hiiiiiii???' + uName

@app.route('/userMain/ct1summary', methods=['GET', 'POST'])
def ct1summary():
    if request.method == 'POST':
        aaa = request.form.get('aaa')
        return(aaa)
        
        
        
@app.route('/login/<sys_name>/<paras>/', methods=['GET', 'POST'])
def loginGo(sys_name, paras):
    
    if request.method == 'POST':
        # 謥登入進來的
        if request.form.get('goLogin') is not None and request.values['Login']!='Login':
            return render_template('login_go.html', sys_name=sys_name, paras=paras)
        
        print('hiiiii')
        return render_template('login_go.html', sys_name=sys_name, paras=paras)
    else:
        return render_template('login_go.html', sys_name=sys_name, paras=paras)
        
        
        
@app.route('/<sys_name>/<paras>/', methods=['GET', 'POST'])
def systemGo(sys_name, paras):
    user = 'Public'
    name = 'Public'
    shift = 'Public'
    auth = 'Public'
    
    today = datetime.date.today().strftime("%Y-%m-%d")
    now = datetime.datetime.now().strftime("%Y%m%d%H%M")
    ystday = (datetime.date.today()+datetime.timedelta(-1)).strftime("%Y-%m-%d")
    if int(now[-4:]) < 730:
        today_mfg = ystday
    else:
        today_mfg = today
    #return octOLD(user,name, auth, shift, date1, date2, old_shift)
    #octOGDOAD(user,name, auth, shift, date1, date2, sql_shift, oct_def, isCT1data)
                
    #sys_name = request.form.get('sys_name')
    """
    if request.form.get('showNorCheck') is not None:
            
            sectShow = 'showNorCheck'
            site = request.form.get('showNorCheck')
            # 下載日常點檢資料
            table = 'nor_check'
            nor_check = mysql2df(table)
            
            return render_template('userMain.html', user=str(user),name=name, auth=auth, shift=shift, nor_check=nor_check, site=site, sectShow=sectShow)

    if request.form.get('maint') is not None:
        sectShow = 'maint'
        
        table = "maint"
        maint_list = mysql2df(table)
        fliterCT1 = (maint_list["Class"] == "CT1")
        ct1Data = maint_list[fliterCT1]
        fliterOCT = (maint_list["Class"] == "OCT")
        octData = maint_list[fliterOCT]
        fliterLSR = (maint_list["Class"] == "LASER")
        lsrData = maint_list[fliterLSR]
        
        min_Done = [min(ct1Data.loc[:, 'Done']), min(octData.loc[:, 'Done']), min(lsrData.loc[:, 'Done'])]
        return render_template('userMain.html', user=str(user),name=name, auth=auth, shift=shift, today=today, maint_list = maint_list.values.tolist(), min_Done=min_Done, sectShow=sectShow)
    """
    print(sys_name, paras)
    if paras == 'mfgtoday':
        date1 = today_mfg
        date2 = today_mfg
    else:
        spl = paras.split('$')
    if 1:
        if sys_name == 'norcheck':
            sectShow = 'showNorCheck'
            site = paras
            # 下載日常點檢資料
            table = 'nor_check'
            nor_check = mysql2df(table)
              
            return render_template('userMain_single.html', user=str(user),name=name, auth=auth, shift=shift, nor_check=nor_check, site=site, sectShow=sectShow)

        elif sys_name == 'cps' and paras == 'pmplan':
            sectShow = 'cps'
            table = 'cps_pmplan'
            df0 = mysql2df(table)
            df0 = df0[df0['PM_Plan'] == 'NG'].copy()
            df0.rename(columns = {'Machine': 'EQP'}, inplace=True)
            
            df0['建議'] = '近日安排保養'
            df0 = df0[['EQP', '建議' ,'PM_Ratio']].copy()
            item_name = 'PM Plan'
            return render_template('userMain_single.html', user=str(user),name=name, auth=auth, shift=shift, 
                                   df0=df0, item_name=item_name, sectShow=sectShow)
        
        elif sys_name == 'cps' and paras == 'ct1eqpdiff':
            sectShow = 'cps'
            df0 = cpsEQP_Diff(today, today)
            item_name = 'CT1機差'
            return render_template('userMain_single.html', user=str(user),name=name, auth=auth, shift=shift,
                                   df0=df0, item_name=item_name,sectShow=sectShow)
        # EDA用
        elif sys_name == 'eda'and paras == 'hr':
            sectShow = 'hr'
            df0 = edaHR()
            item_name = '人事系統'
            return render_template('userMain_single.html', user=str(user),name=name, auth=auth, shift=shift,
                                   df0=df0, item_name=item_name,sectShow=sectShow)
        
        
        elif sys_name == 'ct1ADC':
            spl = paras.split('$')
            if paras != 'mfgtoday':
                date1 = spl[0]
                date2 = spl[1]
            return ct1ADC(user,name, auth, shift, date1, date2)
        elif sys_name == 'octOLD':
            spl = paras.split('$')
            if paras != 'mfgtoday':
                date1 = spl[0]
                date2 = spl[1]
            # D 日班; N
            old_shift = 'All'
            #old_shift = spl[2]
            return octf.octOLD(user,name, auth, shift, date1, date2, old_shift)
        elif sys_name in ['octOGD', 'octOAPD', 'octAD']:
            spl = paras.split('$')
            if paras != 'mfgtoday':
                date1 = spl[0]
                date2 = spl[1]
            # D 日班; N
            sql_shift = 'All'
            #sql_shift = spl[2]
            if sys_name == 'octOGD':
                oct_def = 'OTHER GLASS DEFECT'
            elif sys_name == 'octOAPD':
                oct_def = 'OTHER APPEAR DEFECT'
            elif sys_name == 'octAD':
                oct_def = 'ABNORMAL DISPLAY'

            isCT1data = False
            return octf.octOGDOAD(user,name, auth, shift, date1, date2, sql_shift, oct_def, isCT1data)
        elif sys_name == 'octPADCOR':
            if paras != 'mfgtoday':
                date1 = spl[0]
                date2 = spl[1]
            return octf.octPADCOR(user,name, auth, shift, date1, date2)
        elif sys_name == 'octDP2BP':
            if paras != 'mfgtoday':
                date1 = spl[0]
                date2 = spl[1]
            return octf.octDP2BP(user,name, auth, shift, date1, date2)
        elif sys_name == 'octADCRBSuc':
            if paras != 'mfgtoday':
                date1 = spl[0]
                date2 = spl[1]
            return octf.octADCRBSuc(user,name, auth, shift, date1, date2)
        elif sys_name == 'octADCRBRej':
            if paras != 'mfgtoday':
                date1 = spl[0]
                date2 = spl[1]
            return octf.octADCRBRej(user,name, auth, shift, date1, date2)
        elif sys_name == 'octADCRBSamp':
            if paras != 'mfgtoday':
                date1 = spl[0]
                date2 = spl[1]
            return octf.octADCRBSamp(user,name, auth, shift, date1, date2)
    
    else:
        return "<h1>網址格式有誤</h1>"
@app.route('/publicMain', methods=['GET', 'POST'])
def publicMain():
    today = datetime.date.today().strftime("%Y-%m-%d")
    now = datetime.datetime.now().strftime("%Y%m%d%H%M")
    ystday = (datetime.date.today()+datetime.timedelta(-1)).strftime("%Y-%m-%d")
    if int(now[-4:]) < 730:
        today_mfg = ystday
    else:
        today_mfg = today
    
    
    user = 'Public'
    name = 'Public'
    shift = 'Public'
    auth = 'Public'
    if request.method == 'POST':
    # PCS000 MOVE監測 公開版
    
    
    
        if request.form.get('ct1Summ2') is not None:
            print('ok')
            
            
            
            date1 = request.form.get('ct1Summ2_date1')
            
            date2 = request.form.get('ct1Summ2_date2')
            
            if date1 is None:
                #today = today0[0:4]+'/'+today0[4:6]+'/'+today0[6:8]
                date1 = today_mfg
                date2 = today_mfg
                
            
            sectShow = 'ct1Summ2'
    
            today0 = datetime.date.today().strftime("%Y%m%d")
            today = today0[0:4]+'-'+today0[4:6]+'-'+today0[6:8]
            now = datetime.datetime.now().strftime("%Y%m%d%H%M")
            # 下載保養資料
            table = 'maint'
            maint_list = mysql2df(table)
            if type(maint_list) == 'str':
                return '<h1>讀取資料庫MAINT失敗，請重新進入</h1>'
           
            # 下載日常點檢資料
            table = 'nor_check'
            nor_check = mysql2df(table)
            if type(nor_check) == 'str':
                return '<h1>讀取資料庫nor_check失敗，請重新進入</h1>'
                    
        
            lines = ['CT1', 'OCT', 'LASER']
            
            fliterCT1 = (maint_list["Class"] == "CT1")
            ct1Data = maint_list[fliterCT1]
            
            fliterOCT = (maint_list["Class"] == "OCT")
            octData = maint_list[fliterOCT]
            fliterLSR = (maint_list["Class"] == "LASER")
            lsrData = maint_list[fliterLSR]
            
            min_Done = [min(ct1Data.loc[:, 'Done']), min(octData.loc[:, 'Done']), min(lsrData.loc[:, 'Done'])]
            print('主頁面reload')
            notify='哈囉有收到嗎'
            
            # 修正版oracle 與法
            
            Start_Day = date1[0:4]+'/'+date1[5:7]+'/'+date1[8:10]
            End_Day = date2[0:4]+'/'+date2[5:7]+'/'+date2[8:10]
            
            mysql = "select t.mfg_day, t.model_no, t.test_user as LINE, count(*)as TOT"
            mysql = mysql + ",round(100*sum(decode(t.grade,'G',1,0))/count(*),1) as GO"
            mysql = mysql + ",round(100*sum(decode(t.defect_code_desc,'V-OPEN-BL',1,0))/count(*),2) as VOBL" #原V_OPEN_BL
            mysql = mysql + ",round(100*sum(decode(t.defect_code_desc,'OTHER ALIGN DEFECT',1,0))/count(*),2) as OAD"
            mysql = mysql + ",round(100*sum(decode(t.defect_code_desc,'OTHER APPEAR DEFECT',1,0))/count(*),2) as OAPD" #原O_A_D
            mysql = mysql + ",round(100*sum(decode(t.defect_code_desc,'OTHER GLASS DEFECT',1,0))/count(*),2) as OGD"
            #mysql = mysql + ",round(100*sum(decode(t.defect_code_desc,'OTHER LINE DEFECT ',1,0))/count(*),1) as OLD" #原O_L_D
            #mysql = mysql + ",round(100*sum(decode(t.defect_code_desc,'BP',1,0))/count(*),1) as BP"
        
            #mysql = mysql + ",'" + Start_Day + "' as Start_Day,'" + End_Day + "' as End_Day "
            
            mysql = mysql + " from celods.h_dax_fbk_test_ods t where t.op_id='CGL' "
            mysql = mysql + " and t.mfg_day between to_date('" + Start_Day + "','yyyy/mm/dd') and to_date('" + End_Day + "','yyyy/mm/dd')"
            
            mysql = mysql + " group by (t.mfg_day, t.model_no, t.test_user) order by t.test_user"
            
            
            ct1_summ2_date12 = [date1, date2]
            
            ct1_summ2 = ora2df(mysql)
            #mach = [ [0,'CCCGL1082',1], [1,'CCCGL1083',0], [2,'CCCGL2082', 1], [3,'CCCGL2083', 0] ]st.values.tolist(), maint_showIdx=maint_showIdx, mi 
            
            return render_template('publicMain.html', user=str(user),name=name, auth=auth, shift=shift, today=today, maint_list = maint_list.values.tolist(), min_Done=min_Done, nor_check=nor_check, sectShow=sectShow, ct1_summ2=ct1_summ2, ct1_summ2_date12=ct1_summ2_date12)

            return ct1Summ2(user,name, auth, shift, date1, date2)
        btnName = list(request.form)[-1]
         
        # ct1Summ2表格之第二層cHIPID列表觸發 Public版本
        if btnName[0:9] == 'ct1Summ__':
            
            
            
            
            user = request.form.get('user')
            name = request.form.get('name')
            shift = request.form.get('shift')
            auth = request.form.get('auth')
            date1 = request.form.get('ct1Summ2_date1')
            date2 = request.form.get('ct1Summ2_date2')
            isGoHours = False
            sectShow = 'ct1_summ2_chipid'
            #now = datetime.datetime.now().strftime("%Y%m%d%H%M")
            
            logging.info("ct1良率第二層觸發,  "+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            ABBR_DEFECT_NAMES = ['BP',    'V_O'   , 'V_L'   ,     'H_O', 'H_L',    'X_S'  ,  'VOBL'    ,  'H_BAND_MURA', 'W_S'       ,     'B_S',       'AGM'            , 'OAD'            , 'OAPD',            
                                            'OGD',    'DP_W', 'DPP_W', 'DP_CLUSTER', 'DP_ADJ'   , 'DP_NEAR', 'BPP'     , 'SBP_XW',   'CP',       'POINT_COUNT' ]
            
            WHOLE_DEFECT_NAMES = ['BP', 'V-OPEN', 'V-LINE' , 'H-OPEN', 'H-LINE', 'X-SHORT', 'V-OPEN-BL', 'H-BAND MURA', 'WHITE SPOT', 'BLACK SPOT', 'AROUND GAP MURA', 'OTHER ALIGN DEFECT', 'OTHER APPEAR DEFECT',
                                  'OTHER GLASS DEFECT', 'DP', 'DP-PAIR', 'DP-CLUSTER', '3DP-ADJ', 'DP-NEAR', 'BP-PAIR', 'SMALL BP', 'PD13 ',   'POINT-COUNT']   

            A2W_DEFECT_NAMES = {}
            for i in range(len(ABBR_DEFECT_NAMES)):
                A2W_DEFECT_NAMES[ABBR_DEFECT_NAMES[i]] = WHOLE_DEFECT_NAMES[i]
                
            # 補充包
            A2W_DEFECT_NAMES['AGM_X'] = 'AROUND GAP MURA'
            A2W_DEFECT_NAMES['AGM_Y'] = 'AROUND GAP MURA'

            if date1 is None:
                1
                #date1 = today_mfg
                #date2 = today_mfg
            

            aaa = btnName.split('__', 4)
            print(aaa)
            logging.info('傳入NAME為: '+btnName)
            print('傳入NAME為: '+btnName)
            date = aaa[1]
            date1 = date
            date2 = date
            model_no = aaa[2]
            eqp = aaa[3]
            # 假如沒有找到對應，直接使用原始名稱
            try:
                defect = A2W_DEFECT_NAMES[aaa[4]]
            except:
                defect = aaa[4]
            go_hour = '00'
            return ct1DefectImg(user,name, auth, shift, date1, date2, model_no, defect, eqp, isGoHours, go_hour)
            
            
            
            
            
            
        
        
        if request.form.get('pcsCheck') is not None:
            print('pcsCheck Post')
            table = 'pcs_check2'
            pcs_record = mysql2df(table)
            #pcs_check = mysql2df(table)
            date = request.form.get('pcsCheck_date')
            if date is None:
                date = today_mfg
            
            pcs_check = pd.DataFrame(columns=pcs_record.columns)
            for i in range(len(pcs_record)):
                if pcs_record.loc[i]['MFG_Date'] == date:
                    pcs_check.loc[i] = pcs_record.loc[i]
            
            pcsCheck_date=date
            sectShow = 'pcsCheck'
            
            
            if  request.values['pcsCheck']=='download':
                
                pcs_check.reset_index(inplace=True)
                cols = list(pcs_check.columns)
                print(cols)
                for i in range(len(cols)):
                    if i >= 4:
                        
                        for idx in range(len(pcs_check)):
                            if pcs_check.loc[idx, cols[i]] == -1 :
                                pcs_check.loc[idx, cols[i]] = ''
                        cols[i] = cols[i][0:2] +':'+ cols[i][3:5]
                pcs_check.columns = cols
                pcs_check = pcs_check.drop(columns =['index','Date'])
                
                date = date[2:4]+date[5:7]+date[8:10]
                filepath = r'static\pcsCheck_'+date+'.csv'
                pcs_check.to_csv(filepath, index=False)
                file = 'pcsCheck_'+date+'.csv'
                path = r'static'
                

                return send_from_directory(path, file, as_attachment=True)
            
            
            
            return render_template('publicMain.html', user=str(user),name=name, auth=auth, shift=shift, sectShow=sectShow, pcs_check=pcs_check, pcsCheck_date=pcsCheck_date)
        
    return render_template('publicMain.html', user=str(user),name=name, auth=auth, shift=shift)

@app.route('/userMain', methods=['GET', 'POST'])
def userMain():
    name0000 = request.form.get('name')
    print(name0000, '進入userMain')
    #tt.sleep(5)
    today0 = datetime.date.today().strftime("%Y%m%d")
    today = datetime.date.today().strftime("%Y-%m-%d")
    now = datetime.datetime.now().strftime("%Y%m%d%H%M")
    # 上傳紀錄時間用
    now2 = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    print(name0000, '進入userMain', now2)
    ystday = (datetime.date.today()+datetime.timedelta(-1)).strftime("%Y-%m-%d")
    if int(now[-4:]) < 730:
        today_mfg = ystday
    else:
        today_mfg = today
    sectShow = ''
    btnName = list(request.form)[-1]
    print( 'list(request.form) => ', list(request.form))   
        


    lines = ['CT1', 'OCT', 'LASER']

    notify='哈囉有收到嗎'
    
    
    if request.method == 'POST':
        print('進入request.method == POST')
        
        if request.form.get('login') is not None and request.values['login'] !='login':
            user = request.form.get('userNum')
            pw = request.form.get('pw')
            paras = request.form.get('login')
            sys_name = request.form.get('sys_name')
            print("sys_name", sys_name, paras)
            if len(user) != 7: 
                return loginGo(sys_name, paras)
            
            
            print(str(user)+'登入進行中...')
            try:
                
                conn = pymysql.connect(host='localhost',user='craig945',password='ml7ac222',db='craig01',port=3306)
                cur = conn.cursor()
            
                cur.execute("SELECT * FROM user_data")  # 執行查詢語句
                # fetchall()以list的方式回傳所有資料或者是空list(無資料)
                result = cur.fetchall()  # 獲取查詢結果
                col = cur.description  # 獲取查詢結果的欄位描述
                columns=[]
                for i in range(len(col)):
                    columns.append(col[i][0])  # 獲取欄位名，列表形式儲存
                userData = pd.DataFrame(result, columns=columns)
                conn.close()
            except:
                return loginGo(sys_name, paras) 
            print('pw=',pw)
            #print(userData)
            for i in range(len(userData)):
                #print(user, userData.loc[i]['Number'])
                if int(user) == int(userData.loc[i]['Number']):
                    print('找到工號')
                    if pw == userData.loc[i]['PW']:
                        auth = userData.loc[i]['Auth']
                        name = userData.loc[i]['Name']
                        shift = userData.loc[i]['Shift']
                        break
                    else:
                        print('密碼錯誤ｅｌｓｅ')
                        return loginGo(sys_name, paras)
                        #return render_template('login_go.html', notify='密碼錯誤哦~') 
                elif i == (len(userData)-1):
                    return loginGo(sys_name, paras)
            
            #sys_name = request.form.get('sys_name')
            print("sys_name", sys_name, paras)
            if sys_name == 'ct1adc':
                #paras = request.form.get('login')
                spl = paras.split('$')
                date1 = spl[0]
                date2 = spl[1]
                return ct1ADC(user,name, auth, shift, date1, date2)
            
                #return octOLD(user,name, auth, shift, date1, date2, old_shift)
                #octOGDOAD(user,name, auth, shift, date1, date2, sql_shift, oct_def, isCT1data)
                
        elif request.form.get('login') is not None and request.values['login']=='login':
            user = request.form.get('userNum')
            pw = request.form.get('pw')
            
            
            if len(user) != 7: 
                return loginGo(sys_name, paras)
            
            
            print(str(user)+'登入進行中...')
            try:
                
                conn = pymysql.connect(host='localhost',user='craig945',password='ml7ac222',db='craig01',port=3306)
                cur = conn.cursor()
            
                cur.execute("SELECT * FROM user_data")  # 執行查詢語句
                # fetchall()以list的方式回傳所有資料或者是空list(無資料)
                result = cur.fetchall()  # 獲取查詢結果
                col = cur.description  # 獲取查詢結果的欄位描述
                columns=[]
                for i in range(len(col)):
                    columns.append(col[i][0])  # 獲取欄位名，列表形式儲存
                userData = pd.DataFrame(result, columns=columns)
                conn.close()
            except:
                return render_template('login3.html', notify='Error!!下載資料庫失敗，請重新送出or聯絡管理員') 
            print('pw=',pw)
            print(userData.loc[i]['PW'])
            for i in range(len(userData)):
                
                if int(user) == int(userData.loc[i]['Number']):
                    print('找到工號')
                    if pw == userData.loc[i]['PW']:
                        auth = userData.loc[i]['Auth']
                        name = userData.loc[i]['Name']
                        shift = userData.loc[i]['Shift']
                        break
                    else:
                        print('密碼錯誤ｅｌｓｅ')
                        return render_template('login3.html', notify='密碼錯誤哦~') 
                elif i == (len(userData)-1):
                    return render_template('login3.html', notify='無此人員，請聯絡管理員') 
            print(str(user)+'登入系統')
        
        else:
            # 非登入post 統一讀取個人資料
            user = request.form.get('user')
            name = request.form.get('name')
            shift = request.form.get('shift')
            auth = request.form.get('auth')
            if user == 'Public':
                isRaw = False
                for req0 in list(request.form):
                    if 'Raw' in req0:
                        isRaw = True
                        break
                if not isRaw:
                    return "<h1>禁止訪問!!!請回上一頁<h1>"
        
        # 人事系統 hr
        
        req_name_list = ['hr', 'hr_newEmpolyee', 'hr_changeShift', 'hr_leave', 'hr_leaveTimeout', 'hr_overwork']
        req_name_list = ['hr']
        for req_name in req_name_list:
            if request.form.get(req_name) is not None:
                return hrMain(user,name, auth, shift, req_name)
                        
         
        req_name = 'hr_newEmployeeBtn'
        if request.form.get(req_name) is not None:
            return hr_newEmployeeBtn(user,name, auth, shift, today)
        req_name = 'hr_changeShift'
        if request.form.get(req_name) is not None:
            return hr_changeShift(user,name, auth, shift)
        
    
        
        req_name = 'hr_changeShift_upload'
        if request.form.get(req_name) is not None:
            return hr_changeShift_upload(user,name, auth, shift)
        # 機台點檢系統
        if request.form.get('showNorCheck') is not None:
            
            sectShow = 'showNorCheck'
            site = request.form.get('showNorCheck')
            # 下載日常點檢資料
            table = 'nor_check'
            nor_check = mysql2df(table)
            
            return render_template('userMain.html', user=str(user),name=name, auth=auth, shift=shift, nor_check=nor_check, site=site, sectShow=sectShow)
        
        
        
        # 環安點檢系統
        if request.form.get('ESCheck') is not None:
            
            sectShow = 'ESCheck'
            # 環安項目點擊
            ES_item = request.form.get('ESCheck')
            if ES_item == '環安點檢':
                table = 'es_check'
                ESCheck = mysql2df(table)
                ESCheck = ESCheck[['TYPE_NAME', 'ITEM_NAME',  'STATUS', 'CONTENT']].copy()
                ESCheck['ROW_CNT'] = 1
                if len(ESCheck) > 0:
                    start_idx = 0
                    type0 = ESCheck.loc[0]['TYPE_NAME']
                for idx in ESCheck.index[1:]:
                    next_type0 = ESCheck.loc[idx]['TYPE_NAME']
                    if type0 == next_type0:
                        ESCheck.loc[start_idx, 'ROW_CNT'] = ESCheck.loc[start_idx]['ROW_CNT'] + 1
                        ESCheck.loc[idx, 'ROW_CNT'] = -1
                    else:
                        start_idx = idx
                        type0 = next_type0
    
                return render_template('userMain.html', user=str(user),name=name, auth=auth, shift=shift, ESCheck=ESCheck, sectShow=sectShow)

        
        
        
        
        
        
        
        if request.form.get('maint') is not None:
            sectShow = 'maint'
            
            table = "maint"
            maint_list = mysql2df(table)
            fliterCT1 = (maint_list["Class"] == "CT1")
            ct1Data = maint_list[fliterCT1]
            fliterOCT = (maint_list["Class"] == "OCT")
            octData = maint_list[fliterOCT]
            fliterLSR = (maint_list["Class"] == "LASER")
            lsrData = maint_list[fliterLSR]
            
            min_Done = [min(ct1Data.loc[:, 'Done']), min(octData.loc[:, 'Done']), min(lsrData.loc[:, 'Done'])]
            return render_template('userMain.html', user=str(user),name=name, auth=auth, shift=shift, today=today, maint_list = maint_list.values.tolist(), min_Done=min_Done, sectShow=sectShow)
    
            
        if request.form.get('Maint_Status') is not None:
            
            print("Maint_Status表單觸發")
            mach_data = request.values['Maint_Status']
            data_list = mach_data.split('_', 2)
            class0 = data_list[0]
            mach0 = data_list[1]
            last_time = data_list[2]
            time = today
            logging.info("Maint_Status表單觸發, "+mach_data)
            
            user = request.form.get('user')
            name = request.form.get('name')
            shift = request.form.get('shift')
            auth = request.form.get('auth')
            
            return render_template('maintDateChangeList.html', class0=class0, mach0=mach0, user=user, name=name, shift=shift,last_time=last_time, time=time)
            
        if request.form.get('MaintDateChangeBtn') is not None:
            print('進入Maint date更新')
            logging.info("  進入Maint date更新 ")
            sectShow = 'maint'
            name = request.form.get('Name')
            user = request.form.get('User')
            class0 = request.form.get('Class')
            mach0 = request.form.get('Machine')
            date00 = request.form.get('Date')
            remarks0 = request.form.get('Remarks')
            date0 = date00
            done0 = 1

            table = "maint_history"
            maint_history = mysql2df(table)
            #maint_history = pd.DataFrame()
            maint_names = ['_OK', '_rem']
            new_n = len(maint_history)
            
            maint_history.loc[new_n, 'EQP'] = mach0
            maint_history.loc[new_n, 'Site'] =class0
            maint_history.loc[new_n, 'Maint_Date'] = date0
            maint_history.loc[new_n, 'Remarks'] =remarks0
            maint_history.loc[new_n, 'Maint_Person'] = str(user)+name
            
            isOKs = True
            key_word = "Maint_Check0"
            for num in range(1, 4, 1):
                for mn in maint_names:
                    req_name = key_word + str(num) + mn
                    val = request.form.get(req_name)
                    if mn == '_OK' and val == 'NG':
                        isOKs = False
                    maint_history.loc[new_n, req_name] = val
                    
            
            df2mysql(maint_history, table)
            
            # 更新燈號
            table = "maint"
            maint_list = mysql2df(table)

            if isOKs:
                for i in range(len(maint_list)):
                    if maint_list.loc[i]['Machine'] == mach0:
                        maint_list.loc[i, 'Date'] = date0
                        maint_list.loc[i, 'Person'] = str(user)+name
                        # Done=2做完但保養時間內; Done=1做完但保養時間外(由系統修改)
                        maint_list.loc[i, 'Done'] = 2
            
            fliterCT1 = (maint_list["Class"] == "CT1")
            ct1Data = maint_list[fliterCT1]
            fliterOCT = (maint_list["Class"] == "OCT")
            octData = maint_list[fliterOCT]
            fliterLSR = (maint_list["Class"] == "LASER")
            lsrData = maint_list[fliterLSR]
            min_Done = [min(ct1Data.loc[:, 'Done']), min(octData.loc[:, 'Done']), min(lsrData.loc[:, 'Done'])]

            df2mysql(maint_list, table)
            
            return render_template('userMain.html', user=str(user),name=name, auth=auth, shift=shift, today=today, maint_list = maint_list.values.tolist(), min_Done=min_Done, sectShow=sectShow)
                      

        if request.form.get('yieldSumm') is not None:
            user = request.form.get('user')
            name = request.form.get('name')
            shift = request.form.get('shift')
            auth = request.form.get('auth')
            req_list = list(request.form)
            date1 = request.form.get('ct1Summ_date1')
            date2 = request.form.get('ct1Summ_date2')
            if date1 is None:
                #today = today0[0:4]+'/'+today0[4:6]+'/'+today0[6:8]
                date1 = today_mfg
                date2 = today_mfg
            
            return yieldSumm(user,name, auth, shift, date1, date2, req_list)
       
        # ct1良率 每小時go ratio
        sub_name = 'goHours'
        if request.form.get(sub_name) is not None:
            print(sub_name + 'Post')
            logging.info((sub_name + 'Post'))
            date = request.form.get('goHours_date')
            print(date)
            if date is None:
                date = today_mfg
            return goHours(user,name, auth, shift, date)
        
        if request.form.get('ct1SameDef') is not None:
            user = request.form.get('user')
            name = request.form.get('name')
            shift = request.form.get('shift')
            auth = request.form.get('auth')

            date = request.form.get('ct1SameDef_date')
            
            if date is None:
                #today = today0[0:4]+'/'+today0[4:6]+'/'+today0[6:8]
                date = today_mfg
            print(date)
            return ct1SameDef(user,name, auth, shift, date)
        
        # L7AH1 Monitor
        if request.form.get('ct1Summ2') is not None:
            print('ok')
            
            user = request.form.get('user')
            name = request.form.get('name')
            shift = request.form.get('shift')
            auth = request.form.get('auth')
            
            date1 = request.form.get('ct1Summ2_date1')
            
            date2 = request.form.get('ct1Summ2_date2')
            
            if date1 is None:
                #today = today0[0:4]+'/'+today0[4:6]+'/'+today0[6:8]
                date1 = today_mfg
                date2 = today_mfg
                return ct1Summ2(user,name, auth, shift, date1, date2)
            else:

                return ct1Summ2(user,name, auth, shift, date1, date2)
            #return ct1Summ2(user,name, auth, shift)
        
        
                    
        # ct1良率 每小時go ratio之第二層cHIPID列表觸發
        sub_name = 'goHours__'
        if btnName[0:9] == sub_name:
            print(sub_name + 'Post', btnName)
            logging.info((sub_name + 'Post'))
            return goHoursRaw(user,name, auth, shift, btnName)
        
        # ct1良率 機差
        sub_name = 'ct1MachDiff'
        if request.form.get(sub_name) is not None:
            print(sub_name + 'Post')
            logging.info((sub_name + 'Post'))
            
            aaa = request.form.get('isNight')
            date1 = request.form.get('date1')
            date2 = request.form.get('date2')
            if aaa is None:
                isNight = True
            elif aaa == 'Y':
                isNight = True
            else:
                isNight = False
            print(isNight)
            if date2 is None:
                date1 = today_mfg
                date2 = today_mfg
            
            isNight = False
            return ct1MachDiff(user,name, auth, shift,date1, date2,isNight)
        
        
        
        # PCS000 MOVE監測
        if request.form.get('pcsCheck') is not None:
            print('pcsCheck Post')
            table = 'pcs_check2'
            pcs_record = mysql2df(table)
            #pcs_check = mysql2df(table)
            date = request.form.get('pcsCheck_date')
            if date is None:
                date = today_mfg
            
            pcs_check = pd.DataFrame(columns=pcs_record.columns)
            #date_list = datesListStr(date1, date2)
            #print(date)
            for i in range(len(pcs_record)):
                if pcs_record.loc[i]['MFG_Date'] == date:
                    #print('yes')
                    pcs_check.loc[i] = pcs_record.loc[i]
            #print(pcs_check)
            
            #chart = pcs_check.iloc[:][:].plot(title='PCS Check per 15min',  #圖表標題
            #                                    xlabel='Time',  #x軸說明文字
            #                                    ylabel='Move',  #y軸說明文字
            #                                    legend=True,  # 是否顯示圖例
            #                                    figsize=(30, 10)# 圖表大小
            #                                    )  
            #plt.savefig('test.jpg')#儲存圖片
            
            if request.values['pcsCheck']=='download':
                pcs_check.reset_index(inplace=True)
                cols = list(pcs_check.columns)
                print(cols)
                for i in range(len(cols)):
                    if i >= 4:
                        
                        for idx in range(len(pcs_check)):
                            if pcs_check.loc[idx, cols[i]] == -1 :
                                pcs_check.loc[idx, cols[i]] = ''
                        cols[i] = cols[i][0:2] +':'+ cols[i][3:5]
                pcs_check.columns = cols
                pcs_check = pcs_check.drop(columns =['index','Date'])
                
                date = date[2:4]+date[5:7]+date[8:10]
                filepath = r'static/pcsCheck_'+date+'.csv'
                pcs_check.to_csv(filepath, index=False)
                file = 'pcsCheck_'+date+'.csv'
                #path = r'C:\Users\kjchen\craig\maint\210810\static'
                path = r'static'
               
                
                return send_from_directory(path, file, as_attachment=True)
                #return app.send_static_file(file)
            
            pcsCheck_date=date
            sectShow = 'pcsCheck'
            return render_template('userMain.html', user=str(user),name=name, auth=auth, shift=shift, sectShow=sectShow, pcs_check=pcs_check, pcsCheck_date=pcsCheck_date)

                        
        if request.form.get('ct1Summ2') is not None:
            print('ok')
            date1 = request.form.get('ct1Summ2_date1')
            
            date2 = request.form.get('ct1Summ2_date2')
            
            if date1 is None:
                #today = today0[0:4]+'/'+today0[4:6]+'/'+today0[6:8]
                date1 = today_mfg
                date2 = today_mfg
                

            return ct1Summ2(user,name, auth, shift, date1, date2)
        
        btnName = list(request.form)[-1]
        
        # ct1Summ2表格之第二層cHIPID列表觸發   主頁版
        if btnName[0:9] == 'ct1Summ__':
            #t0 = time.time()
            user = request.form.get('user')
            name = request.form.get('name')
            shift = request.form.get('shift')
            auth = request.form.get('auth')
            date1 = request.form.get('ct1Summ_date1')
            date2 = request.form.get('ct1Summ_date2')
            isGoHours = False
            go_hour = '00'
            sectShow = 'ct1_summ2_chipid'
            #now = datetime.datetime.now().strftime("%Y%m%d%H%M")
            
            logging.info("ct1良率第二層觸發,  "+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            
            
            '''
            # 簡稱對應表建立
            ABBR_DEFECT_NAMES = ['BP', 'V_O', 'V_L' , 'H_O', 'H_L', 'X_S', 'VOBL', 'H_BAND_MURA', 'W_S', 'B_S', 'AGM', 'OAD',
                                 'OAPD', 'OGD', 'DP_W', 'DPP_W', 'DP_CLUSTER', 'DP_ADJ', 'DP_NEAR', 'BPP', 'BP-PAIR', 'SBP_XW', 'CP']
            '''
            ABBR_DEFECT_NAMES = ['BP',    'V_O'   , 'V_L'   ,     'H_O', 'H_L',    'X_S'  ,  'VOBL'    ,  'H_BAND_MURA', 'W_S'       ,     'B_S',       'AGM'            , 'OAD'            , 'OAPD',            
                                            'OGD',    'DP_W', 'DPP_W', 'DP_CLUSTER', 'DP_ADJ'   , 'DP_NEAR', 'BPP'     , 'SBP_XW',   'CP',       'POINT_COUNT' ]
            
            WHOLE_DEFECT_NAMES = ['BP', 'V-OPEN', 'V-LINE' , 'H-OPEN', 'H-LINE', 'X-SHORT', 'V-OPEN-BL', 'H-BAND MURA', 'WHITE SPOT', 'BLACK SPOT', 'AROUND GAP MURA', 'OTHER ALIGN DEFECT', 'OTHER APPEAR DEFECT',
                                  'OTHER GLASS DEFECT', 'DP', 'DP-PAIR', 'DP-CLUSTER', '3DP-ADJ', 'DP-NEAR', 'BP-PAIR', 'SMALL BP', 'PD13 ',   'POINT-COUNT']   
            '''
            WHOLE_DEFECT_NAMES = ['BP', 'V-OPEN', 'V-LINE' , 'H-OPEN', 'H-LINE', 'X-SHORT', 'V-OPEN-BL', 'H_BAND_MURA', 'POINT-COUNT',
                                  'WHITE SPOT', 'BLACK SPOT', 'AROUND GAP MURA', 'OTHER ALIGN DEFECT', 'OTHER APPEAR DEFECT',
                                  'OTHER GLASS DEFECT', 'DP', 'DP-PAIR', 'DP-CLUSTER', '3DP-ADJ', 'DP-NEAR', 'BP-PAIR', 'SMALL BP', 
                                  'PD13', 'POINT-COUNT']   
            '''
            A2W_DEFECT_NAMES = {}
            for i in range(len(ABBR_DEFECT_NAMES)):
                A2W_DEFECT_NAMES[ABBR_DEFECT_NAMES[i]] = WHOLE_DEFECT_NAMES[i]
                
            # 補充包
            A2W_DEFECT_NAMES['AGM_X'] = 'AROUND GAP MURA'
            A2W_DEFECT_NAMES['AGM_Y'] = 'AROUND GAP MURA'
            #print(A2W_DEFECT_NAMES)
            
            
            if date1 is None:
                #today = today0[0:4]+'/'+today0[4:6]+'/'+today0[6:8]
                1
                #date1 = today_mfg
                #date2 = today_mfg
            
            
            #print('eumm__')
            #print(list(request.form)[-1])
            #print(str(request.form))
            #print(str(request.headers))
            aaa = btnName.split('__', 4)
            print(aaa)
            logging.info('傳入NAME為: '+btnName)
            print('傳入NAME為: '+btnName)
            date = aaa[1]
            #判斷是否為兩項
            if len(date) >= 15:
                print('ct1Summ__來自機差')
                bbb = date.split('+', 1)
                date1 = bbb[0]
                date2 = bbb[1]
                print(date1, date2)
            # 判斷是否為gohours來源
            elif len(date) >= 11:
                print('ct1Summ__來自GO HOURS')
                bbb = date.split('+', 1)
                date1 = bbb[0]
                date2 = date1
                go_hour = bbb[1]
                isGoHours = True
            # Yield Summary專用 修改
            elif date == 'ys':
                #print('Yield sUMMARY模式')
                date0 = date1
                date1 = date0[0:4]+'/'+date0[5:7]+'/'+date0[8:10]
                date0 = date2
                date2 = date0[0:4]+'/'+date0[5:7]+'/'+date0[8:10]
                # 保持原本的date1和date2
            else:
                date1 = date
                date2 = date
            
            model_no = aaa[2]
            eqp = aaa[3]
            # 假如沒有找到對應，直接使用原始名稱
            try:
                defect = A2W_DEFECT_NAMES[aaa[4]]
            except:
                defect = aaa[4]
            
            # 主頁最底下欄位專用
            if eqp == '總數':
                #defect = aaa[4]
                
                req_list = ['chk_'+aaa[4]]
                date1 = request.form.get('ct1Summ_date1')
                date2 = request.form.get('ct1Summ_date2')
                return ct1DefectImg(user,name, auth, shift, date1, date2, model_no, defect, eqp, isGoHours, go_hour)
            
                #return yieldSumm(user,name, auth, shift, date1, date2, req_list)
            
            
            return ct1DefectImg(user,name, auth, shift, date1, date2, model_no, defect, eqp, isGoHours, go_hour)
            
            
            
            
            
            print('  defect = '+defect)
            logging.info('  defect = '+defect)
            # 下載判圖記錄
            table = 'img_check_record'
            df_img_record = mysql2df(table)
            print('mysql2df(table) ok')
            logging.info('mysql2df -> '+table+'   ok!!')
            
            
            mysql = r"select t.tft_chip_id as chipid ,t.model_no, t.test_time, t.test_user, t.defect_code_desc,  t.test_signal_no as X ,t.test_gate_no as Y, t.pattern_code,t.img_file_path, t.img_file_name "
            mysql += r"from celods.h_dax_fbk_defect_ods t "
            mysql += r"where t.test_mfg_day between to_date('" +date1+ "','YYYY/mm/DD') and to_date('" +date2+ "','YYYY/mm/DD') "
            mysql += r"and t.test_op_id = 'CGL' "
            mysql += r"and t.model_no='" +model_no+ "' "
            mysql += r"and t.defect_code_desc='" +defect+ "' and t.test_user='" +eqp+ "' "
            if isGoHours:
                mysql += r"and to_char(t.test_time,'HH24')='" + go_hour + "' "
            mysql += r"order by t.test_time "
            
            
            mysql = r""
            mysql += r"select a.chipid, a.test_time, a.model_no, a.test_user, a.defect_code_desc, a.x, a.y, a.pattern_code, b.img_file_path, b.img_file_name "
            mysql += r"from ( "
            mysql += r"select t.tft_chip_id as chipid, t.test_time ,t.model_no, t.test_user, t.defect_code_desc, "
            mysql += r"max(t.test_signal_no) as x,max(t.test_gate_no) as y, t.pattern_code "
            mysql += r"from celods.h_dax_fbk_defect_ods t "
            mysql += r"where t.test_mfg_day between to_date('" +date1+ "','YYYY/mm/DD') and to_date('" +date2+ "','YYYY/mm/DD') " 
            mysql += r"and t.test_op_id = 'CGL' "
            mysql += r"and t.model_no='" +model_no+ "' " 
            mysql += r"and t.defect_code_desc in ('" +defect+ "') " 
            mysql += r"and t.test_user='" +eqp+ "' " 
            mysql += r"and t.major_defect_flag = 'Y' "
            mysql += r"and t.grade in ('W','X') " 
            mysql += r"and t.judge_flag = 'L' "
            if isGoHours:
                mysql += r"and to_char(t.test_time,'HH24')='" + go_hour + "' "
            mysql += r"group by t.tft_chip_id,t.test_time,t.model_no, t.test_user,t.defect_code_desc,t.pattern_code "
            mysql += r") a "
            mysql += r"Left Join ( "
            mysql += r"select t2.img_file_path, t2.img_file_name, t2.tft_chip_id as chipid, t2.test_signal_no as xx, t2.test_gate_no as yy "
            mysql += r"from celods.h_dax_fbk_defect_ods t2 "
            mysql += r"where t2.test_mfg_day between to_date('" +date1+ "','YYYY/mm/DD') and to_date('" +date2+ "','YYYY/mm/DD') " 
            mysql += r"and t2.test_op_id = 'CGL' " 
            mysql += r"and t2.model_no='" +model_no+ "' " 
            mysql += r"and t.defect_code_desc in ('" +defect+ "') " 
            mysql += r"and t2.test_user='" +eqp+ "' " 
            mysql += r"and t2.major_defect_flag = 'Y' "
            mysql += r"and t2.grade in ('W','X') " 
            mysql += r"and t2.judge_flag = 'L' "
            if isGoHours:
                mysql += r"and to_char(t.test_time,'HH24')='" + go_hour + "' "
            mysql += r") b on a.chipid=b.chipid and a.x=b.xx and a.y=b.yy "
      
            logging.info(mysql)
            try:
                ct1_summ2_chipid = ora2df(mysql)
            except:
                logging.info('<h1>ora2df失敗</h1>')
                return '<h1>ora2df失敗</h1>'
            pd.set_option('display.max_colwidth', None)
            #df_html = ct1_summ2.to_html()
            imgLinks = []
            
            #找圖ya
            for i in range(len(ct1_summ2_chipid)):
                list0 = []
                chipid = ct1_summ2_chipid.loc[i]['CHIPID']
                time00 = str(ct1_summ2_chipid.loc[i]['TEST_TIME'])[11:13]
                test_time_str = str(ct1_summ2_chipid.loc[i]['TEST_TIME'])
                test_date = test_time_str[0:4]+test_time_str[5:7]+test_time_str[8:10]
                ct1_summ2_chipid.loc[i, 'Check'] = 'N'
                defect = ct1_summ2_chipid.loc[i]['DEFECT_CODE_DESC']
                eqp = ct1_summ2_chipid.loc[i]['TEST_USER']
                pt = ct1_summ2_chipid.loc[i]['PATTERN_CODE']
                # IMG_FILE_PATH可能為 none
                try:
                    ora_imgpath = ct1_summ2_chipid.loc[i]['IMG_FILE_PATH']+ct1_summ2_chipid.loc[i]['IMG_FILE_NAME']
                except:
                    ora_imgpath = 'NNNNNNNNNNNNN'
                
                
                for ii in range(len(df_img_record)):
                    if chipid == df_img_record.loc[ii]['CHIPID']:
                        ct1_summ2_chipid.loc[i, 'Check'] = df_img_record.loc[ii]['imgCheck']
                        ct1_summ2_chipid.loc[i, 'Check_Name'] = df_img_record.loc[ii]['name']
                        #ct1_summ2_chipid.loc[i]['Remark'] = df_img_record.loc[ii]['Remark']
                
                # 超高速串圖  開發中
                if ora_imgpath[2:12] == '10.10.10.4':
                    print('高速找圖觸發: 10.10.10.4!!!!!')
                    logging.info('高速bp找圖觸發: 10.10.10.4!!!!!')
                    #aaa = r'\\10.10.10.4\AOI Data\Defect_Image\Sub3\20211004\12\Defect\C95M6CC_C3_PB48L_TBP_D5268_G1941.bmp'
                    aa = ora_imgpath[21:]
                    imgPath = r'http://tcweb002.corpnet.auo.com/'+ eqp + r'/AOI%20Data'+aa
                    sub_num = int(aa[17])
                    print('sub_num='+aa[17])
                    logging.info('sub_num='+aa[17])
                    if sub_num not in [1,2,3]:
                        sub_num = 3
                #bbb = r'http://tcweb002.corpnet.auo.com/CCCGL1082/AOI%20Data/Defect_Image/Sub3/20211004/12/Defect/C95M6CC_C3_PB48L_TBP_D5268_G1941.bmp'
                    for sub in [1,2,3]:
                        if sub == sub_num:
                            list0.append(imgPath)
                        else:
                            list0.append(' ')
                    imgLinks.append(list0)
                    continue
    
                chipid_times = []
                if time00 == '00':
                    chipid_times = [time00]
                else:
                    chipid_times = [time00]#, str(int(time00)-1).zfill(2)]
                print(chipid_times)
                #判斷pattern code最後一字是否為數字時使用
                strlist_num = []
                for num in range(0,10):
                    strlist_num.append(str(num))
                
                WHOLE_DEFECT_NAMES = ['BP', 'V-OPEN', 'V-LINE' , 'H-OPEN', 'H-LINE', 'X-SHORT', 'V-OPEN-BL', 'H_BAND_MURA', 'POINT-COUNT'
                                  'WHITE SPOT', 'BLACK SPOT', 'AROUND GAP MURA', 'OTHER ALIGN DEFECT', 'OTHER APPEAR DEFECT',
                                  'OTHER GLASS DEFECT', 'DP', 'DP-PAIR', 'DP_CLUSTER', '3DP_ADJ', 'DP_NEAR', 'BP_PAIR', 'SMALL BP', 
                                  'PD13', 'POINT-COUNT']
                
                # BP (選BMP)http://tcweb002.corpnet.auo.com/CCCGL7082/AOI%20Data/Defect_Image/Sub3/20210908/08/Defect/
                # H-open http://tcweb002.corpnet.auo.com/CCCGL6082/AOI%20Data/Defect_Image/Sub1/20210908/08/Defect/C8CL3CC_C1_PWHITE_TDP_D10327_G4.bmp
                # V-LINE 疑似沒圖
                
                # v open http://tcweb002.corpnet.auo.com/CCCGL8082/AOI%20Data/Defect_Image/Sub2/20210908/07/Defect/
                subDefect_list = ['BP', 'H-OPEN', 'H-LINE', 'V-OPEN', 'V-LINE', 'X-SHORT', 'BP-PAIR']      
                ag_list = ['V-OPEN-BL', 'AROUND GAP MURA', 'WHITE SPOT', 'BLACK SPOT']
                
                
                if defect in subDefect_list:
                    logging.info('  '+chipid+', Pattern Code = '+str(subDefect_list))
                    list0 = subDefect(eqp, chipid, test_date, chipid_times)
                
                if defect in ag_list:
                    #http://tcweb002.corpnet.auo.com/CCCGL8082/AOI%20Data/Ori_Image/AreaGrabber1/20211024/07/Source/CAGX6ZF_C1_PM_LB_FMura_S1_WithDefect
                    #http://tcweb002.corpnet.auo.com/CCCGL8082/AOI%20Data/Ori_Image/AreaGrabber1/20211024/07/Source/CAGX6ZF_C1PM_LB_FMura_S1_WithDefect.bmp
                    print('ag_list找圖觸發')
                    AGs = ['AreaGrabber1/', 'AreaGrabber2/', 'AreaGrabber3/']
                    for ag in AGs:
                        ccd_num =int(ag[-2])
                        for time0 in chipid_times:
                            pathImgs = [r'http://tcweb002.corpnet.auo.com/',  eqp,
                                        r'/AOI%20Data/Ori_Image/',        ['AreaGrabber1/', 'AreaGrabber2/', 'AreaGrabber3/'],
                                        test_date,     time0,
                                        '/Source/']
                            
                            path0 = pathImgs[0]+pathImgs[1]+pathImgs[2]+ ag + pathImgs[4]+'/'+pathImgs[5]+pathImgs[6]
                            #print(path0)
                            # CAGX6ZF_C1_PM_LB_FMura_S1_WithDefect.bmp
                            img_path = path0 + chipid +'_C'+ ag[-2] + '_P'+ pt + '_FMura_S' + ag[-2] + '_WithDefect.bmp'
                            list0.append(img_path)
                                        #break
                        if len(list0) != ccd_num:
                            list0.append(' ')
                elif ct1_summ2_chipid.loc[i]['PATTERN_CODE'] is None:
                    list0.append(' ')
                    list0.append(' ')    
                    list0.append(' ')
                    #暫不找圖
                # L模式
                elif ct1_summ2_chipid.loc[i]['PATTERN_CODE'][0] == 'L':
                    logging.info('  '+chipid+', Pattern Code = L模式')
                    #print(chipid, eqp, date, time0)
                    
                    
                    #Sub1/20210808/20/OtherGlass/C7BZ6CE_C1_PWHITE.tif
                    #http://tcweb002.corpnet.auo.com/CCCGL3082/AOI%20Data/Defect_Image/Sub2/20210907/03/OtherGlass/C8B62GE_C2_PWHITE.tif
                    times = []
                    for j in range(11):
                       times.append(str(j).rjust(2,'0'))
                    
                    subs = ['Sub1/', 'Sub2/', 'Sub3/']
                    for sub in subs:
                        for time0 in chipid_times:
                            pathImgs = [r'http://tcweb002.corpnet.auo.com/',  eqp,
                                r'/AOI%20Data/Defect_Image/',        ['Sub1/', 'Sub2/', 'Sub3/'],
                                test_date,     time0,
                                '/OtherGlass/']
                            path0 = pathImgs[0]+pathImgs[1]+pathImgs[2]+ sub + pathImgs[4]+'/'+pathImgs[5]+pathImgs[6]
                            #print(path0)
                            imgs_list = AUOFab_PathList(path0)[1]
                            #print(imgs_list)
                                #print(imgs_list)
                            for img in imgs_list:
                                if img[0:7] == chipid:
                                    print(path0+img)
                                    logging.info('  找到chipid image:'+img)
                                    list0.append(path0+img)
                                    #break
                        if len(list0) != int(sub[-2]):
                            list0.append(' ')
                        
                # M模式
                #http://tcweb002.corpnet.auo.com/CCCGL1082/AOI%20Data/Ori_Image/AreaGrabber2/20210903/08/Source/C85T3YE_C2_PM_R_FMura_S2_WithDefect.bmp


                # 有一特例: OGD  先判斷是否為OGD
                elif ct1_summ2_chipid.loc[i]['DEFECT_CODE_DESC'] == 'OTHER GLASS DEFECT' and ct1_summ2_chipid.loc[i]['PATTERN_CODE'][0] == 'M':    
                    logging.info('  '+chipid+', Pattern Code = OGD+M模式')
                    print('OGD特殊狀況進入')
                    
                    times = []
                    for j in range(11):
                       times.append(str(j).rjust(2,'0'))
                    
                    AGs = ['AreaGrabber1/', 'AreaGrabber2/', 'AreaGrabber3/']
                    for ag in AGs:
                        for time0 in chipid_times:
                            pathImgs = [r'http://tcweb002.corpnet.auo.com/',  eqp,
                                        r'/AOI%20Data/Defect_Image/',        ['AreaGrabber1/', 'AreaGrabber2/', 'AreaGrabber3/'],
                                        test_date,     time0,
                                        '/Source/']
                        
                        
                            path0 = pathImgs[0]+pathImgs[1]+pathImgs[2]+ ag + pathImgs[4]+'/'+pathImgs[5]+pathImgs[6]
                            #print(path0)
                            imgs_list = AUOFab_PathList(path0)[1]
                            #print(imgs_list)
                                #print(imgs_list)
                            for img in imgs_list:
                                if img[0:7] == chipid:
                                    #print(path0+img)
                                    
                                    aaa = img.split('_', 4)
                                    pc = ct1_summ2_chipid.loc[i]['PATTERN_CODE']
                                    ptn_code = aaa[2][1:]+'_'+aaa[3]   
                                    if pc[-1] in strlist_num:
                                        pc = pc[:-1]
                                    print(ptn_code, pc)
                                    logging.info('  找到chipid image:'+img+', '+ptn_code+' =? '+pc)
                                    # 需為指定pattern code之影像
                                    if pc == ptn_code:
                                        list0.append(path0+img)
                                        #break
                        if len(list0) != int(ag[-2]):
                            list0.append(' ')


                elif ct1_summ2_chipid.loc[i]['PATTERN_CODE'][0] == 'M':
                    logging.info('  '+chipid+', Pattern Code = M模式')
                    
                    
                    
                    # 有一特例: OGD  先判斷是否為OGD
                   
                        
                    times = []
                    for j in range(11):
                       times.append(str(j).rjust(2,'0'))
                    
                    
                    AGs = ['AreaGrabber1/', 'AreaGrabber2/', 'AreaGrabber3/']
                    for ag in AGs:
                        
                        for time0 in chipid_times:
                            pathImgs = [r'http://tcweb002.corpnet.auo.com/',  eqp,
                                        r'/AOI%20Data/Ori_Image/',        ['AreaGrabber1/', 'AreaGrabber2/', 'AreaGrabber3/'],
                                        test_date,     time0,
                                        '/Source/']
                            path0 = pathImgs[0]+pathImgs[1]+pathImgs[2]+ ag + pathImgs[4]+'/'+pathImgs[5]+pathImgs[6]
                            #print(path0)
                            imgs_list = AUOFab_PathList(path0)[1]
                            #print(imgs_list)

                            for img in imgs_list:
                                if img[0:7] == chipid:
                                    #print(img)
                                    #ex:img = C8AA8LA_C3_PM_G_FMura_S3_WithDefect.bmp
                                    aaa = img.split('_', 4)
                                    pc = ct1_summ2_chipid.loc[i]['PATTERN_CODE']
                                    ptn_code = aaa[2][1:]+'_'+aaa[3]   
                                    if pc[-1] in strlist_num:
                                        pc = pc[:-1]
                                    print(ptn_code, pc)
                                    logging.info('  找到chipid image:'+img+', '+ptn_code+' =? '+pc)
                                    # 需為指定pattern code之影像
                                    if pc == ptn_code:
                                        list0.append(path0+img)
                                        #break
                        if len(list0) != int(ag[-2]):
                            list0.append(' ')
                
                
                    
                    
                    
                # 寫錯  備用以後用
                #http://tcweb002.corpnet.auo.com/CCCGL2082/AOI%20Data/Defect_Image/AreaGrabber1/20210903/09/Source/C89B8PD_C1_PL32_FMura_S1_0.bmp
                elif ct1_summ2_chipid.loc[i]['PATTERN_CODE'][0] == 'M':
                    chipid = ct1_summ2_chipid.loc[i]['CHIPID']
                    time0 = str(ct1_summ2_chipid.loc[i]['TEST_TIME'])[11:13]
                    #print(chipid, eqp, date, time0)
                    for time0 in chipid_times:
                        pathImgs = [r'http://tcweb002.corpnet.auo.com/',  eqp,
                                    r'/AOI%20Data/Defect_Image/',        ['AreaGrabber1/', 'AreaGrabber2/', 'AreaGrabber3/'],
                                    date[0:4]+date[5:7]+date[8:10],     time0,
                                    '/Source/']
                        #Sub1/20210808/20/OtherGlass/C7BZ6CE_C1_PWHITE.tif
                        
                        times = []
                        for j in range(11):
                           times.append(str(i).rjust(2,'0'))
                        
                        
                        for ag in pathImgs[3]:
                            path0 = pathImgs[0]+pathImgs[1]+pathImgs[2]+ ag + pathImgs[4]+'/'+pathImgs[5]+pathImgs[6]
                            #print(path0)
                            imgs_list = AUOFab_PathList(path0)[1]
                            #print(imgs_list)
                            if i == 1:
                                print('第二項')
                                print(imgs_list)
                            for img in imgs_list:
                                if img[0:7] == chipid:
                                    print(path0+img)
                                    list0.append(path0+img)
                            if len(list0) != int(ag[-2]):
                                list0.append(' ')
                        
                else:
                    # 未在已知範圍   給三個空白
                    list0.append(' ')
                    list0.append(' ')    
                    list0.append(' ')    
                imgLinks.append(list0)
                    #print(imgLinks)
            
            #print(ct1_summ2_chipid)
            ct1_summ2_date12 = [date1, date2]
            #t1 = time.time()
            #logging.info('找圖花費時間: '+str(t1-t0)[:6])
            return render_template('userMain.html', user=str(user),name=name, auth=auth, shift=shift, sectShow=sectShow, ct1_summ2_chipid=ct1_summ2_chipid, ct1_summ2_date12=ct1_summ2_date12, imgLinks=imgLinks)

        # ct1　看圖後上傳紀錄
        if request.form.get('imgCheckUpload') is not None:
            logging.info('判圖記錄上傳中...(imgCheckUpload)')
            #print(request.form)
            print(list(request.form))
            req_list = list(request.form)[:-1] #-1為submit按鈕
            #df_img_record = pd.DataFrame()
            start_time = request.form.get('now0')
            now_dt = datetime.datetime.now()
            end_time = now_dt.strftime("%Y-%m-%d %H:%M:%S")
            
            table = 'img_check_record'
            db_record = mysql2df(table)
            print('mysql2df(table) ok')
            logging.info('mysql2df(table)    ok!!')
            
            
            df_img_record = pd.DataFrame(columns=db_record.columns)
            
            
            cols = df_img_record.columns
            newIdx = 0
            
            for item in req_list:
                req = request.form.get(item)
                
                # 第四項前的是身分資訊   無編號會進到EXCEPT
                try:
                    aaa = item.split('__',2)
                    col = aaa[0]
                    num = int(aaa[1])
                    
                except:
                    continue
                if col in cols:
                    df_img_record.loc[num, col] = req
                
            # 個別補上個人資訊
            user_list = ['user', 'name', 'shift', 'auth']
            
                
            drops = []
            print(df_img_record['TEST_TIME'])
            for m in df_img_record.index:
                for ii in user_list:
                    req = request.form.get(ii)
                    df_img_record.loc[m, ii] = req
                if 'Checked_Date' in df_img_record.columns:
                    df_img_record.loc[m, 'Checked_Date'] = now2
                imgCheck = df_img_record.loc[m]['imgCheck']
                if imgCheck is None or pd.isna(imgCheck):
                    drops.append(m)
                    continue
                if 'TEST_TIME_MFG' in df_img_record.columns:
                # 新增MFG DATE轉換資訊
                    test_time = df_img_record.loc[m]['TEST_TIME']
                    #print(test_time)
                    df_img_record.loc[m,'TEST_TIME_MFG'] = testTime2MFG(str(test_time))
                    if imgCheck is None or pd.isna(imgCheck):
                        drops.append(m)
            
            df_img_record = df_img_record.drop(drops)
            df_img_record.reset_index(drop=True, inplace=True)
            print(df_img_record)
            df2mysql_app(df_img_record, table)
            logging.info('df2mysql(df_img_record, table)  ok!!')
            sectShow = 'uploadOK'
            
            if start_time is not None:
                check_defect = ""
                if len(df_img_record) > 0:
                    check_defect = "_" + str(df_img_record.loc[0]['DEFECT_CODE_DESC']) 
                dt0 = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
                spent_time = (now_dt - dt0).total_seconds()
                df_DL = pd.DataFrame()
                df_DL.loc[0, 'MODE'] = 'CT1_YS' + check_defect
                df_DL.loc[0, 'USER'] = str(user)+str(name)
                df_DL.loc[0, 'START_TIME'] = start_time
                df_DL.loc[0, 'END_TIME'] = end_time
                df_DL.loc[0, 'SPEND_TIME'] = spent_time
                df_DL.loc[0, 'CHIPID_COUNT'] = len(df_img_record)
                table = 'dl_time'
                print(df_DL)
                df2mysql_app(df_DL, table)
                
            btn_value = request.form.get('imgCheckUpload')
            if btn_value == 'ct1IDS':
                sub_name = 'ct1IDS'
                return ct1IDS(user,name, auth, shift,sub_name)
            
            
            return render_template('userMain.html', user=str(user),name=name, auth=auth, shift=shift, sectShow=sectShow)
        
         # ct1 ADC確認
        sub_name = 'ct1ADC'
        if request.form.get(sub_name) is not None:
            print(sub_name + 'Post')
            logging.info((sub_name + 'Post'))
            date1 = request.form.get(sub_name+'_date1')
            date2 = request.form.get(sub_name+'_date2')
            if request.form.get(sub_name) != '送出':
                date1 = today_mfg
                date2 = today_mfg
                
            return ct1ADC(user,name, auth, shift, date1, date2)
        
        
        
        sub_name = 'ct1ADCRaw__'
        # ct1 ADC確認 第二層
        if sub_name in btnName:
            print(sub_name + 'Post')
            logging.info((sub_name + 'Post'))
            
            date1 = request.form.get(sub_name+'_date1')
            date2 = request.form.get(sub_name+'_date2')
            
            
            spl = btnName.split('__', 6)
            logging.info('傳入NAME為: '+btnName)
            print('傳入NAME為: '+btnName)
            date1 = spl[1]
            date2 = spl[2]
            ct1_user = spl[3]
            pc = spl[4]
            
            return ct1ADCRaw(user,name, auth, shift, date1, date2, ct1_user, pc)
        
        
        sub_name = 'ct1ADC_Upload'
        # OCT ADC RB看圖後上傳紀錄
        if request.form.get(sub_name) is not None:
            logging.info('判圖記錄上傳中...(ct1ADC_Upload)')
            #print(request.form)
            req_list = list(request.form)[:-1] #-1為submit按鈕
            return ct1ADC_Upload(user,name, auth, shift, req_list)
        
        
        sub_name = 'ct1IDS'
        if request.form.get(sub_name) is not None:
            print(sub_name + 'Post')
            logging.info((sub_name + 'Post'))
            #date1 = request.form.get(sub_name+'_date1')
            #date2 = request.form.get(sub_name+'_date2')
            if request.form.get(sub_name) != '送出':
                1
                chipids = []
            return ct1IDS(user,name, auth, shift, sub_name)
        
        sub_name = 'ct1IDS'
        if request.form.get(sub_name) is not None:
            print(sub_name + 'Post')
            logging.info((sub_name + 'Post'))
            #date1 = request.form.get(sub_name+'_date1')
            #date2 = request.form.get(sub_name+'_date2')
            if request.form.get(sub_name) != '送出':
                1
                chipids = []
            return ct1IDS(user,name, auth, shift, sub_name)
        sub_names = ['ct1IDS', 'ct1AGMSearch', 'ct1JudgerArea']
        for sub_name in sub_names:
            if request.form.get(sub_name) is not None:
                print(sub_name + 'Post')
                logging.info((sub_name + 'Post'))
                #date1 = request.form.get(sub_name+'_date1')
                #date2 = request.form.get(sub_name+'_date2')
                if request.form.get(sub_name) != '送出':
                    1
                    chipids = []
                return ct1IDS(user,name, auth, shift, sub_name)
            
        if request.form.get('Status') is not None:
            print("表單觸發")
            mach_data = request.values['Status']
            data_list = mach_data.split('_', 2)
            class0 = data_list[0]
            mach0 = data_list[1]
            mode = data_list[2]
            user = request.form.get('user')
            name = request.form.get('name')
            shift = request.form.get('shift')
            auth = request.form.get('auth')
            logging.info('點檢燈號觸發: '+mach0+'; '+mode)
            print('點檢燈號觸發: '+mach0+'; '+auth+'; '+mode)
            time = today
            if class0 == 'LASER' and mode == 'Consum':
                table = 'nor_check'
                nor_check = mysql2df(table)
                for i in range(len(nor_check)):
                    eqp = nor_check.loc[i]['Machine']
                    if eqp == mach0:
                        consum_date = nor_check.loc[i]['Consum_Date']
                        return render_template('norCheckList.html', class0=class0, mach0=mach0, user=user, name=name, shift=shift, auth=auth,
                                   time=time, mode=mode, consum_date=consum_date)
            
            
           
                
            
            elif class0 in ['CT1'] and mode == 'CST_Linechange':
                table = 'nor_check'
                nor_check = mysql2df(table)
                for i in range(len(nor_check)):
                    eqp = nor_check.loc[i]['Machine']
                    if eqp == mach0:
                        model1 = nor_check.loc[i]['Model1']
                        model0 = nor_check.loc[i]['Model0']
                        return render_template('norCheckList.html', class0=class0, mach0=mach0, user=user, name=name, shift=shift, auth=auth,
                                   time=time, mode=mode, model0=model0, model1=model1)
            
            elif class0 in ['OCT'] and mode == 'CST_Linechange22222':
                check_list = ['CST_Check_ID01', 'CST_Check_ID02', 'CST_Check_ID03',
                              'CST_Check_ID04', 'CST_Check_ID05']
                csdID_list = []
                # 換線要5個cst 其他兩個['OCT502','OCT503', 'OCT602', 'OCT603', 'OCT702', 'OCT703']
            
                table = 'nor_check'
                nor_check = mysql2df(table)
                for i in nor_check.index:
                    eqp = nor_check.loc[i]['Machine']
                    if eqp == mach0:
                        for col in check_list:
                            csdID_list.append(nor_check.loc[i][col])
                        return render_template('norCheckList.html', class0=class0, mach0=mach0, user=user, name=name, shift=shift, auth=auth,
                                   time=time, mode=mode, csdID_list=csdID_list)
            elif class0 in ['OCT'] and mode in ['CST', 'CST_500', 'CST_Linechange']:
                check_list = ['CST_Check_ID01', 'CST_Check_ID02', 'CST_Check_ID03',
                              'CST_Check_ID04', 'CST_Check_ID05']
                table = 'nor_check'
                nor_check = mysql2df(table)
                cst_dir = {}
                df0 = nor_check[(nor_check['CST_Status'].isin(['R', 'RR'])) & (nor_check['Class'].isin(['OCT']))& (~nor_check['Machine'].isin(['COM100', 'SOT200']))]
                for idx0 in df0.index:
                    eqp0 = df0.loc[idx0]['Machine']
                    status0 = df0.loc[idx0]['CST_Status']
                    
                    
                    if status0 == 'RR' and eqp0 in ['OCT502','OCT503', 'OCT602', 'OCT603', 'OCT702', 'OCT703']:
                        cst_dir[eqp0] = 5
                        for col0 in check_list:
                            cst0 = df0.loc[idx0][col0] 
                            if cst0 != 'NNN':
                                cst_dir[eqp0] = cst_dir[eqp0] -1 
                    elif status0 == 'RR':
                        cst_dir[eqp0] = 2
                        for col0 in check_list[:2]:
                            cst0 = df0.loc[idx0][col0] 
                            if cst0 != 'NNN':
                                cst_dir[eqp0] = cst_dir[eqp0] -1
                    else:
                        cst_dir[eqp0] = 1
            
                    
                return render_template('norCheckList.html', class0=class0, mach0=mach0, user=user, name=name, shift=shift, auth=auth,
                                   time=time, mode=mode, cst_dir=cst_dir)
  
            else:
                return render_template('norCheckList.html', class0=class0, mach0=mach0, user=user, name=name, shift=shift, auth=auth,
                                   time=time, mode=mode)
            
            print('Light_Status觸發')
            
        
        # 點檢紀錄查詢
        if request.form.get('showNormalCheckRecord') is not None:
            
            date = request.form.get('showNormalCheckRecord_date')
            site = request.form.get('site')
            mode0 = request.form.get('mode')
            
            sectShow = 'showNormalCheckRecord'
            logging.info('點檢紀錄查詢系統('+sectShow+'): (date,site, mode)'+str(date)+str(site)+', '+str(mode0))
            print(site, mode0)
            if date is None:
                date = today_mfg
            if site is None:
                site = 0
                
            if mode0 is None:
                mode_idx = -1
                mode_key = 'NNNNNNNN'
            elif site in ['1', '2'] and mode0 == '點燈機點檢':
                mode_idx = [0,[1,2,3,4]]
                mode_key = 'Lig'
            elif site in ['1', '2'] and mode0 == 'CST點檢':
                mode_idx = [2,[1,2,3,4]]
                mode_key = 'CST'
            elif site == '1' and mode0 == 'Cold_Run':
                mode_idx = [1,[1,2,3,4]]
                mode_key = 'Cle'
            elif site == '2' and mode0 == '清潔點檢': 
                mode_idx = [1,[1,2,3,4]]
                mode_key = 'Cle'
            elif site == '2' and mode0 == '保養點檢': 
                mode_idx = [3,[1,2,3,4]]
                mode_key = 'Mai'
            elif site == '3' and mode0 == '清潔點檢': 
                mode_idx = [0,[1,2]]
                mode_key = 'Cle'
            elif site == '3' and mode0 == 'CST點檢': 
                mode_idx = [1,[1,2]]
                mode_key = 'CST'
            else:
                mode_idx = -2
                mode_key = 'NNNNNNNN'
            
            submit_list = [date, site, mode_idx]
            #print(submit_list)
            mode = []
            if site=='1':
                mode.append('CT1')
                table = 'ct1_check_record'
            elif site=='2':
                mode.append('OCT')
                table = 'check_record'
            elif site=='3':
                mode.append('LASER')
                table = 'lsr_check_record'
            else:
                mode.append('NN')
                mode.append('NN')
                table = 'check_record'
                check_record = pd.DataFrame()
                return render_template('userMain.html', user=str(user),name=name, auth=auth, shift=shift, today=today, sectShow=sectShow,check_record=check_record,mode=mode,submit_list=submit_list)
            
            none_list = ['NN', 'None']
            check_record0 = mysql2df(table)
            check_record = pd.DataFrame(columns=check_record0.columns)
            for i in range(len(check_record0)):
                # mode_key選擇指定點檢項目來過濾資料
                # 時間調整為mfg_day
                # try 防止日期格式異常者
                try:
                    db_time = check_record0.loc[i]['time'][11:13]+check_record0.loc[i]['time'][14:16]
                    db_date = check_record0.loc[i]['time'][0:10]
                    if int(db_time) < 730:
                        #print(check_record0.loc[i]['time'])
                        db_date_dt = datetime.datetime.strptime(db_date, "%Y-%m-%d")
                        db_mfgday = (db_date_dt+datetime.timedelta(-1)).strftime("%Y-%m-%d")
                    else:
                        db_mfgday = db_date
                except:
                    continue
                if db_mfgday == date and check_record0.loc[i]['Mode'][0:3] == mode_key:
                    
                    for j in list(check_record0.columns):
                        if (check_record0.loc[i][j] is None) or (check_record0.loc[i][j] in none_list):
                            check_record0.loc[i, j] = ' - '
                    check_record.loc[i] = check_record0.loc[i]
            
            if mode0 == '點燈機點檢':
                mode.append('Normal')
            elif str(mode0)[0:3] == 'CST':
                mode.append('CST')
            elif mode0 == 'Cold_Run':
                mode.append('Cold_Run')
            elif mode0 == '清潔點檢':
                mode.append('Clear')
            elif mode0 == '保養點檢':
                mode.append('Maint')
            elif mode0 == '耗材更換警示':
                mode.append('Consum')
            else:
                mode.append('NN')
            print(mode)
            
            return render_template('userMain.html', user=str(user),name=name, auth=auth, shift=shift, today=today, sectShow=sectShow,check_record=check_record,mode=mode, submit_list=submit_list)


            # 點檢紀錄查詢2
        if request.form.get('showNormalCheckRecord2') is not None:
            
            date1 = request.form.get('showNormalCheckRecord2_date1')
            date2 = request.form.get('showNormalCheckRecord2_date2')
            site = request.form.get('site')
            eqp = request.form.get('eqp')
            sectShow = 'showNormalCheckRecord2'
            logging.info('點檢紀錄查詢系統('+sectShow+'): (dat1+2,eqp)'+str(date1)+', '+str(date2)+', '+str(eqp))
            
            
            
            if date1 is None or date2 is None:
                date1 = today_mfg
                date2 = today_mfg
            
            if site is None:
                site = 0
            if eqp is None:
                eqp = 0
            
            
            submit_list2 = [date1, date2, site, eqp]
            
            if date1 is None or date2 is None:
                date_list = []
            else:
                date_list = datesListStr(date1, date2)
            mode = []
            if site=='1':
                mode.append('CT1')
                table = 'ct1_check_record'
            elif site=='2':
                mode.append('OCT')
                table = 'check_record'
            elif site=='3':
                mode.append('LASER')
                table = 'lsr_check_record'
            else:
                mode.append('NN')
                mode.append('NN')
                table = 'check_record'
                check_record = pd.DataFrame()
                return render_template('userMain.html', user=str(user),name=name, auth=auth, shift=shift, today=today, sectShow=sectShow,check_record=check_record,mode=mode, submit_list2=submit_list2)
             
            none_list = ['NN', 'None']
            check_record0 = mysql2df(table)
            check_record_Light = pd.DataFrame(columns=check_record0.columns)
            check_record_Clear = pd.DataFrame(columns=check_record0.columns)
            check_record_CST = pd.DataFrame(columns=check_record0.columns)
            check_record_Maint = pd.DataFrame(columns=check_record0.columns)
            Light_idx = 0
            Clear_idx = 0
            CST_idx = 0
            Maint_idx = 0
            for i in range(len(check_record0)):
                
                # 時間調整為mfg_day
                # try 防止日期格式異常者
                try:
                    db_time = check_record0.loc[i]['time'][11:13]+check_record0.loc[i]['time'][14:16]
                    db_date = check_record0.loc[i]['time'][0:10]
                    if int(db_time) < 730:
                        print(check_record0.loc[i]['time'])
                        db_date_dt = datetime.datetime.strptime(db_date, "%Y-%m-%d")
                        db_mfgday = (db_date_dt+datetime.timedelta(-1)).strftime("%Y-%m-%d")
                    else:
                        db_mfgday = db_date
                except:
                    continue
                
                
                
                if db_mfgday in date_list and check_record0.loc[i]['Machine'] == eqp:
                    for j in list(check_record0.columns):
                        if (check_record0.loc[i][j] is None) or (check_record0.loc[i][j] in none_list):
                            check_record0.loc[i, j] = ' - '
                    if check_record0.loc[i]['Mode'][0:5] == 'Light':
                        check_record_Light.loc[Light_idx] = check_record0.loc[i]
                        Light_idx += 1
                    elif check_record0.loc[i]['Mode'][0:5] == 'Clear':
                        check_record_Clear.loc[Clear_idx] = check_record0.loc[i]
                        Clear_idx += 1
                    elif check_record0.loc[i]['Mode'][0:3] == 'CST':
                        check_record_CST.loc[CST_idx] = check_record0.loc[i]
                        CST_idx += 1
                    elif check_record0.loc[i]['Mode'][0:5] == 'Maint':
                        check_record_Maint.loc[Maint_idx] = check_record0.loc[i]
                        Maint_idx += 1
            print(check_record_Light)
       
            return render_template('userMain.html', user=str(user),name=name, auth=auth, shift=shift, sectShow=sectShow,check_record_Light=check_record_Light, check_record_Clear=check_record_Clear, check_record_CST=check_record_CST, check_record_Maint = check_record_Maint, mode=mode,submit_list2=submit_list2)

        
        #點檢表單送出
        if request.form.get('CheckBtn') is not None:
            
            name = request.form.get('Name')
            mach = request.form.get('Machine')
            user = request.form.get('User')
            mode = request.form.get('Mode')
            shift = request.form.get('Shift')
            auth = request.form.get('Auth')
            class0 = request.form.get('Class')
            # 不需加入資料庫的項目
            req_excepts = []
            # 判斷是否改綠燈
            isG = True
            isLineChange = False
            # 檢查是否為換線mode
            mode2 = mode
            #暫解 日後改
            if class0 == 'CT1' and mode2 == 'Clear_Linechange':
                mode2 = 'Cold Run'
            
            # CST_500一樣會變成"CST" ，上傳資料為全部req 所以記錄一樣會是cst500
            aaa = mode.split('_', 1)
            if len(aaa) != 1: 
                mode = aaa[0]
                isLineChange = True
            
            table = "nor_check"
            nor_check = mysql2df(table)
            machIdx = nor_check.index[nor_check['Machine'] == mach]
            need_list = ['Date', 'Class', 'User', 'Name','Mode']
            logging.info('點檢表單送出中...(('+mach+'; '+mode)
            
            # if 換線燈  清空CST數量 (>500 -> 0)
            if class0 in ('CT1', 'LASER') and mode in ['CST']:
                nor_check.loc[machIdx, mode+'_Count'] = 0
                print('    已清空CST_Count, '+nor_check.loc[machIdx]['Machine'])
            #舊有的CST點檢  目前針對com100 sot200
            elif class0 in ('OCT') and mode in ['CST'] and mach in ['COM100', 'SOT200']:
                nor_check.loc[machIdx, 'CST_Count'] = 0
                print('    已清空CST_Count, '+nor_check.loc[machIdx]['Machine'])
                
                
                
            if class0 == 'CT1':
                table = 'ct1_check_record'
                db_data = mysql2df(table)
                check_record = pd.DataFrame(columns=db_data.columns)
            elif class0 == 'OCT':
                # 下載oct點檢紀錄
                table = 'check_record'
                db_data = mysql2df(table)
                check_record = pd.DataFrame(columns=db_data.columns)
                if type(check_record) == 'str':
                    return '<h1>'+ table +'下載失敗，請回上一頁並重新進入</h1>'
                newIdx = len(check_record)
                
            elif class0 == 'LASER':
                table = 'lsr_check_record' 
                db_data = mysql2df(table)
                check_record = pd.DataFrame(columns=db_data.columns)
                #lsr_check_record = pd.DataFrame()
                #check_record = lsr_check_record
            
            
            newIdx = len(check_record)
            columns = check_record.columns
            print('request.values[CheckBtn] => ',request.values['CheckBtn'])
             #　未Ｒｕｎ貨 改黃燈
            if request.values['CheckBtn']=='notRun':
                print('  未Run貨送出中...')
                
                for item in columns:
                    if item in need_list:
                        ans = request.form.get(item)
                        if ans is not None and item in check_record.columns:
                            check_record.loc[newIdx, item] = ans
                        if item == 'Mode':
                            check_record.loc[newIdx, item] = mode2+'_notRun'
                    else:
                        check_record.loc[newIdx, item] = 'NN'
                if 'NOT_RUN_MODEL' in check_record.columns:
                    check_record.loc[newIdx, 'NOT_RUN_MODEL'] = 'Y'
                
                print(check_record.columns)
                nor_check.loc[machIdx, mode+'_Status'] = 'YY'
                
                if mode == 'CST':
                    nor_check.loc[machIdx, mode+'_Count'] = 0
                nor_check.loc[machIdx, mode+'_Person'] = str(user)+name
                nor_check.loc[machIdx, mode+'_Update'] = now2
                
                
                

                df2mysql_app(check_record, table)
                
                
                table = 'nor_check'
                aaa = df2mysql(nor_check, table)
                
                sectShow = 'showNorCheck'
                site = class0
                return render_template('userMain.html', user=str(user),name=name, auth=auth, shift=shift, nor_check=nor_check, sectShow=sectShow, site=site)
            
            #oct　ＣＳＴ改版
            elif class0 in ['OCT'] and mode == 'CST' and mach not in ['COM100', 'SOT200']:
                print('OCT CST點檢2版觸發')
                # 不處理點選的機檯燈號
                isG = False
                need_col = ['CST_Check_ID01','CST_Check_ID01_OK', 'CST_Check_rem', 'Machine','time']
                check_list = ['CST_Check_ID01', 'CST_Check_ID02', 'CST_Check_ID03',
                              'CST_Check_ID04', 'CST_Check_ID05']
                req_list = list(request.form)
                for item in req_list:
                    if '__' in item:
                        val0 = request.form.get(item)
                        spl0 = item.split('__')
                        try:
                            col0 = spl0[0]
                            idx0 = int(spl0[1])
                        except:
                            continue
                        check_record.loc[idx0, col0] = val0
                check_record = check_record[check_record['CST_Check_ID01'].str.len() == 6].copy()
                
                check_record.reset_index(drop=True, inplace=True)
                for col0 in ['Name', 'User', 'Shift', 'Auth', 'Mode']:
                    print(col0)
                    val0 = request.form.get(col0)
                    check_record[col0] = val0
                check_record['time'] = now2
                print(check_record[need_col])
                # 紅燈項目
                cst_dir = {}
                df_redcst = nor_check[(nor_check['CST_Status'].isin(['R', 'RR'])) & (nor_check['Class'].isin(['OCT'])) & (~nor_check['Machine'].isin(['COM100', 'SOT200']))]
                for idx0 in df_redcst.index:
                    eqp0 = df_redcst.loc[idx0]['Machine']
                    status0 = df_redcst.loc[idx0]['CST_Status']
                    if status0 == 'RR' and eqp0 in ['OCT502','OCT503', 'OCT602', 'OCT603', 'OCT702', 'OCT703']:
                        cst_dir[eqp0] = 5
                        for col0 in check_list:
                            cst0 = df_redcst.loc[idx0][col0] 
                            if cst0 != 'NNN':
                                cst_dir[eqp0] = cst_dir[eqp0] -1 
                    elif status0 == 'RR':
                        cst_dir[eqp0] = 2
                        for col0 in check_list[:2]:
                            cst0 = df_redcst.loc[idx0][col0] 
                            if cst0 != 'NNN':
                                cst_dir[eqp0] = cst_dir[eqp0] -1
                        if cst_dir[eqp0] <= 0:
                            cst_dir.pop(eqp0, True)
                        
                    else:
                        cst_dir[eqp0] = 1
                
                
                ok_eqps = []
                filter0 = check_record['Machine'].str.contains(',')
                # 優先處理只有一項的EQP
                df0 = check_record[~filter0]
                for idx0 in df0.index:
                    eqp0 = df0.loc[idx0]['Machine']
                    csd0 = df0.loc[idx0]['CST_Check_ID01']
                    print(csd0, '命中唯一', eqp0)
                    if eqp0 in cst_dir.keys():
                        print('   ...紅燈對中!!', csd0, eqp0)
                        
                        cst_dir[eqp0] = cst_dir[eqp0] - 1
                        eqp0_idx = nor_check[(nor_check['Machine'] == eqp0)].index[-1]
                        if cst_dir[eqp0] <= 0:
                            cst_dir.pop(eqp0, True)
                            #ok_eqps.append(eqp0)
                            # 清除已有項目 全改為NNN
                            for col0 in check_list:
                                nor_check.loc[eqp0_idx, col0] = 'NNN'
                                
                            # 改為綠燈
                            print('   ...',eqp0, '改為綠燈')
                            nor_check.loc[eqp0_idx, mode2 + '_Status'] = 'G'
                            nor_check.loc[eqp0_idx, mode2 + '_Count'] = 0
                        else:
                            # 註記已有項目
                            for col0 in check_list:
                                if nor_check.loc[eqp0_idx][col0] == 'NNN':
                                    nor_check.loc[eqp0_idx, col0] = csd0
                                    break
                
                # 兩種以上可能的EQP
                df0 = check_record[filter0]
                for idx0 in df0.index:
                    eqps0 = df0.loc[idx0]['Machine']
                    csd0 = df0.loc[idx0]['CST_Check_ID01']
                    spl0 = eqps0.split(', ')
                    print(spl0)
                    #從最後一項開始比對
                    for num0 in range(len(spl0)-1, -1, -1):
                        eqp0 = spl0[num0]
                        print(csd0, '命中', eqp0)
                        if eqp0 in cst_dir.keys():
                            print('   ...紅燈對中!!', csd0, eqp0)
                            # 修正多個可能機台   改為一項
                            #check_record.loc[idx0, 'Machine'] = eqp0
                            
                            cst_dir[eqp0] = cst_dir[eqp0] - 1
                            eqp0_idx = (nor_check['Machine'] == eqp0)
                            if cst_dir[eqp0] <= 0:
                                cst_dir.pop(eqp0, True)
                                
                            
                                #ok_eqps.append(eqp0)
                                # 清除已有項目 全改為NNN
                                for col0 in check_list:
                                    nor_check.loc[eqp0_idx, col0] = 'NNN'
                                
                                # 改為綠燈  片數歸0
                                nor_check.loc[eqp0_idx, mode2 + '_Status'] = 'G'
                                nor_check.loc[eqp0_idx, mode2 + '_Count'] = 0
                                print('   ...',eqp0, '改為綠燈')
                            else:
                                # 註記已有項目
                                for col0 in check_list:
                                    if nor_check.loc[eqp0_idx][col0] == 'NNN':
                                        nor_check.loc[eqp0_idx, col0] = csd0
                            #命中一個後跳過
                            break       
                        
                # 都沒對中時 刪除記錄
                1
                                    
            #oct　ＣＳＴ換線以特例處理(因上if改版而取消失)
            elif class0 in ['OCT'] and mode2 == 'CST_Linechange':
                print('OCT CST換線觸發')
                
                req_list = list(request.form)[:-1]
                check_list = ['CST_Check_ID01', 'CST_Check_ID02', 'CST_Check_ID03',
                              'CST_Check_ID04', 'CST_Check_ID05']
                for item in req_list:
                    req = request.form.get(item)
                    if item in check_record.columns:
                        check_record.loc[newIdx, item] = req
                    #　檢查新or舊cst
                    if item in check_list:
                        if req == "":
                            isG = False
                        else:
                            nor_check.loc[machIdx, item] = req
                # 已完成點檢 清空id紀錄
                if isG:
                    for item in check_list:
                        if item in check_record.columns:
                            nor_check.loc[machIdx, item] = 'NNN'
                    # 更正完整時間
                if 'time' in check_record.columns:
                    check_record.loc[newIdx, 'time'] = now2
            #ＣＴ１　ＣＳＴ換線以特例處理
            elif class0 in ['CT1'] and mode2 == 'CST_Linechange':
                print('ct1 cst換線觸發')
                req_list = list(request.form)[:-1]
                check_list = ['CST_LC02_46B2', 'CST_LC03_46F3', 'CST_LC04_46F4',
                              'CST_LC05_01B5', 'CST_LC06_01B6', 'CST_LC07_01F7',
                              'CST_LC08_01F8']
                df_tmp = pd.DataFrame()
                body = '<h1>'+user+name+' 觸發CT1 CST點檢(換線)長度有誤</h1><br/>'
                cst_type = request.form.get('CST_Type')
                if cst_type == 'old':
                    min_length = 13
                    max_length = 18
                    
                elif cst_type == 'new':
                    min_length = 23
                    max_length = 28
                isAlarm = False
                for item in req_list:
                    if item in check_record.columns:
                        req = request.form.get(item)
                        check_record.loc[newIdx, item] = req
                        
                    #　檢查新or舊cst
                    if item in check_list and item in check_record.columns:
                        # 更新-157的值
                        rail_length = float(req) - 157
                        check_record.loc[newIdx, item] = rail_length
                        
                        if rail_length < 7:
                            isG = False
                            isAlarm = True
                            #df_tmp.loc[1,'CST_Type'] = cst_type
                            df_tmp.loc[0, '長度標準'] = '大於7'
                            df_tmp.loc[0, item[-4:]] = rail_length
                        

                    elif item in ['CST_LC09_PanelBone']:
                        rail_length = float(req)
                        if rail_length >= min_length and rail_length <= max_length:
                            print('length ok')
                            df_tmp.loc[1, 'Panel離CST左右魚骨'] = rail_length
                            df_tmp.loc[1,'CST_Type'] = cst_type
                            df_tmp.loc[1, '長度標準'] = '介於 '+str([min_length, max_length])
                        
                        
                if isAlarm:
                    file = []
                    body += df_tmp.to_html()
                    body += '<br/> <br/>'
                    #receiver = 'Craig.Hsiao@auo.com;'+'Alex.XC.Pan@auo.com;'+'KJ.Chen@auo.com;'
                    receiver = 'Alex.XC.Pan@auo.com;'+'Yida.Tsai@auo.com;'+ 'Calvin.Wang@auo.com;'+ 'Roger.CH.Hsu@auo.com;'+ 'Jh.Hsu@auo.com;'+'Craig.Hsiao@auo.com;'+'KJ.Chen@auo.com;'
                    cc = 'Craig.Hsiao@auo.com;'
                    subject = '[L7AC2 Alarm] CT1 CST點檢 長度異常'
                    outlook(receiver,cc,body,subject,file)
                    
                # 更正完整時間
                if 'time' in check_record.columns:
                    check_record.loc[newIdx, 'time'] = now2
            
            
            #　OCT CST_500表單送出
            elif class0 in ['OCT'] and mode2 in ['CST_500']:
                newIdx = 0
                for item in columns:
                    ans = request.form.get(item)
                    #remName = item+'_rem'
                    if ans is not None and item in check_record.columns:
                        check_record.loc[newIdx, item] = ans
                        #print(item, ans)
                    else:
                        1
                        #check_record.loc[newIdx, item] = 'NN'
                        #print(item, ans)
                check_record.loc[newIdx, 'time'] = now2
                isG = True
            
            
            
            # 備品點檢
            elif class0 in ['CT1', 'LASER', 'OCT']:
                req_list = list(request.form)[:-1]
                ok_names = ['Consum_LSRstopper', 'Consum_LSRalignment', 'Consum_TOUclamp', 
                         'Consum_TOUstopper', 'Consum_TOUpositionY', 'Consum_CVclamp',
                         'Consum_Exitalignment']
                for item in req_list:
                    if item in check_record.columns:
                        req = request.form.get(item)
                        if item in ok_names and req == 'NG':
                            isG = False
                        check_record.loc[newIdx, item] = req
                # 更正完整時間
                if 'time' in check_record.columns:
                    check_record.loc[newIdx, 'time'] = now2
                
           
            
            
            
            
            
            # 修正nor_check資料庫中的更新人員
            
            moDef = int(now[8:10])-10
            nightDef = int(now[8:10])-22
            
            # LASER為超過下午三點黃燈 其他為上下午10點
            if isG:
                nor_check.loc[machIdx, mode+'_Person'] = str(user)+name
                nor_check.loc[machIdx, mode+'_Update'] = now2
                if class0 == 'LASER' and mode == 'Consum':
                    nor_check.loc[machIdx, mode+'_Status'] = 'G'
                    consum_date = request.form.get('Consum_Date')
                    nor_check.loc[machIdx, mode+'_Date'] = consum_date
                
                elif mode == 'Consum':
                    nor_check.loc[machIdx, mode+'_Status'] = 'G'
                
                elif class0 == 'LASER':
                    if int(now[8:10]) < 15:
                        nor_check.loc[machIdx, mode+'_Status'] = 'G'
                    else:
                        nor_check.loc[machIdx, mode+'_Status'] = 'Y'
                    
                elif abs(moDef) <= abs(nightDef):
                    if moDef < 0:
                        nor_check.loc[machIdx, mode+'_Status'] = 'G'
                    else:
                        nor_check.loc[machIdx, mode+'_Status'] = 'Y'
                else:
                    if nightDef < 0:
                        nor_check.loc[machIdx, mode+'_Status'] = 'G'
                    else:
                        nor_check.loc[machIdx, mode+'_Status'] = 'Y'
                

            #上傳資料庫
            if class0 == 'CT1':    
                table = 'ct1_check_record'
            elif class0 == 'OCT':
                table = 'check_record'
            elif class0 == 'LASER':
                table = 'lsr_check_record'
                
            if 1:#class0 == 'OCT':
                df2mysql_app(check_record, table)
            else:
                1
                #aaa = df2mysql(check_record, table)
           
            table = 'nor_check'
            aaa = df2mysql(nor_check, table)
            
            
            sectShow = 'showNorCheck'
            site = class0
            return render_template('userMain.html', user=str(user),name=name, auth=auth, shift=shift, nor_check=nor_check, sectShow=sectShow, site=site)
        
        
        
        
        #  OCT系統特區 
        
        # OCT OLD Monitor
        sub_name = 'octOLD'
        if request.form.get(sub_name) is not None:
            print(sub_name + 'Post')
            logging.info((sub_name + 'Post'))
            date1 = request.form.get(sub_name+'_date1')
            date2 = request.form.get(sub_name+'_date2')
            old_shift = request.form.get(sub_name+'_shift')
            print(old_shift)
            if date1 is None:
                date1 = today
                date2 = today
                old_shift = 'All'
            return octf.octOLD(user,name, auth, shift, date1, date2, old_shift)
        
        # OCT PAD Monitor
        sub_name = 'octPADCOR'
        if request.form.get(sub_name) is not None:
            print(sub_name + 'Post')
            logging.info((sub_name + 'Post'))
            date1 = request.form.get(sub_name+'_date1')
            date2 = request.form.get(sub_name+'_date2')
            old_shift = request.form.get(sub_name+'_shift')
            print(old_shift)
            if date1 is None:
                date1 = today
                date2 = today
            old_shift = 'All'
            return octf.octPADCOR(user,name, auth, shift, date1, date2)
        
        # OCT OGD Monitor
        sub_name = 'octOGD'
        if request.form.get(sub_name) is not None:
            print(sub_name + 'Post')
            logging.info((sub_name + 'Post'))
            date1 = request.form.get(sub_name+'_date1')
            date2 = request.form.get(sub_name+'_date2')
            sql_shift = request.form.get(sub_name+'_shift')
            chk = request.form.get(sub_name+'_chk')
            oct_def = 'OTHER GLASS DEFECT'
            isCT1data = False
            
            if chk == 'Y':
                isCT1data = True
            
            if date1 is None:
                date1 = today
                date2 = today
                sql_shift = 'All'
            return octf.octOGDOAD(user,name, auth, shift, date1, date2, sql_shift, oct_def, isCT1data)
        
        
        # OCT OAPD Monitor
        sub_name = 'octOAPD'
        if request.form.get(sub_name) is not None:
            print(sub_name + 'Post')
            logging.info((sub_name + 'Post'))
            date1 = request.form.get(sub_name+'_date1')
            date2 = request.form.get(sub_name+'_date2')
            sql_shift = request.form.get(sub_name+'_shift')
            chk = request.form.get(sub_name+'_chk')
            oct_def = 'OTHER APPEAR DEFECT'
            isCT1data = False
            
            if chk == 'Y':
                isCT1data = True

            if date1 is None:
                date1 = today
                date2 = today
                sql_shift = 'All'
            return octf.octOGDOAD(user,name, auth, shift, date1, date2, sql_shift, oct_def, isCT1data)
        
        # OCT AD Monitor
        sub_name = 'octAD'
        if request.form.get(sub_name) is not None:
            print(sub_name + 'Post')
            logging.info((sub_name + 'Post'))
            date1 = request.form.get(sub_name+'_date1')
            date2 = request.form.get(sub_name+'_date2')
            sql_shift = request.form.get(sub_name+'_shift')
            chk = request.form.get(sub_name+'_chk')
            oct_def = 'ABNORMAL DISPLAY'
            isCT1data = False
            
            if chk == 'Y':
                isCT1data = True

            if date1 is None:
                date1 = today
                date2 = today
                sql_shift = 'All'
            return octf.octOGDOAD(user,name, auth, shift, date1, date2, sql_shift, oct_def, isCT1data)
        
        # OCT DP2BP
        sub_name = 'octDP2BP'
        if request.form.get(sub_name) is not None:
            print(sub_name + 'Post')
            logging.info((sub_name + 'Post'))
            date1 = request.form.get(sub_name+'_date1')
            date2 = request.form.get(sub_name+'_date2')

            if request.form.get(sub_name) != '送出':
                date1 = today
                date2 = today
                sql_shift = 'All'
            return octf.octDP2BP(user,name, auth, shift, date1, date2)
        
        
        
        
        sub_name = 'octDP2BPRaw__'
        # OCT DP2BP第二層
        if btnName[0:13] == sub_name:
            print(sub_name + 'Post')
            logging.info((sub_name + 'Post'))
            sub_name = 'octDP2BP'
            date1 = request.form.get(sub_name+'_date1')
            date2 = request.form.get(sub_name+'_date2')
            
            
            spl = btnName.split('__', 6)
            logging.info('傳入NAME為: '+btnName)
            print('傳入NAME為: '+btnName)
            
            tool_id = spl[1]
            pc = spl[2]
            
            return octf.octDP2BPRaw(user,name, auth, shift, date1, date2, tool_id, pc)
        
         # OCT DP2BP上傳紀錄
        if request.form.get('octDP2BP_Upload') is not None:
            logging.info('octDP2BP_Upload上傳中...')
            print('octDP2BP_Upload上傳中...')
            #print(request.form)
            req_list = list(request.form)[:-1] #-1為submit按鈕
            
            return octf.octDP2BP_Upload(user,name, auth, shift, req_list)
        
        
        
        
        
        
        
        
        sub_name = 'octOLDRaw__'
        # OLD FY第二層
        if btnName[0:11] == sub_name:
            print(sub_name + 'Post')
            logging.info((sub_name + 'Post'))
            
            isSY = False
            aaa = btnName.split('__', 6)
            date = aaa[1]
            pc = aaa[2]
            eqp = aaa[3]
            old_shift = aaa[4]
            oct_def = aaa[5]
            
            #判斷是否為兩項
            if len(date) >= 15:
                bbb = date.split('+', 1)
                date1 = bbb[0]
                date2 = bbb[1]
                print(date1, date2)
            else:
                date1 = date
                date2 = date
            return octf.octOLDRaw(user,name, auth, shift, date1, date2, old_shift, eqp, pc, oct_def, isSY)
        
        
        
        sub_name = 'octOLDSYRaw__'
        # OLD SY第二層
        if btnName[0:13] == sub_name:
            print(sub_name + 'Post')
            logging.info((sub_name + 'Post'))
            
            isSY = True
            aaa = btnName.split('__', 6)
            date = aaa[1]
            pc = aaa[2]
            eqp = aaa[3]
            old_shift = aaa[4]
            oct_def = aaa[5]
            
            #判斷是否為兩項
            if len(date) >= 15:
                bbb = date.split('+', 1)
                date1 = bbb[0]
                date2 = bbb[1]
                print(date1, date2)
            else:
                date1 = date
                date2 = date
            return octf.octOLDRaw(user,name, auth, shift, date1, date2, old_shift, eqp, pc, oct_def, isSY)
        
        
        sub_name = 'octCheckUpload'
        # OCT看圖後上傳紀錄
        if request.form.get(sub_name) is not None:
            logging.info('判圖記錄上傳中...(octCheckUpload)')
            #print(request.form)
            req_list = list(request.form)[:-1] #-1為submit按鈕
            return octf.octCheckUpload(user,name, auth, shift, req_list)
        
        
        # OCT ADC RB標點失敗率
        sub_name = 'octADCRBSuc'
        if request.form.get(sub_name) is not None:
            print(sub_name + 'Post')
            logging.info((sub_name + 'Post'))
            date1 = request.form.get(sub_name+'_date1')
            date2 = request.form.get(sub_name+'_date2')
            if request.form.get(sub_name) != '送出':
                date1 = today_mfg
                date2 = today_mfg
                sql_shift = 'All'
                
            #date1 = '2021-11-17'
            #date2 = '2021-11-18'
            
            return octf.octADCRBSuc(user,name, auth, shift, date1, date2)
        
        
        sub_name = 'octADCRBSucRaw__'
        # ADC成功率  第二層 RAW DATA
        if sub_name in btnName:
            print(sub_name + 'Post')
            logging.info((sub_name + 'Post'))
            
            
            spl = btnName.split('__')
            date1 = spl[1]
            date2 = spl[2]
            tool_id = spl[3]
            pc = spl[4]
            def_col = spl[5]
            return octf.octADCRBSucRaw(user,name, auth, shift, date1, date2, tool_id, pc, def_col,btnName)
            
        sub_name = 'csvDownload'
        # csv下載
        if request.form.get(sub_name) is not None:
            file_name = request.form.get(sub_name) +'.csv'
            #path = r'C:\Users\kjchen\craig\maint\210810\static'
            print('CSV下載:', file_name)
            path = r'static\csv'
            return send_from_directory(path, file_name, as_attachment=True)
        
        sub_name = 'octADCRBSucEQP__'
        # ADC成功率  第二層 CT1機台分布
        if sub_name in btnName:
            print(sub_name + 'Post')
            logging.info((sub_name + 'Post'))
    
            spl = btnName.split('__')
            date1 = spl[1]
            date2 = spl[2]
            tool_id = spl[3]
            pc = spl[4]
            def_col = spl[5]
        
            return octf.octADCRBSucEQP(user,name, auth, shift, date1, date2, tool_id, pc, def_col)
        sub_name = 'octADCRBSuc_Upload'
        # OCT ADC RB看圖後上傳紀錄
        if request.form.get(sub_name) is not None:
            logging.info('判圖記錄上傳中...(octADCRBSuc_Upload)')
            #print(request.form)
            req_list = list(request.form)[:] #-1為submit按鈕
            return octf.octADCRBSuc_Upload(user,name, auth, shift, req_list)
            
        # OCT ADC RB覆判成功率
        sub_name = 'octADCRBRej'
        if request.form.get(sub_name) is not None:
            print(sub_name + 'Post')
            logging.info((sub_name + 'Post'))
            date1 = request.form.get(sub_name+'_date1')
            date2 = request.form.get(sub_name+'_date2')
            if request.form.get(sub_name) != '送出':
                date1 = today_mfg
                date2 = today_mfg
                sql_shift = 'All'
            
            #date1 = '2021-11-17'
            #date2 = '2021-11-18'
            return octf.octADCRBRej(user,name, auth, shift, date1, date2)
        
        
        sub_name = 'octADCRBRejRaw0__'
        # ADC RB覆判  第二層 RAW DATA
        if sub_name in btnName:
            print(sub_name + 'Post')
            logging.info((sub_name + 'Post'))
            
           
            spl = btnName.split('__')
            date1 = spl[1]
            date2 = spl[2]
            tool_id = spl[3]
            pc = spl[4]
            def_col = spl[5]
            
            return octf.octADCRBRejRaw0(user,name, auth, shift, date1, date2, tool_id, pc, def_col)
        
        
        sub_name = 'octADCRBRejRaw'
        # ADC RB覆判  第三層 RAW DATA
        if request.form.get(sub_name) is not None:
            print(sub_name + 'Post')
            logging.info((sub_name + 'Post'))
            
            btn_value0 = request.form.get(sub_name)
            print(btn_value0)
            spl = btn_value0.split('__')
            date1 = spl[1]
            date2 = spl[2]
            tool_id = spl[3]
            pc = spl[4]
            def_col = spl[5]
            defect = spl[6]
            return octf.octADCRBRejRaw(user,name, auth, shift, date1, date2, tool_id, pc, def_col, defect)
        
        
        
        # 舊版raw data第二層(已無使用)
        sub_name = 'octADCRBRejRaw__'
        # ADC RB覆判  第三層 RAW DATA
        if sub_name in btnName:
            print(sub_name + 'Post')
            logging.info((sub_name + 'Post'))
            
           
            spl = btnName.split('__')
            date1 = spl[1]
            date2 = spl[2]
            tool_id = spl[3]
            pc = spl[4]
            def_col = spl[5]
            return octf.octADCRBRejRaw(user,name, auth, shift, date1, date2, tool_id, pc, def_col)
        
        
        
        sub_name = 'octADCRBRejEQP__'
        # ADC RB 覆判  第二層 CT1機台分布
        
        if sub_name in btnName:
            print(sub_name + 'Post')
            logging.info((sub_name + 'Post'))
    
            spl = btnName.split('__')
            date1 = spl[1]
            date2 = spl[2]
            tool_id = spl[3]
            pc = spl[4]
            def_col = spl[5]
        
            return octf.octADCRBSucEQP(user,name, auth, shift, date1, date2, tool_id, pc, def_col)
        
        sub_name = 'octADCRBRej_Upload'
        # ADC RB覆判 上傳紀錄
        if request.form.get(sub_name) is not None:
            logging.info('判圖記錄上傳中...(octADCRBRej_Upload)')
            #print(request.form)
            req_list = list(request.form)[:] #-1為submit按鈕
            return octf.octADCRBRej_Upload(user,name, auth, shift, req_list)
        
        # OCT ADC RB Sampling(oct抽樣)
        sub_name = 'octADCRBSamp'
        if request.form.get(sub_name) is not None:
            print(sub_name + 'Post')
            logging.info((sub_name + 'Post'))
            date1 = request.form.get(sub_name+'_date1')
            date2 = request.form.get(sub_name+'_date2')
            if request.form.get(sub_name) != '送出':
                date1 = today_mfg
                date2 = today_mfg
                sql_shift = 'All'
                
            #date1 = '2021-11-17'
            #date2 = '2021-11-18'
            return octf.octADCRBSamp(user,name, auth, shift, date1, date2)
        
        
        sub_name = 'octADCRBSampRaw__'
        # OCT ADC RB Sampling RAW DATA
        if sub_name in btnName:
            print(sub_name + 'Post')
            logging.info((sub_name + 'Post'))
            
            
            spl = btnName.split('__')
            date1 = spl[1]
            date2 = spl[2]
            tool_id = spl[3]
            pc = spl[4]
            def_col = spl[5]
            return octf.octADCRBSampRaw(user,name, auth, shift, date1, date2, tool_id, pc, def_col)
        
        sub_name = 'octADCRBSamp_Upload'
        # OCT ADC RB Sampling上傳
        if request.form.get(sub_name) is not None:
            logging.info('POW...(octADCRBSamp_Upload)')
            #print(request.form)
            req_list = list(request.form)[:] #-1submits
            return octf.octADCRBSamp_Upload(user,name, auth, shift, req_list)
        
        
        # OCT AOI GO RATIO
        sub_name = 'octAOIGO'
        if request.form.get(sub_name) is not None:
            print(sub_name + 'Post')
            logging.info((sub_name + 'Post'))
            date1 = request.form.get(sub_name+'_date1')
            date2 = request.form.get(sub_name+'_date2')
            if request.form.get(sub_name) != '送出':
                date1 = today_mfg
                date2 = today_mfg
                
            return octf.octAOIGO(user,name, auth, shift, date1, date2)
        
        # OCT AOI GO RATIO
        sub_name = 'octAOIRKRaw1__'
        if sub_name in btnName:
            print(sub_name + 'Post')
            logging.info((sub_name + 'Post'))
            spl = btnName.split('__')
            g_type = spl[1]
            mfg_day = spl[2]
            tool_id = spl[3]
            grade = spl[4]
            return octf.octAOIRKRaw1(user,name, auth, shift, g_type, mfg_day, tool_id)
        
        # OCT AOI GO RATIO
        sub_name = 'octAOIGORaw1__'
        if sub_name in btnName:
            print(sub_name + 'Post')
            logging.info((sub_name + 'Post'))
            spl = btnName.split('__')
            g_type = spl[1]
            mfg_day = spl[2]
            tool_id = spl[3]
            grade = spl[4]
            
            return octf.octAOIGORaw1(user,name, auth, shift, g_type, mfg_day, tool_id)
        # OCT AOI GO RATIO
        sub_name = 'octAOIGORaw2'
        # OCT ADC RB Sampling RAW DATA
        if request.form.get(sub_name) is not None:
            print(sub_name + 'Post')
            logging.info((sub_name + 'Post'))
            
            btn_value0 = request.form.get(sub_name)
            print(btn_value0)
            spl = btn_value0.split('__')
            g_type = spl[0]
            mfg_day = spl[1]
            tool_id = spl[2]
            isG = spl[3]
            if isG == 'G0':
                isG = True
            elif isG == 'NO_GO':
                isG = False
                
            defect = spl[4]
            
            return octf.octAOIGORaw2(user,name, auth, shift, g_type, mfg_day, tool_id, isG, defect)
        
        sub_name = 'octAOIGO_Upload'
        # octAOIGO上傳
        if request.form.get(sub_name) is not None:
            logging.info('上傳中...(octAOIGO_Upload)')
            #print(request.form)
            req_list = list(request.form)[:] #-1submits
            return octf.octAOIGO_Upload(user,name, auth, shift, req_list)
        
        
        
        
        
        
        # OCT AOI SAMPLING
        sub_name = 'octAOISamp'
        if request.form.get(sub_name) is not None:
            print(sub_name + 'Post')
            logging.info((sub_name + 'Post'))
            date1 = request.form.get(sub_name+'_date1')
            date2 = request.form.get(sub_name+'_date2')
            if request.form.get(sub_name) != '送出':
                date1 = today_mfg
                date2 = today_mfg
                
            return octf.octAOISamp(user,name, auth, shift, date1, date2)
        
        
        # OCT AOI SAMPLING
        
        sub_name = 'octAOISampRaw__'
        # OCT ADC RB Sampling RAW DATA
        if sub_name in btnName:
            print(sub_name + 'Post')
            logging.info((sub_name + 'Post'))
            
            
            spl = btnName.split('__')
            date1 = spl[1]
            date2 = spl[2]
            tool_id = spl[3]
            pc = spl[4]
            def_col = spl[5]
                
            return octf.octAOISampRaw(user,name, auth, shift, date1, date2, tool_id, pc, def_col)
        
        sub_name = 'octAOISamp_Upload'
        # octAOISamp上傳
        if request.form.get(sub_name) is not None:
            logging.info('上傳中...(octAOISamp上傳)')
            #print(request.form)
            req_list = list(request.form)[:] #-1submits
            return octf.octAOISamp_Upload(user,name, auth, shift, req_list)
        
        
        
        
        
        
        
        # OCT ADC Shift
        sub_name = 'octADCShift'
        if request.form.get(sub_name) is not None:
            print(sub_name + 'Post')
            logging.info((sub_name + 'Post'))
            date1 = request.form.get(sub_name+'_date1')
            date2 = request.form.get(sub_name+'_date2')
            if request.form.get(sub_name) != '送出':
                date1 = today_mfg
                date2 = today_mfg
                
            return octf.octADCShift(user,name, auth, shift, date1, date2)
        
        
        # OCT ADC Shift raw
        sub_name = 'octADCShiftRaw'
        if request.form.get(sub_name) is not None:
            print(sub_name + 'Post')
            logging.info((sub_name + 'Post'))
            date1 = request.form.get(sub_name+'_date1')
            date2 = request.form.get(sub_name+'_date2')
            if request.form.get(sub_name) != '送出':
                date1 = today_mfg
                date2 = today_mfg
                
            return octf.octADCShiftRaw(user,name, auth, shift, date1, date2)
        
        # 通用Submit實驗區
        """
        req_list = list(request.form)
        for req0 in req_list:
            if req0[:3] == 'sub':
                sub_name = req0
                date1 = request.form.get(sub_name+'_date1')
                date2 = request.form.get(sub_name+'_date2')
                if request.form.get(sub_name) != '送出':
                    date1 = today_mfg
                    date2 = today_mfg
                    
                if sub_name == '':
                    1
        """
        #  LASER系統特區    
       
        # cj 救廢片
        sub_names = ['lsrCJScrapped', 'lsrCJScrapped_03', 'lsrCJScrapped_05', 'lsrCJScrapped_07', 'lsrCJScrapped_10', 'lsrCJScrapped_20']
        for sub_name in sub_names:
            if request.form.get(sub_name) is not None:
                print(sub_name + 'Post')
                logging.info((sub_name + 'Post'))
                
                if sub_name[-2:] in ['03', '05', '07', '10', '20']:
                    hd_filter = int(sub_name[-2:])
                else:
                    hd_filter = 0
                #date = request.form.get(sub_name+'_date')
                #if date is None:
                #    date = today
                date = today_mfg
                return lsrCJScrapped(user,name, auth, shift, date, hd_filter)
        
        sub_names = 'lsrCJScrapped2'
        if request.form.get(sub_name) is not None:
            print(sub_name + 'Post')
            logging.info((sub_name + 'Post'))
            
            #return lsrCJScrapped(user,name, auth, shift, date, hd_filter)
    
        
        # cj 救廢片 上傳
        sub_name = 'lsrCJScrapped_Upload'
        if request.form.get(sub_name) is not None:
            print(sub_name + 'Post')
            logging.info((sub_name + 'Post'))
            date = today_mfg
            hd_filter = 0
            return lsrCJScrapped_Upload(user,name, auth, shift, date)
        # cj 救廢片 紀錄查詢
        sub_name = 'lsrCJScrapped_history'
        if request.form.get(sub_name) is not None:
            print(sub_name + 'Post')
            logging.info((sub_name + 'Post'))
            date1 = request.form.get('lsrCJScrapped_date1')
            date2 = request.form.get('lsrCJScrapped_date2')
            
            if date1 is None:
                date1 = today
                date2 = today
            
        
            return lsrCJScrapped_history(user,name, auth, shift , date1, date2)
        
        # LASER CHIPID查詢
        sub_name = 'lsrBychip'
        if request.form.get(sub_name) is not None:
            print(sub_name + 'Post')
            logging.info((sub_name + 'Post'))
            chipid = request.form.get('lsrBychip_chipid')
            return lsrBychip(user,name, auth, shift, chipid)
        
               
        # LASER RJ Check
        sub_name = 'lsrRJCheck'
        if request.form.get(sub_name) is not None:
            print(sub_name + 'Post')
            logging.info((sub_name + 'Post'))
            date1 = request.form.get(sub_name+'_date1')
            date2 = request.form.get(sub_name+'_date2')
            if request.form.get(sub_name) != '送出':
                date1 = today_mfg
                date2 = today_mfg
                sql_shift = 'All'
                
            #date1 = '2021-11-17'
            #date2 = '2021-11-18'
            return lsrRJCheck(user,name, auth, shift, date1, date2)
        
        
        sub_name = 'lsrRJCheckRaw__'
        # LASER RJ Check RAW DATA
        if sub_name in btnName:
            print(sub_name + 'Post')
            logging.info((sub_name + 'Post'))
            
           
            spl = btnName.split('__')
            date1 = spl[1]
            date2 = spl[2]
            tool_id = spl[3]
            pc = spl[4]
            def_col = spl[5]
            return lsrRJCheckRaw(user,name, auth, shift, date1, date2, tool_id, pc, def_col)
        
        
        sub_name = 'lsrRJCheckCT1__'
        # LASER RJ Check RAW DATA(CT1坐標)
        req_list = list(request.form)
        str_match = [s for s in req_list if sub_name in s]
        if len(str_match) > 0:
            print(sub_name + 'Post')
            logging.info((sub_name + 'Post'))
            print(str_match)
            for name0 in str_match:
                spl = name0.split('__')
                chipid = spl[1]
            
                return lsrRJCheckCT1(user,name, auth, shift, chipid)
        
        
        
        sub_name = 'lsrRJCheck_Upload'
        # LASER RJ Check上傳
        if request.form.get(sub_name) is not None:
            logging.info('POW...(lsrRJCheck_Upload)')
            #print(request.form)
            req_list = list(request.form) #-1submits
            return lsrRJCheck_Upload(user,name, auth, shift, req_list)
        
        
        # 影像測試
        sub_name = 'imgTest'
        if request.form.get(sub_name) is not None:
            print(sub_name + 'Post')
            sectShow = sub_name
            return render_template('userMain.html',sectShow=sectShow, user=str(user),name=name, auth=auth, shift=shift)
        
        
        sub_name = 'blockCheck'
        if request.form.get(sub_name) is not None:
            print(sub_name + 'Post')
            return blockCheck(user,name, auth, shift)
        
        """
        sub_name = 'blockCheck_Upload'
        if request.form.get(sub_name) is not None:
            print(sub_name + 'Post')
            return blockCheck_Upload(user,name, auth, shift)
        """
        
        sub_name = 'dlTime'
        if request.form.get(sub_name) is not None:
            print(sub_name + 'Post')
            sectShow = sub_name
            #return blockCheck(user,name, auth, shift)
        sub_name = 'sysHealthy'
        if request.form.get(sub_name) is not None:
            print(sub_name + 'Post')
            sectShow = sub_name
            table = "sys_healthy"
            df_sysHeal = mysql2df6878(table)
            df_sysHeal.drop_duplicates(["System_Name", "Status"],keep='last', inplace=True)
            df_sysHeal.reset_index(drop=True, inplace=True)
            today_dt = datetime.datetime.today()
            for idx0 in df_sysHeal.index:
                time0 = df_sysHeal.loc[idx0]['Time']
                    
                dt_time0 = datetime.datetime.strptime(time0, '%Y%m%d_%H%M')
                spend_time0 = (today_dt - dt_time0).total_seconds() / 60
                if spend_time0 > 60:
                    df_sysHeal.loc[idx0, 'Status'] = 'R'
                else:
                    df_sysHeal.loc[idx0, 'Status'] = 'G'
            return render_template('userMain.html',sectShow=sectShow, user=str(user),name=name, auth=auth, shift=shift,
                                  df_sysHeal=df_sysHeal)
            #return blockCheck(user,name, auth, shift)
            
        sub_name = 'healthy365'
        if request.form.get(sub_name) is not None:
            sectShow = sub_name
            print(sub_name + 'Post')
            table = "healthy365 "
            df_healthy365 = mysql2df(table)
            df_healthy365['KPI_Value'] = df_healthy365['KPI_Value'].round(2).copy()
            df_healthy365['Time'] = df_healthy365['Time'].apply(lambda x: str(datetime.datetime.strptime(x, "%Y%m%d_%H%M"))[:-3])
            df_healthy365.drop_duplicates(['Model_Name'], keep='last', inplace=True)
            return render_template('userMain.html',sectShow=sectShow, user=str(user),name=name, auth=auth, shift=shift,
                                  df_healthy365=df_healthy365)
        
        
        # CT1 AGM Alarm參數設定
        
        sub_name = 'ct1AGMPara'
        if request.form.get(sub_name) is not None:
            sectShow = sub_name
            print(sub_name + 'Post')
            
            if request.form.get(sub_name) == '上傳':
                
                
                
                
                
                
                
                
                print('AGM 已上傳參數')
            table = 'system_ison'
            df_ison = mysql2df6878(table)
            
            """
            cols=['System_Name', 'isON', 'Time','CCCGL1082','CCCGL1083','CCCGL2082','CCCGL2083','CCCGL3082','CCCGL3083','CCCGL4082','CCCGL4083','CCCGL5082','CCCGL5083','CCCGL6082','CCCGL6083','CCCGL7082','CCCGL7083','CCCGL8082','CCCGL8083','CCCGL9072','CCCGL9073']
            agm_eqps=['CCCGL1082','CCCGL1083', 'CCCGL3082','CCCGL3083','CCCGL5082','CCCGL6082','CCCGL6083','CCCGL8082','CCCGL9072','CCCGL9073']
            df0 = pd.DataFrame(columns=cols)
            for col0 in cols:
                if col0 in agm_eqps:
                    df0.loc[0,col0] = 'Y'
                else:
                    df0.loc[0,col0] = 'N'
            df0['System_Name'] = 'CT1_AGM_Alarm'
            df0['Time'] = '2022-02-08 09:54'
            df0['isON'] = 'Y'
            """
            upload_ans = ""
            if request.form.get(sub_name) == '更改後請上傳':
                
                #now2 = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                
                df_new = pd.DataFrame(columns = df_ison.columns)
                df_new.loc[0, 'Time'] = now2
                df_new.loc[0, 'Name'] = str(name)
                df_new.loc[0, 'System_Name'] = 'CT1_AGM_Alarm'
                for col0 in df_new.columns:
                    if col0 not in ['System_Name', 'Name', 'Time']:
                        val0 = request.form.get(col0)
                        if val0 is None:
                            df_new.loc[0, col0] = 'N'
                        else:
                            df_new.loc[0, col0] = val0
                df2mysql6878_app(df_new, table)        
                tt.sleep(0.5)
                
                
                print('AGM 已上傳參數')
                # 再讀一次資料庫
                df_ison = mysql2df6878(table)
                
                upload_ans = now2 + ' 上傳成功!!'
                
                
                
            df_ison.sort_values(by=['Time'], inplace=True)
            df_ison.drop_duplicates(['System_Name'], keep='last', inplace=True)
            dict_ison = df_ison.to_dict('records')[-1]
            
            
            ct1_cols = []
            for col0 in df_ison.columns:
                1
            
            return render_template('userMain.html',sectShow=sectShow, user=str(user),name=name, auth=auth, shift=shift,
                                  dict_ison=dict_ison, upload_ans=upload_ans)
        
        
        return render_template('userMain.html',sectShow=sectShow, user=str(user),name=name, auth=auth, shift=shift)

@app.route('/route_function',methods=[ "GET",'POST'])
def route_function():
    theFood = request.form.get('thefood')
    print(theFood)
    return jsonify({'validate': 'formula success','PayAmount':1500,'Rtnfood':theFood})
    #return "hiiiii"

@app.route('/ajax_return',methods=[ "GET",'POST'])
def ajax_return():
    theFood = request.form.get('thefood')
    print(theFood)
    return jsonify({'validate': 'formula success','PayAmount':1500,'Rtnfood':theFood})

@app.route('/cst_check',methods=[ "GET",'POST'])
def cst_check():
    cst_id = request.form.get('CST_ID')
    eqp = request.form.get('EQP')
    eqp_need = request.form.get('EQP_NEED')
    print(eqp_need, type(eqp_need))
    #print('cst id檢查',str(cst_id), eqp)
    
    sql = r"select t.eqp_id, count(t.eqp_id)"
    sql += r" from celods.h_chip_oper_ods t"
    sql += r" where t.process_stage='BEOL'"
    sql += r" and t.op_id in ('OCT1', 'OCT2', 'ADC2')"
    sql += r" and t.mfg_day > current_date - interval '2' day"
    sql += r" and cassette_id like '%"+cst_id+"%'"
    sql += r" group by t.eqp_id"
    
    sql = r"select t.eqp_id"
    sql += r" from celods.H_CHIP_OPER_ODS t"
    sql += r" where t.site_id = 'L11_CELL'" 
    sql += r" and t.process_stage ='BEOL'"
    sql += r" and t.stage_id in ('OCT1', 'OCT2', 'ADC2')"
    
    sql += r" and t.unload_cassette_id like '%"+cst_id+"%'"
    #sql += r" and t.cassette_id like '%"+cst_id+"%'"
    sql += r" and t.eqp_id is not null"
    sql += r" and t.MFG_DAY > current_date - interval '2' day"
    sql += r" group by t.eqp_id"
    
    df_cst2eqp = ora2df(sql)
    #print(df_cst2eqp, len(df_cst2eqp))
    
    eqp = ""
    eqps = []
    if len(df_cst2eqp) > 0:
        eqps = list(df_cst2eqp['EQP_ID'].str[2:])
        for eqp0 in eqps:
            eqp += eqp0 + ', '
        eqp = eqp[:-2]
    else:
        eqp = "無對應"
    return jsonify({'CST_ID': cst_id,'txt0':'hiiii', 'EQP':eqp, 'EQPS':eqps})
    
@app.route('/hr_indiv',methods=[ "GET",'POST'])
def hr_indiv():
    table = 'c2_hr'
    df0 = mysql2df6878(table)
    
    
    
    
if __name__ == '__main__':
    app.debug = True
    today0 = datetime.datetime.now().strftime("%Y%m%d%H%M")
    logging.basicConfig(handlers=[logging.FileHandler('log/web_log_'+today0[2:]+'.log', 'w', 'utf-8')], level=logging.INFO)
    app.secret_key = 'hihi'
    app.run(host= '10.96.70.126', port=6799, threaded=True)
    
    #app.run()
