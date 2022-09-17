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
#from web_func01 import *
#from hr import *
#from laser_func import *
#import oct_func as octf 
from mysql_to_df import *
#logging.info(":"+datetime.now().strftime("%Y-%m-%d %H:%M:%S") +",:"+str(int(etime-stime))+"s")
", "", "

import time as tt
import pandas as pd
import datetime
#import pymysql
from sqlalchemy import create_engine
import cx_Oracle
import os
import matplotlib.pyplot as plt


# AUOFab_PathList
import requests as req00
from lxml import html
import socket
import csv
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


app = Flask(__name__)
app.config["DEBUG"] = True
os.environ['path'] = r'D:\Craig\oracle\instantclient_11_2'+";"+os.environ['path'] 

def req2(server_path, proxies= {'http':"http://10.97.4.1:8080",}):
    #proxies = {'http':"http://10.97.2197.4.1:8080",}
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
    if 1:
        httpRequest = s.get(server_path, proxies=proxies, headers=headers)
    else:
        print('~, '+server_path)
        logging.info('~, '+server_path)
        return ""
        
        
    return httpRequest
# Fab| path list
def AUOFab_PathList(web0):
    proxies = {'http':'http://10.97.4.1:8080'}
    #web0 = 'http://tcweb002.corpnet.auo.com/CCCGL1082/AOI%20Data/Defect_Image/sub1/'
    
    print('reuest...   ', web0[25:], end='   ')
    req = req2(web0)
    print('ok!!')
    
    webpage = html.fromstring(req.content)
    
    pathList = webpage.xpath('//a/@href')[1:]
    folder_list = []
    for fld in pathList:
        # [:-1]h'/' , [1]listG(W)
        if fld[-1] == '/':
            folder_list.append(os.path.split(fld[:-1])[1])
        else:
            folder_list.append(os.path.split(fld)[1])
    #print(os.path.split(i[:-1]))
    return [pathList, folder_list]


print("yyy")
def mysql2df(table):
    try:
        print('mysqlU')
        conn = pymysql.connect(host='localhost',user='craig945',password='ml7ac222',db='craig01',port=3306)
        print('Conn ok')
        cur = conn.cursor()
        cur.execute("SELECT * FROM "+table)  # dyy
        # fetchall()Hlist^Olist(L)
        print('Cur ok')
        result = cur.fetchall()  # dG
        col = cur.description  # dGyz
        columns=[]
        for i in range(len(col)):
            columns.append(col[i][0])  # WACxs
        df0 = pd.DataFrame(result, columns=columns)
        conn.close()
        return df0
    except:
        print('mysql2df -> '+table+'  oexcept')
        logging.info('mysql2df -> '+table+'  oexcept')
        return 'except'

    
def df2mysql(df0, table):
    try:
            # pdData.index[pdData['Machine'] == 'CCCGL400'].tolist()[0]

            #^w
        engine = create_engine("mysql+pymysql://craig945:ml7ac222@localhost:3306/craig01") 
        #delete = 'DROP TABLE IF EXISTS maint;'
        #engine.execute(delete)                 
        print('create_engine ok')
        df0.to_sql(table, engine, if_exists='replace',index=False) 
        print('to_sql ok')
        engine.dispose()
                              
    except:
        print('df2mysql -> '+table+'  oexcept')
        logging.info('df2mysql -> '+table+'  oexcept')
        return 'except'


def df2mysql_app(df0, table):
    try:
        # pdData.index[pdData['Machine'] == 'CCCGL400'].tolist()[0]

        #^w
        engine = create_engine("mysql+pymysql://craig945:ml7ac222@localhost:3306/craig01") 
        #delete = 'DROP TABLE IF EXISTS maint;'
        #engine.execute(delete)                 
        print('create_engine ok')
        df0.to_sql(table, engine, if_exists='append',index=False) 
        print('to_sql ok')
        engine.dispose()
                              
    except:
        print('df2mysql -> '+table+'  oexcept')
        logging.info('df2mysql -> '+table+'  oexcept')
        return 'except'









    """
    mysql = "select t.mfg_day, t.model_no, t.test_user,count(*)as TOT"
    mysql = mysql + ",round(100*sum(decode(t.grade,'G',1,0))/count(*),1) as GO_Ratio"
    mysql = mysql + ",round(100*sum(decode(t.defect_code_desc,'OTHER ALIGN DEFECT',1,0))/count(*),1) as OAD"
    mysql = mysql + ",round(100*sum(decode(t.defect_code_desc,'OTHER APPEAR DEFECT',1,0))/count(*),1) as OPAD" #O_A_D
    mysql = mysql + ",round(100*sum(decode(t.defect_code_desc,'OTHER GLASS DEFECT',1,0))/count(*),1) as OGD"
    mysql = mysql + ",round(100*sum(decode(t.defect_code_desc,'OTHER LINE DEFECT ',1,0))/count(*),1) as OLD" #O_L_D
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
    # UOi
    table = 'maint'
    maint_list = mysql2df(table)
    if type(maint_list) == 'str':
        return '<h1>wMAINTAsiJ</h1>'
   
    # U`I
    table = 'nor_check'
    nor_check = mysql2df(table)
    if type(nor_check) == 'str':
        return '<h1>wnor_checkAsiJ</h1>'
            

    lines = ['CT1', 'OCT', 'LASER']
    
    fliterCT1 = (maint_list["Class"] == "CT1")
    ct1Data = maint_list[fliterCT1]
    
    fliterOCT = (maint_list["Class"] == "OCT")
    octData = maint_list[fliterOCT]
    fliterLSR = (maint_list["Class"] == "LASER")
    lsrData = maint_list[fliterLSR]
    
    min_Done = [min(ct1Data.loc[:, 'Done']), min(octData.loc[:, 'Done']), min(lsrData.loc[:, 'Done'])]
    print('Dreload')
    notify='o'
    
    # oracle Pk
    
    Start_Day = date1[0:4]+'/'+date1[5:7]+'/'+date1[8:10]
    End_Day = date2[0:4]+'/'+date2[5:7]+'/'+date2[8:10]
    
    mysql = "select t.mfg_day, t.model_no, t.test_user as LINE, count(*)as TOT"
    mysql = mysql + ",round(100*sum(decode(t.grade,'G',1,0))/count(*),1) as GO"
    mysql = mysql + ",round(100*sum(decode(t.defect_code_desc,'V-OPEN-BL',1,0))/count(*),2) as VOBL" #V_OPEN_BL
    mysql = mysql + ",round(100*sum(decode(t.defect_code_desc,'OTHER ALIGN DEFECT',1,0))/count(*),2) as OAD"
    mysql = mysql + ",round(100*sum(decode(t.defect_code_desc,'OTHER APPEAR DEFECT',1,0))/count(*),2) as OAPD" #O_A_D
    mysql = mysql + ",round(100*sum(decode(t.defect_code_desc,'OTHER GLASS DEFECT',1,0))/count(*),2) as OGD"
    #mysql = mysql + ",round(100*sum(decode(t.defect_code_desc,'OTHER LINE DEFECT ',1,0))/count(*),1) as OLD" #O_L_D
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
    subprocess.Popen(['C:/Program Files (x86)/Microsoft Office/Office12/OUTLOOK.exe']) #}OUTLOOK
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
    tt.sleep(10)        #DELAYi|HeF   
    outlook.Quit()
    del outlook
    gc.collect()  
    print('EmailwHX')
    
def mailCraig(subject, body):
    pythoncom.CoInitialize() # is not initialized in the new thread 
    subprocess.Popen(['C:/Program Files (x86)/Microsoft Office/Office12/OUTLOOK.exe']) #}OUTLOOK
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
    time.sleep(6)        #DELAYi|HeF   
    outlook.Quit()
    del outlook
    gc.collect()  
    print('EmailwHX')

#loc = r'\\tw100039213\kjchen-pc02\web v3\WebApplication1\L7AC2 IDL\00 L7AC2\10 tAuto Data\003_Maint_record'
#receiver = 'Craig.Hsiao@auo.com;'
#receiver2 = 'Alex.XC.Pan@auo.com;'+'Yida.Tsai@auo.com;'+ 'Calvin.Wang@auo.com;'+ 'Roger.CH.Hsu@auo.com;'+ 'Jh.Hsu@auo.com;'+'Craig.Hsiao@auo.com;'
#receiver1 = 'Alex.XC.Pan@auo.com;'+'Yida.Tsai@auo.com;'+ 'Calvin.Wang@auo.com;'+ 'Roger.CH.Hsu@auo.com;'+ 'Jh.Hsu@auo.com;'+'Craig.Hsiao@auo.com;'+'KJ.Chen@auo.com;'
#cc = 'Craig.Hsiao@auo.com;'#CC

# checkbox valuestr
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
    
#@Test_TimeMFG DateTime
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
        # nJi
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
        # nJi
        
        
            
            
        if request.form.get('reg') is not None and request.values['reg']=='register':
            
            return render_template('register.html', notify='hihi') 
    
        # qvi
        elif request.form.get('regOK') is not None and request.values['regOK']=='registerOK':
            user = request.form.get('userNum')
            pw1 = request.form.get('pw1')
            pw2 = request.form.get('pw2')
            
            if pw1 != pw2 :
                return render_template('register.html', notify='Error!!GJKXP') 
            
            if len(user) != 7: 
                return render_template('register.html', notify='Error!!u7X') 
            try:
                print(str(user)+'iU...')
                conn = pymysql.connect(host='localhost',user='craig945',password='ml7ac222',db='craig01',port=3306)
                cur = conn.cursor()
            
                cur.execute("SELECT * FROM user_data")  # dyy
                # fetchall()Hlist^Olist(L)
                result = cur.fetchall()  # dG
                col = cur.description  # dGyz
                columns=[]
                for i in range(len(col)):
                    columns.append(col[i][0])  # WACxs
                userData = pd.DataFrame(result, columns=columns)
                conn.close()
                #print(maint_list)
            except:
                return render_template('register.html', notify='Error!!UwAseXorpz') 
            
            try:
                for i in range(len(userData)):
                    if int(user) == int(userData.loc[i]['Number']):
                        userData.loc[i, 'PW'] = pw1
                         
 
                        #^w
                        engine = create_engine("mysql+pymysql://craig945:ml7ac222@localhost:3306/craig01") 
                        #delete = 'DROP TABLE IF EXISTS maint;'
                        #engine.execute(delete)                 
                        print('  create_engine ok')
                        userData.to_sql('user_data', engine, if_exists='replace',index=False) 
                        print('  to_sql ok')
                        engine.dispose()
                        return render_template('register.html', notify='U\!!!"^nJ"!!!') 
            except:
                         #engine.dispose()
                return render_template('register.html', notify='Error!!WwAseXorpz') 
            
            
            
                
      # o/loginH 
     
", "", "#JxAa
         


@app.route('/para/<user>')
def index(user):
    return render_template('ccc.html', user_template=user)


    
@app.route('/user/<uName>')
def userName(uName):
    return 'hiiiiiii???' + uName

def build_csv(df0):
    #
    
    
    now0 = datetime.datetime.now().strftime("%Y%m%d_%H:%M")
    #path0 = os.path.join(SaveDir, 'CC_Log')
    
    
    #if not os.path.isdir(saveDir):
    #    os.makedirs(saveDir) 
    #saveDir = "C:\Users\USER\Downloads\System_Log\Laser\PointCheck"
    saveDir = r"\\cccgla073\AOI_Data\Log\Laser\PointCheck"
    mkDir_all(saveDir)
    cols = list(df0.columns)
    cols.append('Time')
    csvName =  os.path.join(saveDir, now0[:8] + ".csv")
    for idx0 in df0.index:
        vals = list(df0.loc[0])
        vals.append(now0)
        with open(csvName, "a+", newline='') as csvfile:
            writer = csv.writer(csvfile, quoting=csv.QUOTE_NONNUMERIC)                      
            with open(csvName, "r+", newline="") as f:
                reader = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
                if not [row for row in reader]:
                    writer.writerow(cols)                
                 
                writer.writerow(vals)
                
                f.flush()
                csvfile.flush()
            f.close()
            csvfile.close
            
        
@app.route('/fabMain', methods=['GET', 'POST'])
def fabMain():
    
    user,name, auth, shift = ["Fab", "Fab", "Fab", "Fab"]
    #tt.sleep(5)
    today0 = datetime.date.today().strftime("%Y%m%d")
    today = datetime.date.today().strftime("%Y-%m-%d")
    now = datetime.datetime.now().strftime("%Y%m%d%H%M")
    # W
    now2 = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    ystday = (datetime.date.today()+datetime.timedelta(-1)).strftime("%Y-%m-%d")
    if int(now[-4:]) < 730:
        today_mfg = ystday
    else:
        today_mfg = today
    # Laser IT{t
    sectShow = ''
    sub_name = 'lsrPointCheck'
    if request.form.get(sub_name) == 'left':
        sectShow = sub_name
        
        # l
        
        chipids = ""
        df_octPoint = pd.DataFrame()
        return render_template('fabMain.html',sectShow=sectShow, user=str(user),name=name, auth=auth, shift=shift,
                               chipids=chipids, df_octPoint = df_octPoint
                               )
    elif request.form.get(sub_name) == 'search':
        sectShow = sub_name
        chipids = ""
        chipids = request.form.get("lsrPointCheck_chipids")
        chipids = str(chipids).upper()
        print(chipids)
        sql = r"select distinct t.tft_chip_id as chip_id,t.product_code, "
        sql += r" t.defect_code_desc as defect, t.test_signal_no as x, t.test_gate_no as y,"
        sql += r"  t.test_tool_id as oct_eqp, t.test_user, "
        sql += r" to_char(t.test_time,'yyyy-MM-dd hh24:mi:ss') as test_time"
        sql += r" from celods.h_dax_fbk_defect_ods t"
        sql += r" where"
        sql += r" t.site_type = 'BEOL'"
        sql += r" and t.test_op_id = 'OCT2'"
        sql += r" and t.defect_code_desc in ('V-OPEN', 'X-SHORT', 'V-COM-SHORT')"
        sql += r" and t.test_user not in ('CCCTSA04','CCCTS504','CCCTS603',"
        sql += r" 'CCCTS903','CCCTS303','CCOCT303','CCOCT403','CCOCTA03',"
        sql += r" 'CCOCTB03','CCOCTC03','CCOCTE00')"
        sql += r" and t.tft_chip_id = '" + chipids + "'"
        #sql += r" and t.TEST_MFG_DAY > to_date('2022/6/1','yyyy/mm/dd')"
        sql += r" and t.test_time="
        sql += r" (select max(tt.test_time) from celods.h_dax_fbk_defect_ods tt "
        sql += r"   where tt.tft_chip_id=t.tft_chip_id "
        sql += r"         and tt.test_tool_id=t.test_tool_id "
        sql += r"         and tt.defect_code_desc=t.defect_code_desc)"    
        
        df_octPoint = ora2df(sql)
        df_octPoint.drop_duplicates(["CHIP_ID", "DEFECT"], keep='last', inplace=True)
        df_octPoint.reset_index(drop=True, inplace=True)
        eqp2ip = {}
        eqp2ip["CCOCT502"] = "http://10.97.213.16/CellTester/Log"
        eqp2ip["CCOCT503"] = "http://10.97.212.14/CellTester/Log"
        eqp2ip["CCOCT602"] = "http://10.97.213.24/CellTester/Log"
        eqp2ip["CCOCT603"] = "http://10.97.212.23/CellTester/Log"
        eqp2ip["CCOCT702"] = "http://10.97.212.83/CellTester/Log"
        eqp2ip["CCOCT703"] = "http://10.97.213.75/CellTester/Log"
        eqp2ip["CCOCTA00"] = "http://10.97.212.70/CellTester/Log"
        eqp2ip["CCOCTB00"] = "http://10.97.212.38/CellTester/Log"
        eqp2ip["CCOCTC00"] = "http://10.97.212.98/CellTester/Log"
        eqp2ip["CCCTS500"] = "http://10.97.212.10/CellTester/Log"
        eqp2ip["CCCTS600"] = "http://10.97.212.22/CellTester/Log"
        eqp2ip["CCCTS900"] = "http://10.97.212.231/CellTester/Log"
        eqp2ip["CCCTSA00"] = "http://10.97.213.227/CellTester/Log"


        #http://10.97.212.14/CellTester/Log/2022-06-06/ADC_Defect/20220606%20053552%20C5659ZC%203310%20247.jpg
        df_octPoint2 = df_octPoint.copy()
        df_octPoint2["Point_Imgs"] = ""
        for idx0 in df_octPoint.index:
            eqp0 = df_octPoint.loc[idx0]['OCT_EQP']
            test_time0 = str(df_octPoint.loc[idx0]['TEST_TIME'])
            chipid0 = df_octPoint.loc[idx0]['CHIP_ID']
            if eqp0 in eqp2ip.keys():
                
                upath0 = eqp2ip[eqp0]
                upath0 = wwwJoin(upath0, [test_time0[:10], "ADC_Defect"])
                print(upath0)
                paths_list, imgs_list  = AUOFab_PathList(upath0)
                
                img_count = 0
                for img_i in range(len(imgs_list)):
                    img0 = imgs_list[img_i]
                    if chipid0 in img0:
                        img_upath0 = wwwJoin(upath0, [img0])
                        img_html0 = r"<a href='"+img_upath0+"'><img align='center' width='160' height='120' src='"+img_upath0+"'  ></a>"
                        img_html1 = "<a href=\"javascript:PopupPic('"+img_upath0+"')\">" + "<img align='center' width='160' height='120' src='"+img_upath0+"'  >" + "</a>"
      
                        df_octPoint.loc[idx0, 'Point_Img_'+str(img_count)] = img_html1
                        df_octPoint2.loc[idx0, 'Point_Imgs'] = df_octPoint2.loc[idx0]['Point_Imgs'] + ", " + img_upath0
                        
                        #df_adc.loc[i, 'IMG_'+str(num0-skip_n)] = pattern + r"<a href='"+adc_img[num0]+"'><img align='center' width='160' height='120' src='"+adc_img[num0]+"'  ></a>"
                        # df_aoi.loc[i, 'IMG_'+str(num0-skip_n)] = "<a href=\"javascript:PopupPic('"+aoi_img[num0]+"')\">"+pattern+"</a>"
                        img_count += 1
                
        if len(df_octPoint2) == 0:
            df_octPoint2.loc[0, 'CHIP_ID'] = str(chipids)
        build_csv(df_octPoint2)
        return render_template('fabMain.html',sectShow=sectShow, user=str(user),name=name, auth=auth, shift=shift,
                               chipids=chipids, df_octPoint = df_octPoint
                               )
    
    
    return render_template('fabMain.html',sectShow=sectShow, user=str(user),name=name, auth=auth, shift=shift)
    #return 'hiiiiiii???'





@app.route('/userMain/ct1summary', methods=['GET', 'POST'])
def ct1summary():
    if request.method == 'POST':
        aaa = request.form.get('aaa')
        return(aaa)
        
        
        
@app.route('/login/<sys_name>/<paras>/', methods=['GET', 'POST'])
def loginGo(sys_name, paras):
    
    if request.method == 'POST':
        # nJi
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
            # U`I
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
            # U`I
            table = 'nor_check'
            nor_check = mysql2df(table)
              
            return render_template('userMain_single.html', user=str(user),name=name, auth=auth, shift=shift, nor_check=nor_check, site=site, sectShow=sectShow)

        elif sys_name == 'cps' and paras == 'pmplan':
            sectShow = 'cps'
            table = 'cps_pmplan'
            df0 = mysql2df(table)
            df0 = df0[df0['PM_Plan'] == 'NG'].copy()
            df0.rename(columns = {'Machine': 'EQP'}, inplace=True)
            
            df0[''] = 'wOi'
            df0 = df0[['EQP', '' ,'PM_Ratio']].copy()
            item_name = 'PM Plan'
            return render_template('userMain_single.html', user=str(user),name=name, auth=auth, shift=shift, 
                                   df0=df0, item_name=item_name, sectShow=sectShow)
        
        elif sys_name == 'cps' and paras == 'ct1eqpdiff':
            sectShow = 'cps'
            df0 = cpsEQP_Diff(today, today)
            item_name = 'CT1t'
            return render_template('userMain_single.html', user=str(user),name=name, auth=auth, shift=shift,
                                   df0=df0, item_name=item_name,sectShow=sectShow)
        # EDA
        elif sys_name == 'eda'and paras == 'hr':
            sectShow = 'hr'
            df0 = edaHR()
            item_name = 'Ht'
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
            # D Z; N
            old_shift = 'All'
            #old_shift = spl[2]
            return octf.octOLD(user,name, auth, shift, date1, date2, old_shift)
        elif sys_name in ['octOGD', 'octOAPD', 'octAD']:
            spl = paras.split('$')
            if paras != 'mfgtoday':
                date1 = spl[0]
                date2 = spl[1]
            # D Z; N
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
        return "<h1>error</h1>"
   

@app.route('/userMain', methods=['GET', 'POST'])
def userMain():
    name0000 = request.form.get('name')
    print(name0000, 'iJuserMain')
    #tt.sleep(5)
    today0 = datetime.date.today().strftime("%Y%m%d")
    today = datetime.date.today().strftime("%Y-%m-%d")
    now = datetime.datetime.now().strftime("%Y%m%d%H%M")
    # W
    now2 = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    print(name0000, 'iJuserMain', now2)
    ystday = (datetime.date.today()+datetime.timedelta(-1)).strftime("%Y-%m-%d")
    if int(now[-4:]) < 730:
        today_mfg = ystday
    else:
        today_mfg = today
    sectShow = ''

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
    #print('cst idd',str(cst_id), eqp)
    
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
        eqp = "L"
    return jsonify({'CST_ID': cst_id,'txt0':'hiiii', 'EQP':eqp, 'EQPS':eqps})

    
    
    
run_count = 0
if __name__ == '__main__':
    app.debug = True
    today0 = datetime.datetime.now().strftime("%Y%m%d%H%M")
    logging.basicConfig(handlers=[logging.FileHandler('log/web_log_'+today0[2:]+'.log', 'w', 'utf-8')], level=logging.INFO)
    app.secret_key = 'hihi'
    
    try:
        local_ip = get_ip()
    except:
        print('get_ip error')
        pass
    print(local_ip, run_count)
    run_count += 1
    app.run(host= local_ip, port=9977, threaded=True)
    
    #app.run()
