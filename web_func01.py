# -*- coding: utf-8 -*-
"""
Created on Thu Sep  9 11:24:23 2021

@author: kjchen
"""
# AUOFab_PathList所需
import requests as req00
from lxml import html
import time
import logging
import os
import pymysql
import pandas as pd
import cx_Oracle
import datetime
import math #檢查null
from sqlalchemy import create_engine


from flask import Flask, render_template, request, redirect,flash
from flask import send_file, send_from_directory
from flask import app
from flask import url_for
from flask import flash
from mysql_to_df import *

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

#　Test_Time轉MFG DateTime
def testTime2MFG(test_time):
    date = test_time[0:10]
    time0 = test_time[11:16]
    print(date, time0)
    if int(time0[0:2]) < 7 or (int(time0[0:2]) == 7 and int(time0[3:]) < 30):
        date2 = datetime.datetime.strptime(date, "%Y-%m-%d")
        date = (date2+datetime.timedelta(-1)).strftime("%Y-%m-%d")
        return date
    else:
        return date

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
    #print('reuest中...   ', web0[25:], end='   ')
    req = req2(web0, proxies=proxies)
    print('ok!!')
    t1 = time.time()
    if t1-t0 > 5:
        print('req time:',t1-t0)
    logging.info('req time: '+str(t1-t0))
    webpage = html.fromstring(req.content)
    t2 = time.time()
    if t2-t1 > 5:
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
    
def datesListStr(start_date, end_date):

    start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    date_generated = [start + datetime.timedelta(days=x) for x in range(0, (end-start).days+1)]
    date_list=[]
    for date in date_generated:
        date_list.append(date.strftime("%Y-%m-%d"))

    return date_list
    
def subDefect(eqp,chipid, test_date, chipid_times, defect="NA", ptc=None):
    # http://tcweb002.corpnet.auo.com/CCCGL8082/AOI%20Data/Defect_Image/Sub2/20210908/07/Defect/
    times = []
    list0 = []
    for j in range(11):
       times.append(str(j).rjust(2,'0'))
    
    subs = ['Sub1/', 'Sub2/', 'Sub3/']
    for sub in subs:
        for time0 in chipid_times:
            pathImgs = [r'http://tcweb002.corpnet.auo.com/',  eqp,
                r'/AOI%20Data/Defect_Image/',        ['Sub1/', 'Sub2/', 'Sub3/'],
                test_date,     time0,
                '/Defect/']
            path0 = pathImgs[0]+pathImgs[1]+pathImgs[2]+ sub + pathImgs[4]+'/'+pathImgs[5]+pathImgs[6]
            #print(path0)
            imgs_list = AUOFab_PathList(path0)[1]
            #print(imgs_list)
                #print(imgs_list)
            imgs_dict = {}
            for img in imgs_list:
                if img.endswith('.tif'):
                    continue
                if img[0:7] == chipid:
                    
                    print(path0+img)
                    logging.info('  找到chipid image:'+img)
                    try:
                        spl = img.split('_', 10)
                        spl_def1 = spl[2]
                        if defect in ['BP']:
                            if ptc is not None and ptc != spl_def1[1:]:
                                continue
                        spl_def2 = spl[3]
                    except:
                        continue
                    imgs_dict[spl_def1+spl_def2] = img
            maxXY_list = list(imgs_dict.values())
            #print(maxXY_list)
            for img in maxXY_list:
                list0.append(path0+img)

                    #break
    if len(list0) < 3:
        for iii in range(3-len(list0)):
            list0.append(' ')
            
    return list0


def ct1SameDef(user,name, auth, shift, date):
    sectShow = 'ct1SameDef'
    today0 = datetime.date.today().strftime("%Y%m%d")
    today = today0[0:4]+'-'+today0[4:6]+'-'+today0[6:8]
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    logging.info('ct1SameDef觸發, '+now)
    
        
    # 下載判圖記錄
    table = 'img_check_record'
    df_img_record = mysql2df(table)
    print('mysql2df(table) ok')
    logging.info('mysql2df -> '+table+'   ok!!')
            
    table = 'ct1_samedef'
    df_ct1SameDef = mysql2df(table)
    df_ct1SameDef = df_ct1SameDef[df_ct1SameDef['MFG_DAY'] == date].copy()
    df_ct1SameDef['已Check'] = 0
    df_ct1SameDef['Real_Ratio'] = r"N/A"
    
    drop_list = []
    check_count = 0
    real_tot = 0
    if len(df_ct1SameDef) > 0:
        db_date = df_ct1SameDef.loc[df_ct1SameDef.index[0], 'MFG_DAY']
        df00 = df_img_record[(df_img_record['TEST_TIME_MFG']==db_date)]
    for i in df_ct1SameDef.index:
        db_date = df_ct1SameDef.loc[i, 'MFG_DAY']
        line0 = df_ct1SameDef.loc[i]['LINE']
        model_no0 = df_ct1SameDef.loc[i]['MODEL_NO']
        #mfg_days = datesListStr(date1, date2)
        
        # 去除後兩位.0
        """
        df_ct1SameDef.loc[i, 'TOT'] = str(df_ct1SameDef.loc[i]['TOT'])
        df_ct1SameDef.loc[i, 'Check_Total'] = 0
        df_ct1SameDef.loc[i, 'Real_Total'] = 0
        df_ct1SameDef.loc[i, 'Real_Ratio'] = 0
        """
        
        df0 =  df00[(df00['TEST_USER']==line0) & (df00['MODEL_NO']==model_no0)]
            #df0.drop_duplicates(['CHIPID','PATTERN_CODE'], keep='last', inplace=True)
        if len(df0) > 0:
            last_n = df0.index[-1]
            #df0.drop_duplicates(['CHIP_ID', 'OCT_DEFECT'], keep='last', inplace=True)
            df_ct1SameDef.loc[i, '已Check'] = len(df0)
            check_count += len(df0)
            real_num0 = len(df0[df0['imgCheck']=='R'])
            real_tot += real_num0
            df_ct1SameDef.loc[i, 'Real_Ratio'] = real_num0
            
            df_ct1SameDef.loc[i, 'Real_Ratio'] = round(100*df_ct1SameDef.loc[i]['Real_Ratio']/df_ct1SameDef.loc[i]['已Check'], 1)
        
    
        
        """
        if str(db_date) != date:
            drop_list.append(i)
            continue
        else:
            #加入判圖記錄
            chipid_list = []
            for j in range(len(df_img_record)):
                if df_ct1SameDef.loc[i]['MFG_DAY'] == df_img_record.loc[j]['TEST_TIME_MFG'] and df_ct1SameDef.loc[i]['LINE'] == df_img_record.loc[j]['TEST_USER'] and df_ct1SameDef.loc[i]['MODEL_NO'] == df_img_record.loc[j]['MODEL_NO']:
                    # 不完美 日後補充
                    if df_img_record.loc[j]['CHIPID'] in chipid_list:
                        continue
                    
                    df_ct1SameDef.loc[i, 'Check_Total'] = df_ct1SameDef.loc[i]['Check_Total']+1
                    if df_img_record.loc[j]['imgCheck'] == 'R':
                        df_ct1SameDef.loc[i, 'Real_Total'] = df_ct1SameDef.loc[i]['Real_Total']+1
                    
                    # 紀錄起來 避免重複的chipid
                    chipid_list.append(df_img_record.loc[j]['CHIPID'])
            if df_ct1SameDef.loc[i]['Check_Total'] == 0:
                df_ct1SameDef.loc[i, 'Real_Ratio'] = 0
            else:
                df_ct1SameDef.loc[i, 'Real_Ratio'] = 100*df_ct1SameDef.loc[i]['Real_Total']/df_ct1SameDef.loc[i]['Real_Total']
         """   
       
        
            
            
            
            
    """
    df_ct1SameDef = df_ct1SameDef.drop(index=drop_list)
    df_ct1SameDef = df_ct1SameDef.reset_index()
    df_ct1SameDef = df_ct1SameDef.drop(columns=['index'])
    """
        #df_img_record
    #mach = [ [0,'CCCGL1082',1], [1,'CCCGL1083',0], [2,'CCCGL2082', 1], [3,'CCCGL2083', 0] ]st.values.tolist(), maint_showIdx=maint_showIdx, mi 
    
    return render_template('userMain.html', user=str(user),name=name, auth=auth, shift=shift, sectShow=sectShow, df_ct1SameDef=df_ct1SameDef, date=date)






# (user,name, auth, shift, date1, date2)
def ct1MachDiff(user,name, auth, shift,date1, date2,isNight):
    #isNight = False
    sectShow = 'ct1MachDiff'
    #date1 = date1[0:4]+'/'+date1[5:7]+'/'+date1[8:10]
    #date2 = date2[0:4]+'/'+date2[5:7]+'/'+date2[8:10]
    mysql = "select c.model_no,c.tool_id, c.defect_code_desc, c.eq1, c.eq1NG, c.eq1TOT , c.eq1Ratio, c.eq2, c.eq2NG ,c.eq2TOT, c.eq2Ratio "
    mysql += r",'" + date1 + "' as Start_Day,'" + date2 + "' as End_Day "
    if isNight: 
        mysql += r",'N' as Shift "
    else:
        mysql += r",'All' as Shift "
    mysql += r"from "
    mysql += r"( "
    mysql += r"select a.model_no, a.tool_id ,a.defect_code_desc,(a.tool_id || '2') as eq1,nvl(a.eq1NG,0) as eq1NG,nvl(a.eq1TOT,0) as eq1TOT,nvl(a.eq1Ratio,0) as eq1Ratio,(a.tool_id || '3') as eq2,nvl(b.eq2NG,0) as eq2NG,nvl(b.eq2TOT,0) as eq2TOT,nvl(b.eq2Ratio,0) as eq2Ratio "
    mysql += r",case when abs(a.eq1Ratio-b.eq2Ratio)>=2 then 1 else 0 end as YN "
    mysql += r"from "
    mysql += r"( "
    mysql += r"select a.model_no, a.tool_id ,a.defect_code_desc,b.eq1,b.eq1NG,b.eq1TOT,b.eq1Ratio "
    mysql += r"from "
    mysql += r"( "
    mysql += r"select distinct t.model_no, t.tool_id ,t.defect_code_desc "
    mysql += r"from celods.h_dax_fbk_test_ods t where t.op_id='CGL' "
    mysql += r"and t.mfg_day between to_date('" + date1 + "','yyyy-mm-dd') and to_date('" + date2 + "','yyyy-mm-dd') "
    mysql += r"and t.grade in ('W','X') "
    
    if isNight: 
        mysql += r"and substr(t.shift,1,1) = 'N' "
    
    mysql += r"and t.defect_code_desc not in ('OTHER TFT DEFECT') "
    mysql += r")a "
    mysql += r"left join "
    mysql += r"( "
    mysql += r"select distinct b.model_no, b.tool_id,b.test_user,substr(b.test_user,9,1) as eq1,a.defect_code_desc,a.NG as eq1NG,b.TOT as eq1TOT, round(100*a.NG/b.TOT,2) as eq1Ratio "
    mysql += r"from "
    mysql += r"( "
    mysql += r"select t.model_no, t.tool_id, t.test_user ,t.defect_code_desc ,count(*)as NG "
    mysql += r"from celods.h_dax_fbk_test_ods t where t.op_id='CGL' "
    mysql += r"and t.mfg_day between to_date('" + date1 + "','yyyy-mm-dd') and to_date('" + date2 + "','yyyy-mm-dd') "
    mysql += r"and t.grade in ('W','X') "
    mysql += r"and t.defect_code_desc not in ('OTHER TFT DEFECT') "
    
    if isNight: 
        mysql += r"and substr(t.shift,1,1) = 'N' "
    
    mysql += r"group by t.model_no, t.tool_id, t.test_user,t.defect_code_desc order by 1 "
    mysql += r")a, "
    mysql += r"( "
    mysql += r"select t.model_no, t.tool_id, t.test_user ,count(*)as TOT "
    mysql += r"from celods.h_dax_fbk_test_ods t where t.op_id='CGL' "
    mysql += r"and t.mfg_day between to_date('" + date1 + "','yyyy-mm-dd') and to_date('" + date2 + "','yyyy-mm-dd') "
    
    if isNight: 
        mysql += r"and substr(t.shift,1,1) = 'N' "
    
    mysql += r"group by t.model_no, t.tool_id, t.test_user order by 1 "
    mysql += r")b "
    mysql += r"where a.model_no = b.model_no "
    mysql += r"and a.test_user = b.test_user "
    mysql += r"and substr(b.test_user,9,1) = 2 "
    mysql += r")b "
    mysql += r"on a.model_no = b.model_no "
    mysql += r"and a.tool_id = b.tool_id "
    mysql += r"and a.defect_code_desc = b.defect_code_desc "
    mysql += r")a "
    mysql += r"left join "
    mysql += r"( "
    mysql += r"select distinct b.model_no, b.tool_id,b.test_user,substr(b.test_user,9,1) as eq2,a.defect_code_desc,a.NG as eq2NG,b.TOT as eq2TOT, round(100*a.NG/b.TOT,2) as eq2Ratio "
    mysql += r"from "
    mysql += r"( "
    mysql += r"select t.model_no, t.tool_id, t.test_user ,t.defect_code_desc ,count(*)as NG "
    mysql += r"from celods.h_dax_fbk_test_ods t where t.op_id='CGL' "
    mysql += r"and t.mfg_day between to_date('" + date1 + "','yyyy-mm-dd') and to_date('" + date2 + "','yyyy-mm-dd') "
    mysql += r"and t.grade in ('W','X') "
    
    if isNight: 
        mysql += r"and substr(t.shift,1,1) = 'N' "
    
    mysql += r"and t.defect_code_desc not in ('OTHER TFT DEFECT') "
    mysql += r"group by t.model_no, t.tool_id, t.test_user,t.defect_code_desc order by 1 "
    mysql += r")a,"
    mysql += r"( "
    mysql += r"select t.model_no, t.tool_id, t.test_user ,count(*)as TOT        "
    mysql += r"from celods.h_dax_fbk_test_ods t where t.op_id='CGL' "
    mysql += r"and t.mfg_day between to_date('" + date1 + "','yyyy-mm-dd') and to_date('" + date2 + "','yyyy-mm-dd') "
    
    if isNight: 
        mysql += r"and substr(t.shift,1,1) = 'N' "

    mysql += r"group by t.model_no, t.tool_id, t.test_user order by 1 "
    mysql += r")b "
    mysql += r"where a.model_no = b.model_no "
    mysql += r"and a.test_user = b.test_user "
    mysql += r"and substr(b.test_user,9,1) = 3 "
    mysql += r")b "
    mysql += r"on a.model_no = b.model_no "
    mysql += r"and a.tool_id = b.tool_id "
    mysql += r"and a.defect_code_desc = b.defect_code_desc "
    mysql += r")c "
    mysql += r"where c.YN = 1 "
    logging.info('sql = '+mysql)
    df_machDiff = ora2df(mysql)
    #print(df_machDiff)
    df_machDiff['已Check'] = 0
    df_machDiff['Real_Ratio'] = r"N/A"
    
    
     # 下載判圖記錄
    table = 'img_check_record'
    df_img_record = mysql2df(table)
    print('mysql2df(table) ok')
    logging.info('mysql2df -> '+table+'   ok!!')
    
    check_count = 0
    real_tot = 0
    for i in df_machDiff.index:
        model_no0 = df_machDiff.loc[i]['MODEL_NO']
        mfg_days = datesListStr(date1, date2)
        eqps = [df_machDiff.loc[i]['EQ1'], df_machDiff.loc[i]['EQ2']]
        #加入判圖記錄
        chipid_list = []
        #date_list = datesListStr(date1, date2)
        df0 = df_img_record[(df_img_record['TEST_TIME_MFG'].isin(mfg_days)) & (df_img_record['TEST_USER'].isin(eqps))& (df_img_record['MODEL_NO']==model_no0)]
        
        if len(df0) > 0:
            last_n = df0.index[-1]
            #df0.drop_duplicates(['CHIP_ID', 'OCT_DEFECT'], keep='last', inplace=True)
            df_machDiff.loc[i, '已Check'] = len(df0)
            check_count += len(df0)
            real_num0 = len(df0[df0['imgCheck']=='R'])
            real_tot += real_num0
            df_machDiff.loc[i, 'Real_Ratio'] = real_num0
            
            df_machDiff.loc[i, 'Real_Ratio'] = round(100*df_machDiff.loc[i]['Real_Ratio']/df_machDiff.loc[i]['已Check'], 1)
        

    return render_template('userMain.html', user=str(user),name=name, auth=auth, shift=shift, sectShow=sectShow, date1=date1, date2=date2, df_machDiff=df_machDiff, isNight=isNight)

# 無使用
"""
def ct1SearchImg(df_data):
    imgLinks = []
   
    ABBR_DEFECT_NAMES = ['BP',    'V_O'   , 'V_L'   ,     'H_O', 'H_L',    'X_S'  ,  'VOBL'    ,  'H_BAND_MURA', 'W_S'       ,     'B_S',       'AGM'            , 'OAD'            , 'OAPD',            
                                            'OGD',    'DP_W', 'DPP_W', 'DP_CLUSTER', 'DP_ADJ'   , 'DP_NEAR', 'BPP'     , 'SBP_W',   'CP',       'POINT-COUNT' ]
            
    WHOLE_DEFECT_NAMES = ['BP', 'V-OPEN', 'V-LINE' , 'H-OPEN', 'H-LINE', 'X-SHORT', 'V-OPEN-BL', 'H_BAND_MURA', 'WHITE SPOT', 'BLACK SPOT', 'AROUND GAP MURA', 'OTHER ALIGN DEFECT', 'OTHER APPEAR DEFECT',
                          'OTHER GLASS DEFECT', 'DP', 'DP-PAIR', 'DP_CLUSTER', '3DP_ADJ', 'DP-NEAR', 'BP_PAIR', 'SMALL BP', 'PD13 ',   'POINT COUNT']   
     
    A2W_DEFECT_NAMES = {}
    for i in range(len(ABBR_DEFECT_NAMES)):
        A2W_DEFECT_NAMES[ABBR_DEFECT_NAMES[i]] = WHOLE_DEFECT_NAMES[i]
        
    print(A2W_DEFECT_NAMES)

    # 下載判圖記錄
    table = 'img_check_record'
    df_img_record = mysql2df(table)
    print('mysql2df(table) ok')
    logging.info('mysql2df -> '+table+'   ok!!')

    
    #找圖ya
    for i in range(len(df_data)):
        eqp = df_data.loc[i]['TEST_USER']
        list0 = []
        chipid = df_data.loc[i]['CHIPID']
        time00 = str(df_data.loc[i]['TEST_TIME'])[11:13]
        test_time_str = str(df_data.loc[i]['TEST_TIME'])
        test_date = test_time_str[0:4]+test_time_str[5:7]+test_time_str[8:10]
        df_data.loc[i, 'Check'] = 'N'
        for ii in range(len(df_img_record)):
            if chipid == df_img_record.loc[ii]['CHIPID']:
                df_data.loc[i, 'Check'] = df_img_record.loc[ii]['imgCheck']
                df_data.loc[i, 'Check_Name'] = df_img_record.loc[ii]['name']
                #df_data.loc[i]['Remark'] = df_img_record.loc[ii]['Remark']
            
            
        chipid_times = []
        if time00 == '00':
            chipid_times = [time00]
        else:
            chipid_times = [time00, str(int(time00)-1).zfill(2)]
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
        subDefect_list = ['BP', 'H-OPEN', 'H-LINE', 'V-OPEN', 'POINT-COUNT', 'DP-NEAR']      
        
        # 假資料
        df_data.loc[i,'PATTERN_CODE'] = 'aaa'
        if df_data.loc[i]['DEFECT_CODE_DESC'] in subDefect_list:
            logging.info('  '+chipid+', Pattern Code = '+str(subDefect_list))
            list0 = subDefect(eqp, chipid, test_date, chipid_times)
        
    
        elif df_data.loc[i]['PATTERN_CODE'] is None:
            list0.append(' ')
            list0.append(' ')    
            list0.append(' ')
            #暫不找圖
        # L模式
        elif df_data.loc[i]['PATTERN_CODE'][0] == 'L':
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
        elif df_data.loc[i]['DEFECT_CODE_DESC'] == 'OTHER GLASS DEFECT' and df_data.loc[i]['PATTERN_CODE'][0] == 'M':    
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
                            pc = df_data.loc[i]['PATTERN_CODE']
                            ptn_code = aaa[2][1:]+'_'+aaa[3]   
                            # strlist_num 判斷最後一個字是否為數字
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


        elif df_data.loc[i]['PATTERN_CODE'][0] == 'M':
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
                            pc = df_data.loc[i]['PATTERN_CODE']
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
        
        
        else:
            # 未在已知範圍   給三個空白
            list0.append(' ')
            list0.append(' ')    
            list0.append(' ')  
                
        imgLinks.append(list0)
    return imgLinks
                
"""

# ct1良率 每小時go ratio
        
def goHours(user,name, auth, shift, date):
    sectShow = 'goHours'
    print('goHours date: ', date)
    #date = date[0:4]+'/'+date[5:7]+'/'+date[8:10]
    aaa = list(range(24))
    bbb = list(range(24))
    for i in range(len(aaa)):
        aaa[i] = str(aaa[i]).zfill(2)
        bbb[i] = 'C_'+str(aaa[i]).zfill(2)
    mfg_cols = ['MFG_DAY', 'EQP']
    #mfg_cols = ['MFG_DAY', 'EQP']
    mfg_cols = mfg_cols + aaa[7:24] + aaa[0:7] + ['平均']
    mfg_cols = mfg_cols + bbb[7:24] + bbb[0:7] + ['C_TOT']
    df_goHours = pd.DataFrame(columns = mfg_cols)
    df_goHours.set_index(['MFG_DAY', 'EQP'], inplace=True)
    """
    # 下載判圖記錄
    table = 'img_check_record'
    df_img_record = mysql2df(table)
    print('mysql2df(table) ok')
    logging.info('mysql2df -> '+table+'   ok!!')
    """
    
    sql = ""
    #sql += r"select t.mfg_day, t.test_user, round(100*sum(decode(t.grade,'G',1,0))/count(*),2) as go_ratio, count(*) as TOT,to_char(t.test_time,'HH24') as zfill_hour "
    # go ratio去除 other tft
    sql += r"select t.mfg_day, t.test_user, round(100*sum(decode(t.grade,'G', 1 ,decode(t.defect_code_desc,'OTHER TFT DEFECT',1,0)))/count(*),2) as go_ratio, count(*) as TOT,to_char(t.test_time,'HH24') as zfill_hour "
    
    sql += r"from celods.h_dax_fbk_test_ods t "
    sql += r"where t.op_id='CGL' "
    sql += r"and t.site_type = 'BEOL' " 
    sql += r"and t.mfg_day = to_date('"+ date +"','yyyy-mm-dd') "
    #sql += r"and t.defect_code_desc <> 'OTHER TFT DEFECT' "
    sql += r"group by t.mfg_day,test_user,to_char(t.test_time,'HH24') "
    sql += r"order by t.mfg_day, test_user, to_char(t.test_time,'HH24') "

    df0 = ora2df(sql)
    
    idx = 0
    #df_goHours['MFG_DAY'] = 11111
    """
    for i in df0.index:
        zhour = str(df0.loc[i]['ZFILL_HOUR'])
        for col in list(df_goHours.columns):
            if col == zhour:
                #是否已有ｚｈｏｕｒ下的這個數值
                if not math.isnan(df_goHours.loc[idx][zhour]):
                    idx += 1
                    eqp = df0.loc[i]['TEST_USER']
                    df_goHours.loc[idx, 'MFG_DAY'] = df0.loc[i]['MFG_DAY']
                    df_goHours.loc[idx, 'EQP'] = eqp
                
                eqp = df0.loc[i]['TEST_USER']
                df_goHours.loc[idx, 'MFG_DAY'] = df0.loc[i]['MFG_DAY']
                df_goHours.loc[idx, 'EQP'] = eqp
                df_goHours.loc[idx, zhour] = df0.loc[i]['GO_RATIO']
                df_goHours.loc[idx, 'C_'+zhour] = df0.loc[i]['TOT']
                break
    """
    for i in df0.index:
        zhour = str(df0.loc[i]['ZFILL_HOUR'])
        eqp0 = df0.loc[i]['TEST_USER']
        mfg_day0 = df0.loc[i]['MFG_DAY']
        if 1 or zhour in list(df_goHours.columns):
            df_goHours.loc[(mfg_day0, eqp0), zhour] = df0.loc[i]['GO_RATIO']
            df_goHours.loc[(mfg_day0, eqp0), 'C_'+zhour] = df0.loc[i]['TOT']
    df_goHours.reset_index(drop=False, inplace=True)           



        
    
    for i in df_goHours.index:
        go_sum0 = 0
        go_count0 = 0
        tot_sum0 = 0
        # 獨立處理  避免進到math.isana
        df_goHours.loc[i, 'MFG_DAY'] = str(df_goHours.loc[i]['MFG_DAY'])
        eqp0 = str(df_goHours.loc[i]['EQP'])
        df_goHours.loc[i, 'EQP'] = eqp0
        for col in list(df_goHours.columns[2:]):
            if math.isnan(df_goHours.loc[i][col]):
                df_goHours.loc[i, col] = ' - '
                continue
            elif col[0] != 'C':
                go0 = int(df_goHours.loc[i][col])
                go_sum0 += go0
                go_count0 += 1
                if eqp0[-2:] in ['82', '72']:
                    next_go = df_goHours.loc[i+1][col]
                    
                    if next_go != ' - ' and abs(next_go - go0) > 10:
                        if next_go >= go0:
                            df_goHours.loc[i, col] = df_goHours.loc[i][col]+1000
                elif eqp0[-2:] in ['83', '73']:
                    next_go = df_goHours.loc[i-1][col]
                    if next_go != ' - ' and abs(next_go - go0) > 10:
                        if next_go >= go0:
                            df_goHours.loc[i, col] = df_goHours.loc[i][col]+1000
                
            elif  col[0] == 'C' :
                tot_sum0 += int(df_goHours.loc[i][col])
                
            # 一律轉str
            #df_goHours.loc[i, col] = str(df_goHours.loc[i][col])[0:2]
        df_goHours.round(2)
        df_goHours.loc[i]['平均'] = str(go_sum0/go_count0)[:4]

        df_goHours.loc[i]['C_TOT'] = tot_sum0
    
    """
    # 加入看片記錄
    except_list = ['MFG_DAY', 'MODEL_NO', 'TEST_USER','GO', 'TOT', 'Check總數', 'Real_Ratio', '已Check']
    for i in range(len(df_goHours)):
        #tot = df_goHours.loc[i]['TOT']
        df_goHours.loc[i, '已Check'] = 0
        #df_goHours.loc[i, 'Check總數'] = 0
        df_goHours.loc[i, 'Real_Ratio'] = 0
        
        for col in df_goHours.columns:
            if col not in except_list:
                df_goHours.loc[i, 'Check總數'] += df_goHours.loc[i][col]
                df_goHours.loc[i, col] = round(100*df_goHours.loc[i][col]/tot, 1)
        
        chipid_list = []
        for j in range(len(df_img_record)):
            mfg_str = str(df_goHours.loc[i]['MFG_DAY'])[:10]
            #print(mfg_str)
            if mfg_str == df_img_record.loc[j]['TEST_TIME_MFG'] and df_goHours.loc[i]['EQP'] == df_img_record.loc[j]['TEST_USER']:
                # 不完美 日後補充
                if df_img_record.loc[j]['CHIPID'] in chipid_list:
                    continue
                
                df_goHours.loc[i, '已Check'] = df_goHours.loc[i]['已Check']+1
                if df_img_record.loc[j]['imgCheck'] == 'R':
                    df_goHours.loc[i, 'Real_Ratio'] = df_goHours.loc[i]['Real_Ratio']+1
                
                # 紀錄起來 避免重複的chipid
                chipid_list.append(df_img_record.loc[j]['CHIPID'])
        if df_goHours.loc[i]['已Check'] == 0:
            df_goHours.loc[i, 'Real_Ratio'] = r"N/A"
        else:
            df_goHours.loc[i, 'Real_Ratio'] = round(100*df_goHours.loc[i]['Real_Ratio']/df_goHours.loc[i]['已Check'], 1)
        
    """
    
    
    return render_template('userMain.html', user=str(user),name=name, auth=auth, shift=shift, sectShow=sectShow, date=date, df_goHours=df_goHours)

    
    
        


def goHoursRaw(user,name, auth, shift, btnName):
    
    sectShow = 'goHoursRaw'
    aaa = btnName.split('__', 4)
    mfg_day = aaa[1]
    eqp = aaa[2]
    hour = aaa[3]
    tot = int(aaa[4])
    date = mfg_day[0:4]+'/'+mfg_day[5:7]+'/'+mfg_day[8:10]
    bbb = [date, eqp, hour,tot]
    print(bbb)
    logging.info(str(bbb))
    # 一次撈上下資料
    sql = ""
    sql += r"select t.model_no,t.test_user,t.tft_chip_id as chipid,t.test_time, t.defect_code_desc,t.grade " 
    sql += r"from celods.h_dax_fbk_test_ods t "
    sql += r"where t.op_id='CGL' "
    sql += r"and t.site_type = 'BEOL' "
    sql += r"and t.mfg_day = to_date('"+ date +"','yyyy/mm/dd') "
    sql += r"and t.test_user in ('"+ eqp +"') "
    #sql += r"and t.grade in ('3','W','X') "
    sql += r"and t.grade not in ('G') "
    sql += r"and t.defect_code_desc <> 'OTHER TFT DEFECT' "
    sql += r"and to_char(t.test_time,'HH24') = '" + hour +"' " 
    sql += r"order by t.defect_code_desc "
    
    
    defect_spec = 'aaa'
    grade_spec = 'aaa'
    count = 0
    df_goHours_raw = ora2df(sql)
    print(df_goHours_raw)
    nums0 = len(df_goHours_raw)
    # 另外算w組成
    for i in range(len(df_goHours_raw)):
        defect = df_goHours_raw.loc[i]['DEFECT_CODE_DESC'] 
        grade = df_goHours_raw.loc[i]['GRADE'] 
        df_goHours_raw.loc[i, 'NG_COUNT'] = 0 
        if defect == defect_spec and grade == grade_spec:
            count += 1
            
        else:
            #排除 第一次
            if i >= 1:
                df_goHours_raw.loc[i-1, 'NG_COUNT'] = count
                df_goHours_raw.loc[i-1, 'NG_RATIO'] = str(count/tot*100)[0:4]+' %'
            defect_spec = defect
            grade_spec = grade
            count = 1
    # 最後一筆 額外加入總數
    df_goHours_raw.loc[nums0-1, 'NG_COUNT'] = count
    df_goHours_raw.loc[nums0-1, 'NG_RATIO'] = str(count/tot*100)[0:4]+' %'
    
    
    imgLinks=[]
    for i in range(len(df_goHours_raw)):
        # 補上mfg_day
        df_goHours_raw.loc[i, 'MFG_DAY'] = date
        list0 = []
        list0.append(' ')
        list0.append(' ')    
        list0.append(' ')  
        imgLinks.append(list0)
    
    #imgLinks = ct1SearchImg(df_goHours_raw)
    
    return render_template('userMain.html', user=str(user),name=name, auth=auth, shift=shift, sectShow=sectShow, df_goHours_raw=df_goHours_raw, hour=hour)
    
# ct1 良率raw data
def ct1DefectImg(user,name, auth, shift, date1, date2, model_no, defect, eqp, isGoHours, go_hour):
    if user != 'Public':
        sectShow = 'ct1_chipidRaw'
    else:
        sectShow = 'ct1_summ2_chipid'
    print('  defect = '+defect)
    logging.info('  defect = '+defect)
    

    if defect == 'V_DEFECT':
        defect = r"V-OPEN', 'V-LINE', 'V-OPEN-BL"
    elif defect == 'H_DEFECT':
        defect = r"H-OPEN', 'H-LINE','H-BAND MURA"
    elif defect[:3] == 'AGM':
        defect = "AGM"
    elif defect == 'V_BAND_MURA':
        defect = "V-OPEN-BL"
    elif defect == 'H_BAND_MURA':
        defect = "H-BAND MURA"
        
    # 下載判圖記錄
    table = 'img_check_record'
    #df_img_record = mysql2df(table)
    sql = r"select *"
    sql += r" from craig01.img_check_record t"
    sql += r" where t.DEFECT_CODE_DESC in ('" + defect +"')"
    if eqp != '總數':
        sql += r" and t.MODEL_NO in ('" + model_no +"')"
    df_img_record = sql2df(sql)
        
        
    WHOLE_DEFECT_NAMES = ['BP', 'V-OPEN', 'V-LINE' , 'H-OPEN', 'H-LINE', 'X-SHORT', 'V-OPEN-BL', 'H-BAND MURA', 'WHITE SPOT', 'BLACK SPOT', 'AROUND GAP MURA', 'OTHER ALIGN DEFECT', 'OTHER APPEAR DEFECT',
                                  'OTHER GLASS DEFECT', 'DP', 'DP-PAIR', 'DP-CLUSTER', '3DP-ADJ', 'DP-NEAR', 'BP-PAIR', 'SMALL BP', 'PD13 ',   'POINT-COUNT']   
    #NON_MAJOR_DEFS = ['WHITE SPOT', 'DP-PAIR']
    NON_MAJOR_DEFS = [ 'DP-PAIR']
    others_nondef = str(WHOLE_DEFECT_NAMES)[1:-1]
    mysql = r""
    mysql += r"select a.chipid, a.test_time, a.model_no, a.test_user, a.defect_code_desc, a.x, a.y, a.pattern_code, b.img_file_path, b.img_file_name "
    mysql += r"from ( "
    mysql += r"select t.tft_chip_id as chipid, t.test_time ,t.model_no, t.test_user, t.defect_code_desc, "
    mysql += r"max(t.test_signal_no) as x,max(t.test_gate_no) as y, t.pattern_code "
    mysql += r"from celods.h_dax_fbk_defect_ods t "
    mysql += r"where t.test_mfg_day between to_date('" +date1+ "','YYYY/mm/DD') and to_date('" +date2+ "','YYYY/mm/DD') " 
    mysql += r"and t.test_op_id = 'CGL' "
    if defect == 'OTHERS':
        mysql += r"and t.defect_code_desc not in (" +others_nondef+ ") " 
    else: 
        mysql += r"and t.defect_code_desc in ('" +defect+ "') " 
    if eqp != '總數':
        mysql += r"and t.model_no='" +model_no+ "' " 
        mysql += r"and t.test_user in ('" +eqp+ "') " 
    #if defect not in NON_MAJOR_DEFS:
        #print("非major defect")
    mysql += r"and t.major_defect_flag = 'Y' "
    #mysql += r"and t.grade not in ('G') " 
    mysql += r"and t.judge_flag = 'L' "
    if isGoHours:
        mysql += r"and to_char(t.test_time,'HH24')='" + go_hour + "' "
    mysql += r"group by t.tft_chip_id,t.test_time,t.model_no, t.test_user,t.defect_code_desc,t.pattern_code "
    mysql += r" order by t.test_time "
    mysql += r") a "
    mysql += r"Left Join ( "
    mysql += r"select t2.img_file_path, t2.img_file_name, t2.tft_chip_id as chipid, t2.test_signal_no as xx, t2.test_gate_no as yy "
    mysql += r"from celods.h_dax_fbk_defect_ods t2 "
    mysql += r"where t2.test_mfg_day between to_date('" +date1+ "','YYYY/mm/DD') and to_date('" +date2+ "','YYYY/mm/DD') " 
    mysql += r"and t2.test_op_id = 'CGL' " 
    if defect == 'OTHERS':
        mysql += r"and t2.defect_code_desc not in (" +others_nondef+ ") " 
    else: 
        mysql += r"and t2.defect_code_desc in ('" +defect+ "') " 
    
    if eqp != '總數':
        mysql += r"and t2.model_no='" +model_no+ "' " 
        mysql += r"and t2.test_user in ('" +eqp+ "') "
    #if defect not in NON_MAJOR_DEFS:
    mysql += r"and t2.major_defect_flag = 'Y' "
    #mysql += r"and t2.grade not in ('G') " 
    mysql += r"and t2.judge_flag = 'L' "
    if isGoHours:
        mysql += r"and to_char(t2.test_time,'HH24')='" + go_hour + "' "
    #if defect == 'BP-PAIR':
    #    mysql += r") b on a.chipid=b.chipid and abs(a.x-b.xx) < 5 and abs(a.y-b.yy) < 5 "
    
    mysql += r") b on a.chipid=b.chipid and a.x=b.xx and a.y=b.yy "
    logging.info(mysql)
    try:
        ct1_summ2_chipid = ora2df(mysql)
    except:
        logging.info('<h1>ora2df失敗</h1>')
        return '<h1>ora2df失敗</h1>'
    if defect == 'BP-PAIR':
        drops = []
        for i in ct1_summ2_chipid.index[:-1]:
            chipid0 = ct1_summ2_chipid.loc[i]['CHIPID']
            x0 = ct1_summ2_chipid.loc[i]['X']
            y0 = ct1_summ2_chipid.loc[i]['Y']
            chipid1 = ct1_summ2_chipid.loc[i+1]['CHIPID']
            x1 = ct1_summ2_chipid.loc[i+1]['X'] 
            y1 = ct1_summ2_chipid.loc[i+1]['Y']
            if chipid0 == chipid1 and abs(x0-x1) <= 5 and abs(y0-y1) <= 5:
                drops.append(i)
        if len(drops) > 0:
            ct1_summ2_chipid.drop(drops, inplace=True)
            ct1_summ2_chipid.reset_index(drop=True, inplace=True)
            
    
    pd.set_option('display.max_colwidth', None)
    #找圖ya
    #影像分成３個ｃｃｄ　依序放置ｌｉｓｔ　　３ x ｎ大小
    imgLinks = []
    l7ah1_imgs = []
    ct1_summ2_chipid['Check'] = 'N'
    ct1_summ2_chipid['Check_Name'] = None
    for i in range(len(ct1_summ2_chipid)):
        # 三顆ccd影像list初始化，三顆找完之後包進imgLinks中
        
        list0 = []
        chipid = ct1_summ2_chipid.loc[i]['CHIPID']
        time00 = str(ct1_summ2_chipid.loc[i]['TEST_TIME'])[11:13]
        time35 = int(str(ct1_summ2_chipid.loc[i]['TEST_TIME'])[14:16])
        test_time_str = str(ct1_summ2_chipid.loc[i]['TEST_TIME'])
        test_date = test_time_str[0:4]+test_time_str[5:7]+test_time_str[8:10]
        #ct1_summ2_chipid.loc[i, 'Check'] = 'N'
        #ct1_summ2_chipid.loc[i, 'Check_Name'] = None
        defect = ct1_summ2_chipid.loc[i]['DEFECT_CODE_DESC']
        eqp = ct1_summ2_chipid.loc[i]['TEST_USER']
        pt = ct1_summ2_chipid.loc[i]['PATTERN_CODE']
        model_no0 = ct1_summ2_chipid.loc[i]['MODEL_NO']
        # http://10.97.212.139/cccgl2031/D/20211202/12/#:~:text=1569606-,CBLX1JA_1F.jpg
        dict_h1ips = {}
        dict_h1ips['CCCGL1'] = r'http://10.97.213.97/cccgl1031/D/'
        dict_h1ips['CCCGL2'] = r'http://10.97.212.139/cccgl2031/D/'
        dict_h1ips['CCCGL3'] = r'http://10.97.212.184/cccgl3031/D/'
        dict_h1ips['CCCGL4'] = r'http://10.97.212.182/cccgl4031/D/'
        dict_h1ips['CCCGL5'] = r'http://10.97.213.108/cccgl5031/D/'
        dict_h1ips['CCCGL6'] = r'http://10.97.213.125/cccgl6031/D/'
        dict_h1ips['CCCGL7'] = r'http://10.97.213.127/cccgl6031/D/'
        dict_h1ips['CCCGL8'] = r'http://10.97.212.211/cccgl8031/D/'
        
        dict_h1ips['CCCGL9'] = r'http://10.97.212.136/cccgl9061/D/'
        dict_h1ips['CCCGLA'] = r'http://10.97.212.188/cccglA061/D/'
         
        
        if user == 'Public':
            
            l7ah1_times = []
            if int(time00) <= 0:
                l7ah1_times = [time00]
            else:
                l7ah1_times = [str(int(time00)-1).zfill(2), time00]
            
            link = []
            proxies = {'http':'http://10.97.4.1:8080'}
            if eqp is not None and eqp[:6] in dict_h1ips.keys():
                l7ah1_link0 = dict_h1ips[eqp[:6]]
                for t in l7ah1_times:
                    l7ah1_link = l7ah1_link0 + test_date + r"/"+ t + r"/" + chipid + "_1F.jpg"
                    r = req2(l7ah1_link, proxies=proxies)
                    if r.status_code == 200:
                        link = [l7ah1_link]
                        break
            l7ah1_imgs.append(link)
                
        # IMG_FILE_PATH可能為 none
        try:
            ora_imgpath = ct1_summ2_chipid.loc[i]['IMG_FILE_PATH']+ct1_summ2_chipid.loc[i]['IMG_FILE_NAME']
        except:
            ora_imgpath = 'NNNNNNNNNNNNN'
        
        # 找判片記錄
       
        #df0 = df_img_record[(df_img_record['CHIPID']== chipid) & (df_img_record['DEFECT_CODE_DESC']==defect)& (df_img_record['MODEL_NO']==model_no0)]
        df0 = df_img_record[(df_img_record['CHIPID']== chipid) ]
        
        # 下面這一項是yield summary篩選方法
        #df0 = df_img_record[(df_img_record['TEST_TIME_MFG'].isin(mfg_days)) & (df_img_record['TEST_USER']==line0)& (df_img_record['MODEL_NO']==model_no0)]
        #df0.drop_duplicates(['CHIPID','PATTERN_CODE'], keep='last', inplace=True)
        if len(df0) > 0:
            last_n = df0.index[-1]
            ct1_summ2_chipid.loc[i, 'Check'] = df_img_record.loc[last_n]['imgCheck']
            ct1_summ2_chipid.loc[i, 'Check_Name'] = df_img_record.loc[last_n]['name']
            ct1_summ2_chipid.loc[i, 'imgCheckRemarks'] = df_img_record.loc[last_n]['imgCheckRemarks']
            
        
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
        elif time35 <= 7 and eqp in ['CCCGL8083']:
            chipid_times = [str(int(time00)-1).zfill(2)]
        elif time35 <= 3 and eqp not in ['CCCGL1083']:
            chipid_times = [str(int(time00)-1).zfill(2)]
        else:
            chipid_times = [time00]#, str(int(time00)-1).zfill(2)]
        print(chipid_times)
        #判斷pattern code最後一字是否為數字時使用
        strlist_num = []
        for num in range(0,10):
            strlist_num.append(str(num))
        
        # BP (選BMP)http://tcweb002.corpnet.auo.com/CCCGL7082/AOI%20Data/Defect_Image/Sub3/20210908/08/Defect/
        # H-open http://tcweb002.corpnet.auo.com/CCCGL6082/AOI%20Data/Defect_Image/Sub1/20210908/08/Defect/C8CL3CC_C1_PWHITE_TDP_D10327_G4.bmp
        # V-LINE 疑似沒圖
        
        # v open http://tcweb002.corpnet.auo.com/CCCGL8082/AOI%20Data/Defect_Image/Sub2/20210908/07/Defect/
        subDefect_list = ['BP', 'H-OPEN', 'H-LINE', 'V-OPEN', 'V-LINE', 'X-SHORT', 'BP-PAIR', 'DP-NEAR']      
        ag_list = ['V-OPEN-BL', 'AROUND GAP MURA', 'WHITE SPOT', 'BLACK SPOT', 'H-BAND MURA']
        AO7_list = ['CCCGLA072', 'CCCGLA073']
        AO7Def_list = ['OTHER ALIGN DEFECT', 'OTHER GLASS DEFECT', 'OTHER APPEAR DEFECT']
        
        
        
        if eqp == '總數':
            list0.append(' ')
            list0.append(' ')    
            list0.append(' ')    
        elif defect in subDefect_list:
            logging.info('  '+chipid+', Pattern Code = '+str(subDefect_list))
            list0 = subDefect(eqp, chipid, test_date, chipid_times, defect, pt)
        
        elif defect in ag_list:
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
                    if pt is not None:    
                        img_path = path0 + chipid +'_C'+ ag[-2] + '_P'+ str(pt) + '_FMura_S' + ag[-2] + '_WithDefect.bmp'
                    else:
                        img_path = ''
                    list0.append(img_path)
                                #break
                if len(list0) != ccd_num:
                    list0.append(' ')
        
        elif eqp in AO7_list and defect in AO7Def_list and 0:
            1
            #imguri = "http://tcweb002.corpnet.auo.com/" & test_user & "/AOI Data/Defect_Image/" & "AreaGrabber" & i & "/" & test_time & "/Source/"
            
            #imguri = "http://tcweb002.corpnet.auo.com/" & test_user & "/AOI Data/Ori_Image/" & "AreaGrabber" & i & "/" & test_time & "/Source/"
            

        
        # OAD有獨立存圖區  位置跟L模式很像
        elif defect in ['OTHER ALIGN DEFECT']:
            times = []
            for j in range(11):
               times.append(str(j).rjust(2,'0'))
            
            subs = ['Sub1/', 'Sub2/', 'Sub3/']
            for sub in subs:
                for time0 in chipid_times:
                    pathImgs = [r'http://tcweb002.corpnet.auo.com/',  eqp,
                        r'/AOI%20Data/Defect_Image/',        ['Sub1/', 'Sub2/', 'Sub3/'],
                        test_date,     time0,
                        '/OtherAlign/']
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
                            # 多張的話，秀一張就好(坐標資料皆為0,0 無法查找)
                            break
                if len(list0) != int(sub[-2]):
                    list0.append(' ')
        elif ct1_summ2_chipid.loc[i]['PATTERN_CODE'] is None:
            list0.append(' ')
            list0.append(' ')    
            list0.append(' ')
            #暫不找圖
        # L模式 (OGD)
        elif pt[0] == 'L' and pt not in ['LD']:
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
                    if pt[0:3] == 'LW2':
                        img = chipid + '_C' + sub[-2] + '_PWHITE.tif'
                        list0.append(path0+img)
                        break
                    elif pt[0:2] == 'LB':
                        img = chipid + '_C' + sub[-2] + '_PBLACK.tif'
                        list0.append(path0+img)
                        break
                    elif pt[0:3] == 'LW4':
                        img = chipid + '_C' + sub[-2] + '_PB48L.tif'
                        list0.append(path0+img)
                        break
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
        elif ct1_summ2_chipid.loc[i]['DEFECT_CODE_DESC'] == 'OTHER GLASS DEFECT' and (pt[0] == 'M' or pt in ['RD', 'LD']):    
            logging.info('  '+chipid+', Pattern Code = OGD+M模式')
            print('OGD特殊狀況進入')
            #http://tcweb002.corpnet.auo.com/CCCGL2082/AOI%20Data/Defect_Image/AreaGrabber1/20211011/01/Source/C9CV8CD_C1_PM_R_FMura_S1_0.bmp
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
                    # C9CV8CD_C1_PM_R_FMura_S1_0.bmp  C9B29VD_C1_PM_LM_FMura_S1_0.bmp
                    if pt[:-1] in ['M_R', 'M_G', 'M_LM', 'M_HM']:
                        img = chipid + '_C' + ag[-2] + '_P' + pt[:-1] +'_FMura_S' + ag[-2] + '_0.bmp'
                        list0.append(path0+img)
                        break
                    # CAJ65DD_C3_PMHGO3_FMura_S3_0.bmp
                    elif pt == 'MHGO3':
                        # 也可能是MHGO 
                        #proxies = {'http':'http://10.97.4.1:8080'}
                        #web0 = 'http://tcweb002.corpnet.auo.com/CCCGL1082/AOI%20Data/Defect_Image/sub1/'
                        #req = req2(web0, proxies=proxies)
                        img = chipid + '_C' + ag[-2] + '_P' + pt[:] +'_FMura_S' + ag[-2] + '_0.bmp'
                        list0.append(path0+img)
                        break
                    elif pt == 'MHGOC':
                        # CBL81QA_C1_PM_HGO_FMura_S1_0.bmp
                        img = chipid + '_C' + ag[-2] + '_PM_' + pt[1:-1] +'_FMura_S' + ag[-2] + '_0.bmp'
                        list0.append(path0+img)
                        break
                    
                    #CBQH5SC_C1_PM_RD_FMura_S1_0.bmp
                    
                    elif pt in ['RD', 'LD']:
                        img = chipid + '_C' + ag[-2] + '_PM_'+ pt +'_FMura_S' + ag[-2] + '_0.bmp'
                        list0.append(path0+img)
                        break
                    
                    elif pt in ['M_201', 'M_100']:
                        img = chipid + '_C' + ag[-2] + '_P' + 'M_HM' +'_FMura_S' + ag[-2] + '_0.bmp'
                        list0.append(path0+img)
                        break
                    
                    else:
                        img = chipid + '_C' + ag[-2] + '_P' + pt[:-1] +'_FMura_S' + ag[-2] + '_0.bmp'
                        list0.append(path0+img)
                        break
                    
                    imgs_list = AUOFab_PathList(path0)[1]
                    #print(imgs_list)
                        #print(imgs_list)
                    for img in imgs_list:
                        if img[0:7] == chipid:
                            #print(path0+img)
                            
                            aaa = img.split('_', 4)
                            pc = ct1_summ2_chipid.loc[i]['PATTERN_CODE']
                            ptn_code = aaa[2][1:]+'_'+aaa[3]   
                            # strlist_num 判斷最後一個字是否為數字
                            if pc[-1] in strlist_num:
                                pc = pc[:-1]
                            print(ptn_code, pc)
                            logging.info('  找到chipid image:'+img+', '+ptn_code+' =? '+pc)
                            # 需為指定pattern code之影像
                            if pc == ptn_code:
                                
                                list0.append(path0+img)
                                # ˋ多圖找一張就好
                                break
                            
                    
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
    #ct1_summ2_chipid = ct1_summ2_chipid.reset_index()
    if user == 'Public':
        return render_template('publicMain.html', user=user,name=name, auth=auth, shift=shift, sectShow=sectShow, 
                               ct1_summ2_chipid=ct1_summ2_chipid, date1=date1, date2=date2,
                               imgLinks=imgLinks, l7ah1_imgs=l7ah1_imgs)

    else:
        # 判圖比例初始化
        #df_check = pd.DataFrame()
        ct1_summ2_chipid2= ct1_summ2_chipid.fillna({'Check_Name':'未確認'})
        ct1_summ2_chipid2.rename(columns={'Check_Name':'人員', 'Check':'結果'}, inplace=True)
        df_check = ct1_summ2_chipid2.groupby(['人員', '結果']).size().to_frame('片數')
        #df_check.to_csv('test.csv')
        
        df_check['比例(%)'] = 100*df_check['片數'] / len(ct1_summ2_chipid2)
        df_check = df_check.round(2).copy()
        
        #print(df_check)
        now0 = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return render_template('userMain.html', user=user,name=name, auth=auth, shift=shift, sectShow=sectShow, 
                               ct1_summ2_chipid=ct1_summ2_chipid, date1=date1, date2=date2, imgLinks=imgLinks, 
                               df_check=df_check, now0=now0)


def ct1ADC(user,name, auth, shift, date1, date2):
    sectShow = 'ct1ADC'
    # 計算運作時間
    start_time = datetime.datetime.now()
    
    
    df_ct1ADC = pd.DataFrame()
    
    sql = r" Select t.mfg_day , t.test_time , t.tool_id , t.product_code, t.model_no , t.tft_chip_id as chipid, t.pre_grade "
    sql += r" , t.grade , t.defect_code_desc , t.pre_defect_code_desc , B.Test_User as pre_test_user , t.abbr_no , b.test_time as pre_test_time "
    sql += r" from("
    sql += r" select *"
    sql += r" from celods.h_dax_fbk_test_ods t"
    sql += r" Where t.mfg_day between to_date('" + date1 + "','yyyy/mm/dd') and to_date('" + date2 + "','yyyy/mm/dd')"
    sql += r" and t.Site_Type = 'BEOL'"
    sql += r" and t.site_id = 'L11'"
    sql += r" and t.op_id = 'ADC2'"
    sql += r" and t.pre_grade in ('X','W')"
    sql += r" and t.abbr_no not like '%RK%'"
    sql += r" and t.pre_defect_code_desc like '%BP%'"
    sql += r" )t"
    sql += r" left join celods.h_dax_fbk_test_ods B on t.tft_chip_id = b.tft_chip_id"
    sql += r" and b.judge_cnt <t.judge_cnt"
    sql += r" and b.op_id = 'CGL'"
    raw_data0 = ora2df(sql)
    #raw_data0.drop_duplicates(['PRODUCT_CODE', 'CHIPID', 'PRE_TEST_USER'], keep='last', inplace=True)
    raw_data0.drop_duplicates(['CHIPID'], keep='first', inplace=True)
    
    raw_data0['時間差'] = (raw_data0['TEST_TIME'] - raw_data0['PRE_TEST_TIME'])
    raw_data0['時間差'] = raw_data0['時間差'].apply(lambda x: x.days)
    raw_data0 = raw_data0[raw_data0['時間差'] < 180].copy()
    raw_data0.reset_index(drop=True, inplace=True)
    raw_data0.drop(columns=['時間差'], inplace=True)
    
    raw_data0.fillna({'DEFECT_CODE_DESC':'   '}, inplace=True)
    raw_data1 = raw_data0.groupby(['PRODUCT_CODE', 'PRE_TEST_USER', 'DEFECT_CODE_DESC'])
    raw_data2 = raw_data1.size().to_frame(name='COUNT')
    raw_data2 = raw_data2.reset_index()
    
    #加總指定ｄｅｆｅｃｔ
    none_raw = raw_data2[(raw_data2['DEFECT_CODE_DESC'].str.contains('   '))]
    df_none = none_raw.groupby(['PRODUCT_CODE', 'PRE_TEST_USER'])['COUNT'].agg('sum').to_frame(name='NG片數')
    
    
    
      
    df_tot = raw_data2.groupby(['PRODUCT_CODE', 'PRE_TEST_USER'])['COUNT'].agg('sum').to_frame(name='總數')
      
    
    # 合併表格
    df_ct1ADC = pd.concat([df_none, df_tot], verify_integrity = True, axis=1)
    df_ct1ADC = df_ct1ADC.fillna(0)
    
    df_ct1ADC = df_ct1ADC.reset_index()
    
    df_ct1ADC[['NG片數']] = df_ct1ADC[['NG片數']].astype('int')

    df_ct1ADC['NG RATIO(%)'] = 100*df_ct1ADC['NG片數'] / df_ct1ADC['總數']
    df_ct1ADC['已確認'] = 0
    df_ct1ADC = df_ct1ADC.round(2)
    df_ct1ADC['Real_Ratio'] = 'N/A'
    
    
    df_ct1ADC[['NG片數']] = df_ct1ADC[['NG片數']].astype('int')
    
    
    
    table = 'img_check_record'
    db_data = mysql2df(table)
    
    
    for item in df_ct1ADC.index:
        
        ct1_user = df_ct1ADC.loc[item]['PRE_TEST_USER']
        pc = df_ct1ADC.loc[item]['PRODUCT_CODE']
        tot = df_ct1ADC.loc[item]['總數']
        if df_ct1ADC.loc[item]['NG片數'] == 0:
            continue
        defect = '   '
        df_ct1ADCRaw = raw_data0[(raw_data0['DEFECT_CODE_DESC'].str.contains(defect)) & (raw_data0['PRE_TEST_USER'] == ct1_user) & (raw_data0['PRODUCT_CODE'] == pc)]
        
        
        #octADCRBSucRaw = octADCRBSucRaw.reset_index()
        #octADCRBSucRaw['IMG'] = 'NA'
        # 紀錄查詢
        
        
        
        
        
        real_count = 0
        for i in df_ct1ADCRaw.index:
            chipid = df_ct1ADCRaw.loc[i]['CHIPID']
            date0 = str(df_ct1ADCRaw.loc[i]['TEST_TIME'])
            date_oct = date0[0:4] + date0[5:7] + date0[8:10]
            eqp_ct1 = df_ct1ADCRaw.loc[i]['PRE_TEST_USER']
            def_ct1 = df_ct1ADCRaw.loc[i]['PRE_DEFECT_CODE_DESC']
            
            #pre_test_user = octADCRBSuc.loc[i]['PRE_TEST_USER']
            
            df0 = db_data[(db_data['CHIPID']==chipid) & (db_data['TEST_USER']==eqp_ct1) & (db_data['DEFECT_CODE_DESC']==def_ct1)]
            if len(df0) > 0:
                last_n = df0.index[-1]
                okng = df0.loc[last_n]['imgCheck']
                df_ct1ADC.loc[item, '已確認'] = df_ct1ADC.loc[item]['已確認'] + 1
                if okng == 'R':
                    real_count += 1
        
        if df_ct1ADC.loc[item]['已確認'] > 0:
            df_ct1ADC.loc[item, 'Real_Ratio'] = round(100*real_count/df_ct1ADC.loc[item]['已確認'], 2)
                
    
    pc_list = df_ct1ADC.groupby(['PRODUCT_CODE']).size().index
    df_ct1ADC_list = []
    for pc0 in pc_list:
        df0 = df_ct1ADC[df_ct1ADC['PRODUCT_CODE'] == pc0]
        df0.reset_index(drop=True, inplace=True)
        df_ct1ADC_list.append(df0)
    df_ct1ADC = df_ct1ADC_list
    
    
    # 系統時間計算
    #start_time = datetime.datetime.now()
    end_time = datetime.datetime.now()
    
    spent_time = (end_time - start_time).total_seconds()
    df_DL = pd.DataFrame()
    df_DL.loc[0, 'MODE'] = 'CT1_ADC'
    df_DL.loc[0, 'USER'] = str(user)+str(name)
    df_DL.loc[0, 'START_TIME'] = start_time.strftime("%Y-%m-%d %H:%M:%S")
    df_DL.loc[0, 'END_TIME'] = end_time.strftime("%Y-%m-%d %H:%M:%S")
    df_DL.loc[0, 'SPEND_TIME'] = spent_time
    df_DL.loc[0, 'CHIPID_COUNT'] = -1
    table = 'dl_time'
    print(df_DL)
    df2mysql_append(df_DL, table)
    
    
    
    
    return render_template('userMain.html', user=user,name=name, auth=auth, shift=shift, sectShow=sectShow,
                           date1=date1, date2=date2, df_ct1ADC=df_ct1ADC)

def ct1ADCRaw(user,name, auth, shift, date1, date2, ct1_user, pc):
    print(date1, date2, ct1_user, pc)
    sectShow = 'ct1ADCRaw'
    
    df_ct1ADCRaw = pd.DataFrame()
    
    sql = r" Select t.mfg_day , t.test_time , t.tool_id , t.product_code, t.model_no , t.tft_chip_id as chipid, t.pre_grade "
    sql += r" , t.grade , t.defect_code_desc , t.pre_defect_code_desc , B.Test_User as pre_test_user , t.abbr_no , b.test_time as pre_test_time "
    sql += r" from("
    sql += r" select *"
    sql += r" from celods.h_dax_fbk_test_ods t"
    sql += r" Where t.mfg_day between to_date('" + date1 + "','yyyy/mm/dd') and to_date('" + date2 + "','yyyy/mm/dd')"
    sql += r" and t.Site_Type = 'BEOL'"
    sql += r" and t.site_id = 'L11'"
    sql += r" and t.op_id = 'ADC2'"
    sql += r" and t.pre_grade in ('X','W')"
    sql += r" and t.abbr_no not like '%RK%'"
    sql += r" and t.pre_defect_code_desc like '%BP%'"
    sql += r" )t"
    sql += r" left join celods.h_dax_fbk_test_ods B on t.tft_chip_id = b.tft_chip_id"
    sql += r" and b.judge_cnt <t.judge_cnt"
    sql += r" and b.op_id = 'CGL'"
    raw_data0 = ora2df(sql)
    #raw_data0.drop_duplicates(['PRODUCT_CODE', 'CHIPID', 'PRE_TEST_USER'], keep='last', inplace=True)
    raw_data0.drop_duplicates(['CHIPID'], keep='first', inplace=True)
    raw_data0['時間差'] = (raw_data0['TEST_TIME'] - raw_data0['PRE_TEST_TIME'])
    raw_data0['時間差'] = raw_data0['時間差'].apply(lambda x: x.days)
    raw_data0 = raw_data0[raw_data0['時間差'] < 180].copy()
    raw_data0.reset_index(drop=True, inplace=True)
    raw_data0.drop(columns=['時間差'], inplace=True)
    raw_data0.fillna({'DEFECT_CODE_DESC':'   '}, inplace=True)
    
    

    defect = '   '
    df_ct1ADCRaw = raw_data0[(raw_data0['DEFECT_CODE_DESC'].str.contains(defect)) & (raw_data0['PRE_TEST_USER'] == ct1_user) & (raw_data0['PRODUCT_CODE'] == pc)]
    
    
    #octADCRBSucRaw = octADCRBSucRaw.reset_index()
    #octADCRBSucRaw['IMG'] = 'NA'
    df_ct1ADCRaw['確認'] = 'NA'
    df_ct1ADCRaw['說明'] = 'NA'
    df_ct1ADCRaw['MFG_DAY'] = df_ct1ADCRaw['MFG_DAY'].astype('str')
    
    df_adc = df_ct1ADCRaw[['CHIPID']].copy()
    for i in df_ct1ADCRaw.index:
        
        model_no = df_ct1ADCRaw.loc[i]['MODEL_NO']
        chipid = df_ct1ADCRaw.loc[i]['CHIPID']
        eqp = df_ct1ADCRaw.loc[i]['PRE_TEST_USER']
        defect = df_ct1ADCRaw.loc[i]['PRE_DEFECT_CODE_DESC']
        img_list = DefectImg(date1, date2, model_no, defect, eqp, chipid)
        #df_ct1ADCRaw.loc[i, 'IMG1'] = str(img_list)
        for img_num in range(len(img_list)):
            if img_list[img_num] == ' ':
                df_ct1ADCRaw.loc[i, 'IMG'+str(img_num+1)] = ''
            else:
                df_ct1ADCRaw.loc[i, 'IMG'+str(img_num+1)] = r"<a href='"+img_list[img_num]+"'><img align='center' width='160' height='120' src='"+img_list[img_num]+"'  ></a>"
        
        # 找adc影像
        date00 = str(df_ct1ADCRaw.loc[i]['TEST_TIME'])
        date_oct= date00[0:4] + date00[5:7] + date00[8:10]
        eqp_oct = df_ct1ADCRaw.loc[i]['TOOL_ID']
        oct_def = ''
        octimgs = octDefectImg(chipid, date_oct, eqp_oct, oct_def)
        
        adc_img = octimgs[1]
         
        # 合併原表格版本
        for img in adc_img:
            1
            #img_html += r"<a href='"+img+"'><img align='center' width='160' height='120' src='"+img+"'  ></a>"
        #octADCRBRejRaw.loc[i, 'IMG'] = img_html
        
        for num0 in range(len(adc_img)):
            pattern= ""
            img_name = os.path.basename(adc_img[num0])
            spl = img_name.split('_')
            pattern = spl[3][1:]+'_'+spl[4] + '<br/>'
            img_html = pattern + r"<a href='"+adc_img[num0]+"'><img align='center' width='160' height='120' src='"+adc_img[num0]+"'  ></a>"
            df_adc.loc[i, 'IMG_'+str(num0)] = img_html
        
        
        
        
    
    
    # 紀錄查詢
    table = 'img_check_record'
    db_data = mysql2df(table)
    
    for i in df_ct1ADCRaw.index:
        chipid = df_ct1ADCRaw.loc[i]['CHIPID']
        date0 = str(df_ct1ADCRaw.loc[i]['TEST_TIME'])
        date_oct = date0[0:4] + date0[5:7] + date0[8:10]
        eqp_ct1 = df_ct1ADCRaw.loc[i]['PRE_TEST_USER']
        def_ct1 = df_ct1ADCRaw.loc[i]['PRE_DEFECT_CODE_DESC']
        
        #pre_test_user = octADCRBSuc.loc[i]['PRE_TEST_USER']

        
        df0 = db_data[(db_data['CHIPID']==chipid) & (db_data['TEST_USER']==eqp_ct1) & (db_data['DEFECT_CODE_DESC']==def_ct1)]
        if len(df0) > 0:
            last_n = df0.index[-1]
            #df0.drop_duplicates(['CHIP_ID', 'OCT_DEFECT'], keep='last', inplace=True)
            okng = df0.loc[last_n]['imgCheck']
            remarks = df0.loc[last_n]['name']+', '+df0.loc[last_n]['imgCheckRemarks']
            df_ct1ADCRaw.loc[i, '確認'] = okng
            df_ct1ADCRaw.loc[i, '說明'] = remarks
        
    #df_ct1ADCRaw.drop(columns=['MFG_DAY'], inplace=True)
    df_ct1ADCRaw = df_ct1ADCRaw.reset_index(drop=True)
    
    
    
    
    return render_template('userMain.html', user=str(user),name=name, auth=auth, shift=shift, sectShow=sectShow,
                           date1=date1, date2=date2, df_ct1ADCRaw= df_ct1ADCRaw)


def ct1ADC_Upload(user,name, auth, shift, req_list):
    
    #返回第一層
    sectShow = 'ct1ADC'
    #sectShow = 'uploadOK'
    
    #df_dp2bp = pd.DataFrame(columns=['user', 'name', 'shift', 'auth'])
    table = 'img_check_record'
    db_data = mysql2df(table)
    db_ct1ADC = pd.DataFrame(columns=db_data.columns)
    newIdx = len(db_ct1ADC)
    #newIdx = 0
    now_hm = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    for item in req_list:
        if '__' not in item:
            continue
        
        req = request.form.get(item)
        try:
            aaa = item.split('__',2)
            num = int(aaa[0])
            col = aaa[1]
            
        except:
            continue 
        
        
        
        # 轉換為yield summary欄位
        if col in ['DEFECT_CODE_DESC', 'TEST_TIME', 'TEST_USER']:
            #　這項是oct的defect
            continue
        elif col == 'PRE_DEFECT_CODE_DESC':
            col = 'DEFECT_CODE_DESC'
        
        elif col == 'PRE_TEST_TIME':
            col = 'TEST_TIME'
        elif col == 'PRE_TEST_USER':
            col = 'TEST_USER'
        
        if col in db_ct1ADC.columns:
            db_ct1ADC.loc[newIdx+num, col] = req
        #　imgCheck'為每一個Ｉｄ的最後一項
        1
    # 個別補上個人資訊
    user_list = ['user', 'name', 'shift', 'auth']
    drop_list = []
    for m in db_ct1ADC.index:
        
        for ii in user_list:
            req = request.form.get(ii)
            db_ct1ADC.loc[m, ii] = req
        
        db_ct1ADC.loc[m, 'Checked_Date'] = now_hm

        imgCheck = db_ct1ADC.loc[m]['imgCheck']
        if imgCheck is None or pd.isna(imgCheck):
            drop_list.append(m)
        if 'TEST_TIME_MFG' in db_ct1ADC.columns:
        # 新增MFG DATE轉換資訊
            test_time = db_ct1ADC.loc[m]['TEST_TIME']
            db_ct1ADC.loc[m,'TEST_TIME_MFG'] = testTime2MFG(str(test_time))
           
    
    
        # 新增MFG DATE轉換資訊
        #test_time = df_dp2bp.loc[newIdx+m]['TEST_TIME']
        #df_dp2bp.loc[newIdx+m,'TEST_TIME_MFG'] = testTime2MFG(str(test_time))
        
    db_ct1ADC = db_ct1ADC.drop(drop_list)
    #db_ADCRBSuc.reset_index(inplace=True, drop=True)
    #db_ADCRBSuc = db_ADCRBSuc.drop(columns=['Check'])
    print(db_ct1ADC)
    df2mysql_append(db_ct1ADC, table)
    
    
    date1 = request.form.get('date1')
    date2 = request.form.get('date2')
    
    return ct1ADC(user,name, auth, shift, date1, date2)
    
    
    
    

def ct1IDS(user,name, auth, shift, chipids):
    sectShow = 'ct1IDS'
    defect = request.form.get("ct1IDS_defect")
    print('defect',defect)
    txt0 = request.form.get("ct1IDS_chipids")
    if txt0 is None:
        txt0 = ""
    #print(txt0)
    chipids = []
    word_lines = txt0.splitlines()
    txt0 = ""
    for line0 in word_lines:
        #print(line0)
        spl0 = line0.split(' ')
        print('數量', len(spl0))
        if len(spl0) < 3:
            spl0 = line0.split('	')	
        if len(spl0) > 2 and len(spl0[2]) == 7 and spl0[2][0] == 'C':
            chipid = spl0[2]
            txt0 += chipid + "\n"
            print(chipid)
            chipids.append(chipid)
            
        elif len(spl0[0]) > 0 and spl0[0][0] == 'C' and len(spl0[0]) == 7 and spl0[0][0:4] != 'Chip':
            chipid = spl0[0]
            txt0 += chipid + "\n"
            print(chipid)
            chipids.append(chipid)
    print('----------------------------')
    aaa = r"r'"+ str(txt0) +"'"
    txt0 += '共計'+str(len(chipids))+ '片'
    
    
    
    sql_chipids = str(chipids)[1:-1]
    if len(chipids) != 0:
        print(sql_chipids)
        sql = r"select t.tft_glass_id as sheet_id, t.tft_chip_id as chipid,"
        sql += r" t.test_tool_id as tool_id, t.test_user," 
        sql += r" t.model_no, t.test_time, t.defect_code_desc as defect"
        sql += r" , t.test_signal_no as addressx, t.test_gate_no as addressy, t.defect_value, t.pattern_code"
        #sql += r" --t.test_op_id, t.test_time, t.test_user, t.test_judge_cnt, "
        sql += r" from celods.h_dax_fbk_defect_ods t"
        sql += r" where t.tft_chip_id in ("+ sql_chipids +")"
        #--and t.test_tool_id = 'CCCGL208'
        sql += r" and t.test_op_id='CGL'"
        sql += r" and t.defect_code_desc='"+str(defect)+"'"
        sql += r" order by t.tft_chip_id"
        ct1IDS = ora2df(sql)
        ct1IDS.drop_duplicates(['CHIPID'], keep='last', inplace=True)
        
        ct1IDS['確認'] = 'N/A'
        ct1IDS['備註'] = 'N/A'
        
        
        
        
        imgLinks = []
        df_check = pd.DataFrame()
        
        
        table= "img_check_record"
        #df_img_record = mysql2df(table)
        
        sql = r"select *"
        sql += r" from craig01.img_check_record t"
        sql += r" where t.DEFECT_CODE_DESC ='" + defect + "'"
        df_img_record = sql2df(sql)
            
        
        
        
        # 找圖和比對舊資料
        for idx0 in ct1IDS.index:
            chipid0 = ct1IDS.loc[idx0]['CHIPID']
            eqp0 = ct1IDS.loc[idx0]['TEST_USER']
            model_no0 = ct1IDS.loc[idx0]['MODEL_NO']
            #DefectImg(date1, date2, model_no, defect, eqp, chipid)
            if chipid0 == 'C51R9LB':
                print('debug id:')
                
            #判片紀錄查找
            
            #df0 = df_img_record[(df_img_record['CHIPID']== chipid0) & (df_img_record['DEFECT_CODE_DESC']==defect)& (df_img_record['MODEL_NO']==model_no0)]
            df0 = df_img_record[(df_img_record['CHIPID']== chipid0) & (df_img_record['MODEL_NO']==model_no0)]
            # 下面這一項是yield summary篩選方法
            #df0 = df_img_record[(df_img_record['TEST_TIME_MFG'].isin(mfg_days)) & (df_img_record['TEST_USER']==line0)& (df_img_record['MODEL_NO']==model_no0)]
            #df0.drop_duplicates(['CHIPID','PATTERN_CODE'], keep='last', inplace=True)
            if len(df0) > 0:
                last_n = df0.index[-1]
                ct1IDS.loc[idx0, '確認'] = df_img_record.loc[last_n]['imgCheck']
                
                ct1IDS.loc[idx0, '備註'] = df_img_record.loc[last_n]['imgCheckRemarks'] +' by '+df_img_record.loc[last_n]['name']
                ct1IDS.loc[idx0, 'IMG_0'] = "已完成"
                ct1IDS.loc[idx0, 'IMG_1'] = ""
                ct1IDS.loc[idx0, 'IMG_2'] = ""
                continue
            
            
            
            img_list = ct1DefectImg2(defect, eqp0, chipid0)
            #imgLinks.append(img_list)
            skip_n= 0
            for num0 in range(len(img_list)):
                if img_list[num0][-4:] == '.tif':
                    ct1IDS.loc[idx0, 'IMG_'+str(num0-skip_n)] = "<a href=\""+img_list[num0]+"\">CCD"+str(num0)+"</a>"
                else:
                    html0 = "<a href=\"javascript:PopupPic('"+img_list[num0]+"')\">"
                    ct1IDS.loc[idx0, 'IMG_'+str(num0-skip_n)] = html0 + "<img align='center' width='160' height='120' src='"+ img_list[num0] +"'"+">"
                       
                    
                
    else:
         # 左側選單進入 初始化
         ct1IDS = pd.DataFrame()            
         df_check = pd.DataFrame()  
         imgLinks = []
         txt0 = ""
    #print(imgLinks)
    #print(exec(aaa))
    return render_template('userMain.html', user=user,name=name, auth=auth, shift=shift, sectShow=sectShow,
                      txt0=txt0, defect=defect, ct1IDS=ct1IDS, imgLinks=imgLinks, df_check=df_check)

# 簡易版 條件較少
def ct1DefectImg2(defect, eqp, chipid):
    if defect is None:
        defect = ""
    elif defect == 'V_DEFECT':
        defect = r"V-OPEN', 'V-LINE', 'V-OPEN-BL"
    elif defect == 'H_DEFECT':
        defect = r"H-OPEN', 'H-LINE','H-BAND MURA"
    elif defect[:3] == 'AGM':
        defect = "AGM"
        
    mysql = r""
    mysql += r"select a.chipid, a.test_time, a.model_no, a.test_user, a.defect_code_desc, a.x, a.y, a.pattern_code, b.img_file_path, b.img_file_name "
    mysql += r"from ( "
    mysql += r"select t.tft_chip_id as chipid, t.test_time ,t.model_no, t.test_user, t.defect_code_desc, "
    mysql += r"max(t.test_signal_no) as x,max(t.test_gate_no) as y, t.pattern_code "
    mysql += r"from celods.h_dax_fbk_defect_ods t "
    #mysql += r"where t.test_mfg_day between to_date('" +date1+ "','YYYY/mm/DD') and to_date('" +date2+ "','YYYY/mm/DD') " 
    # ||
    mysql += r"where t.test_op_id = 'CGL' "
    #mysql += r"and t.model_no='" +model_no+ "' " 
    mysql += r"and t.defect_code_desc in ('" +defect+ "') " 
    mysql += r"and t.test_user='" +eqp+ "' " 
    #mysql += r"and t.major_defect_flag = 'Y' "
    #mysql += r"and t.grade in ('W','X') " 
    mysql += r"and t.judge_flag = 'L' "
    mysql += r"and t.tft_chip_id='" +chipid+ "' "
    mysql += r"group by t.tft_chip_id,t.test_time,t.model_no, t.test_user,t.defect_code_desc,t.pattern_code "
    mysql += r") a "
    mysql += r"Left Join ( "
    mysql += r"select t2.img_file_path, t2.img_file_name, t2.tft_chip_id as chipid, t2.test_signal_no as xx, t2.test_gate_no as yy "
    mysql += r"from celods.h_dax_fbk_defect_ods t2 "
    #mysql += r"where t2.test_mfg_day between to_date('" +date1+ "','YYYY/mm/DD') and to_date('" +date2+ "','YYYY/mm/DD') " 
    mysql += r"where t2.test_op_id = 'CGL' " 
    #mysql += r"and t2.model_no='" +model_no+ "' " 
    mysql += r"and t2.defect_code_desc in ('" +defect+ "') " 
    mysql += r"and t2.test_user='" +eqp+ "' " 
    #mysql += r"and t2.major_defect_flag = 'Y' "
    #mysql += r"and t2.grade in ('W','X') " 
    mysql += r"and t2.judge_flag = 'L' "
    mysql += r") b on a.chipid=b.chipid and a.x=b.xx and a.y=b.yy "
    logging.info(mysql)
    try:
        ct1_summ2_chipid = ora2df(mysql)
        print('ct1簡易找圖資料:')
        print(ct1_summ2_chipid)
    except:
        return '<h1>ora2df 失敗</h1>'
    if chipid == 'C51R9LB':
        print('debug id:')
        print(ct1_summ2_chipid)

    pd.set_option('display.max_colwidth', None)
    
    list0 = []
    proxies = {'http':'http://10.97.4.1:8080'}
    for i in range(len(ct1_summ2_chipid)):
        # TccdvlistlAT]iimgLinks
        chipid = ct1_summ2_chipid.loc[i]['CHIPID']
        time00 = str(ct1_summ2_chipid.loc[i]['TEST_TIME'])[11:13]
        time35 = int(str(ct1_summ2_chipid.loc[i]['TEST_TIME'])[14:16])
        test_time_str = str(ct1_summ2_chipid.loc[i]['TEST_TIME'])
        test_date = test_time_str[0:4]+test_time_str[5:7]+test_time_str[8:10]
        ct1_summ2_chipid.loc[i, 'Check'] = 'N'
        defect = ct1_summ2_chipid.loc[i]['DEFECT_CODE_DESC']
        eqp = ct1_summ2_chipid.loc[i]['TEST_USER']
        pt = ct1_summ2_chipid.loc[i]['PATTERN_CODE']
        # IMG_FILE_PATHi none
        try:
            ora_imgpath = ct1_summ2_chipid.loc[i]['IMG_FILE_PATH']+ct1_summ2_chipid.loc[i]['IMG_FILE_NAME']
        except:
            ora_imgpath = 'NNNNNNNNNNNNN'
        
        

        # Wt  }o
        if ora_imgpath[2:12] == '10.10.10.4':
            print('to: 10.10.10.4!!!!!')
            logging.info('tbpo: 10.10.10.4!!!!!')
            #aaa = r'\\10.10.10.4\AOI Data\Defect_Image\Sub3\20211004\12\Defect\C95M6CC_C3_PB48L_TBP_D5268_G1941.bmp'
            aa = ora_imgpath[21:]
            imgPath = r'http://tcweb002.corpnet.auo.com/'+ eqp + r'/AOI%20Data'+aa
            list0.append(imgPath)
            continue
       
        chipid_times = []
        if time00 == '00':
            chipid_times = [time00]
        elif time35 <= 7 and eqp in ['CCCGL8083']:
            chipid_times = [str(int(time00)-1).zfill(2)]
        elif time35 <= 3 and eqp not in ['CCCGL1083']:
            chipid_times = [str(int(time00)-1).zfill(2)]
        else:
            chipid_times = [time00]#, str(int(time00)-1).zfill(2)]
        print(chipid_times)
        #P_pattern code@rO_r
        strlist_num = []
        for num in range(0,10):
            strlist_num.append(str(num))
        
        # BP (BMP)http://tcweb002.corpnet.auo.com/CCCGL7082/AOI%20Data/Defect_Image/Sub3/20210908/08/Defect/
        # H-open http://tcweb002.corpnet.auo.com/CCCGL6082/AOI%20Data/Defect_Image/Sub1/20210908/08/Defect/C8CL3CC_C1_PWHITE_TDP_D10327_G4.bmp
        # V-LINE S
        
        # v open http://tcweb002.corpnet.auo.com/CCCGL8082/AOI%20Data/Defect_Image/Sub2/20210908/07/Defect/
        subDefect_list = ['BP', 'H-OPEN', 'H-LINE', 'V-OPEN', 'V-LINE', 'X-SHORT', 'BP-PAIR']      
        ag_list = ['V-OPEN-BL', 'AROUND GAP MURA', 'WHITE SPOT', 'BLACK SPOT', 'H-BAND MURA']
        AO7_list = ['CCCGLA072', 'CCCGLA073']
        AO7Def_list = ['OTHER ALIGN DEFECT', 'OTHER GLASS DEFECT', 'OTHER APPEAR DEFECT']
        
        if defect in subDefect_list:
            logging.info('  '+chipid+', Pattern Code = '+str(subDefect_list))
            list0 = subDefect(eqp, chipid, test_date, chipid_times, defect, pt)
        
        elif defect in ag_list:
            #http://tcweb002.corpnet.auo.com/CCCGL8082/AOI%20Data/Ori_Image/AreaGrabber1/20211024/07/Source/CAGX6ZF_C1_PM_LB_FMura_S1_WithDefect
            #http://tcweb002.corpnet.auo.com/CCCGL8082/AOI%20Data/Ori_Image/AreaGrabber1/20211024/07/Source/CAGX6ZF_C1PM_LB_FMura_S1_WithDefect.bmp
            print('ag_listo')
            AGs = ['AreaGrabber1/', 'AreaGrabber2/', 'AreaGrabber3/']
            for ag in AGs:
                for time0 in chipid_times:
                    pathImgs = [r'http://tcweb002.corpnet.auo.com/',  eqp,
                                r'/AOI%20Data/Ori_Image/',        ['AreaGrabber1/', 'AreaGrabber2/', 'AreaGrabber3/'],
                                test_date,     time0,
                                '/Source/']
                    
                    path0 = pathImgs[0]+pathImgs[1]+pathImgs[2]+ ag + pathImgs[4]+'/'+pathImgs[5]+pathImgs[6]
                    #print(path0)
                    # CAGX6ZF_C1_PM_LB_FMura_S1_WithDefect.bmp
                    img_path = path0 + chipid +'_C'+ ag[-2] + '_P'+ str(pt) + '_FMura_S' + ag[-2] + '_WithDefect.bmp'
                    list0.append(img_path)
                                #break
        
        elif eqp in AO7_list and defect in AO7Def_list and 0:
            1
            #imguri = "http://tcweb002.corpnet.auo.com/" & test_user & "/AOI Data/Defect_Image/" & "AreaGrabber" & i & "/" & test_time & "/Source/"
            
            #imguri = "http://tcweb002.corpnet.auo.com/" & test_user & "/AOI Data/Ori_Image/" & "AreaGrabber" & i & "/" & test_time & "/Source/"
            

        
        # OADWs  mL
        elif defect in ['OTHER ALIGN DEFECT']:
            times = []
            for j in range(11):
               times.append(str(j).rjust(2,'0'))
            
            subs = ['Sub1/', 'Sub2/', 'Sub3/']
            for sub in subs:
                for time0 in chipid_times:
                    pathImgs = [r'http://tcweb002.corpnet.auo.com/',  eqp,
                        r'/AOI%20Data/Defect_Image/',        ['Sub1/', 'Sub2/', 'Sub3/'],
                        test_date,     time0,
                        '/OtherAlign/']
                    path0 = pathImgs[0]+pathImgs[1]+pathImgs[2]+ sub + pathImgs[4]+'/'+pathImgs[5]+pathImgs[6]
                    #print(path0)
                    imgs_list = AUOFab_PathList(path0)[1]
                    #print(imgs_list)
                        #print(imgs_list)
                    last_imgPath = ''
                    for img in imgs_list:
                        if img[0:7] == chipid:
                            print(path0+img)
                            logging.info('  chipid image:'+img)
                            last_imgPath = path0+img
                            #   hiAq@iNn(0,0 Lkd)
                    if last_imgPath != '':
                        list0.append(last_imgPath)
                    
        elif ct1_summ2_chipid.loc[i]['PATTERN_CODE'] is None:
            1
            #list0.append('PT None')
            #
        # L (OGD)
        elif ct1_summ2_chipid.loc[i]['PATTERN_CODE'][0] == 'L':
            logging.info('  '+chipid+', Pattern Code = L')
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
                    
                    if pt[0:3] == 'LW2':
                        img = chipid + '_C' + sub[-2] + '_PWHITE.tif'
                        #list0.append(path0+img)
                        req = req2(path0+img, proxies=proxies)
                        if req.status_code == 200:
                            list0.append(path0+img)
                        break
                    elif pt[0:2] == 'LB':
                        img = chipid + '_C' + sub[-2] + '_PBLACK.tif'
                        req = req2(path0+img, proxies=proxies)
                        if req.status_code == 200:
                            list0.append(path0+img)
                        break
                    elif pt[0:3] == 'LW4':
                        img = chipid + '_C' + sub[-2] + '_PB48L.tif'
                        req = req2(path0+img, proxies=proxies)
                        if req.status_code == 200:
                            list0.append(path0+img)
                        break
                    imgs_list = AUOFab_PathList(path0)[1]
                    
                    #print(imgs_list)
                        #print(imgs_list)
                    last_imgPath = ''
                    for img in imgs_list:
                        if img[0:7] == chipid:
                            print(path0+img)
                            logging.info('  chipid image:'+img)
                            last_imgPath = path0+img
                    if last_imgPath != '':
                        list0.append(last_imgPath)
                            #break
            
                
        # M
        #http://tcweb002.corpnet.auo.com/CCCGL1082/AOI%20Data/Ori_Image/AreaGrabber2/20210903/08/Source/C85T3YE_C2_PM_R_FMura_S2_WithDefect.bmp


        # @S: OGD  P_O_OGD
        elif ct1_summ2_chipid.loc[i]['DEFECT_CODE_DESC'] == 'OTHER GLASS DEFECT' and ct1_summ2_chipid.loc[i]['PATTERN_CODE'][0] == 'M':    
            logging.info('  '+chipid+', Pattern Code = OGD+M')
            print('OGDSpiJ')
            #http://tcweb002.corpnet.auo.com/CCCGL2082/AOI%20Data/Defect_Image/AreaGrabber1/20211011/01/Source/C9CV8CD_C1_PM_R_FMura_S1_0.bmp
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
                    # C9CV8CD_C1_PM_R_FMura_S1_0.bmp  C9B29VD_C1_PM_LM_FMura_S1_0.bmp
                    if pt[:-1] in ['M_R', 'M_G', 'M_LM', 'M_HM']:
                        img = chipid + '_C' + ag[-2] + '_P' + pt[:-1] +'_FMura_S' + ag[-2] + '_0.bmp'
                        list0.append(path0+img)
                        break
                    # CAJ65DD_C3_PMHGO3_FMura_S3_0.bmp
                    elif pt == 'MHGO3':
                        # ]iOMHGO 
                        img = chipid + '_C' + ag[-2] + '_P' + pt +'_FMura_S' + ag[-2] + '_0.bmp'
                        list0.append(path0+img)
                        break
                    elif pt == 'M_201':
                        img = chipid + '_C' + ag[-2] + '_P' + 'M_HM' +'_FMura_S' + ag[-2] + '_0.bmp'
                        list0.append(path0+img)
                        break
                    
                    else:
                        img = chipid + '_C' + ag[-2] + '_P' + pt[:-1] +'_FMura_S' + ag[-2] + '_0.bmp'
                        list0.append(path0+img)
                        break
                    
                    imgs_list = AUOFab_PathList(path0)[1]
                    #print(imgs_list)
                        #print(imgs_list)
                    for img in imgs_list:
                        if img[0:7] == chipid:
                            #print(path0+img)
                            
                            aaa = img.split('_', 4)
                            pc = ct1_summ2_chipid.loc[i]['PATTERN_CODE']
                            ptn_code = aaa[2][1:]+'_'+aaa[3]   
                            # strlist_num P_@rO_r
                            if pc[-1] in strlist_num:
                                pc = pc[:-1]
                            print(ptn_code, pc)
                            logging.info('  chipid image:'+img+', '+ptn_code+' =? '+pc)
                            # wpattern codev
                            if pc == ptn_code:
                                
                                list0.append(path0+img)
                                # h@iNn
                                break
                            
                    
                if len(list0) != int(ag[-2]):
                    list0.append(' ')
                    

        elif ct1_summ2_chipid.loc[i]['PATTERN_CODE'][0] == 'M':
            logging.info('  '+chipid+', Pattern Code = M')
            
            
            
            # @S: OGD  P_O_OGD
           
                
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
                            logging.info('  chipid image:'+img+', '+ptn_code+' =? '+pc)
                            # wpattern codev
                            if pc == ptn_code:
                                list0.append(path0+img)
                                #break
                if len(list0) != int(ag[-2]):
                    list0.append(' ')
        
                
        else:
            # bwd   T
            1    
    return list0




# ct1純找圖
def DefectImg(date1, date2, model_no, defect, eqp, chipid):
    if defect is None:
        defect = ""
    elif defect == 'V_DEFECT':
        defect = r"V-OPEN', 'V-LINE', 'V-OPEN-BL"
    elif defect == 'H_DEFECT':
        defect = r"H-OPEN', 'H-LINE','H-BAND MURA"
    elif defect[:3] == 'AGM':
        defect = "AGM"
    print(eqp)
    mysql = r""
    mysql += r"select a.chipid, a.test_time, a.model_no, a.test_user, a.defect_code_desc, a.x, a.y, a.pattern_code, b.img_file_path, b.img_file_name "
    mysql += r"from ( "
    mysql += r"select t.tft_chip_id as chipid, t.test_time ,t.model_no, t.test_user, t.defect_code_desc, "
    mysql += r"max(t.test_signal_no) as x,max(t.test_gate_no) as y, t.pattern_code "
    mysql += r"from celods.h_dax_fbk_defect_ods t "
    #mysql += r"where t.test_mfg_day between to_date('" +date1+ "','YYYY/mm/DD') and to_date('" +date2+ "','YYYY/mm/DD') " 
    # ||
    mysql += r"where t.test_op_id = 'CGL' "
    #mysql += r"and t.model_no='" +model_no+ "' " 
    mysql += r"and t.defect_code_desc in ('" +defect+ "') " 
    mysql += r"and t.test_user='" +eqp+ "' " 
    mysql += r"and t.major_defect_flag = 'Y' "
    mysql += r"and t.grade in ('W','X') " 
    mysql += r"and t.judge_flag = 'L' "
    mysql += r"and t.tft_chip_id='" +chipid+ "' "
    mysql += r"group by t.tft_chip_id,t.test_time,t.model_no, t.test_user,t.defect_code_desc,t.pattern_code "
    mysql += r") a "
    mysql += r"Left Join ( "
    mysql += r"select t2.img_file_path, t2.img_file_name, t2.tft_chip_id as chipid, t2.test_signal_no as xx, t2.test_gate_no as yy "
    mysql += r"from celods.h_dax_fbk_defect_ods t2 "
    #mysql += r"where t2.test_mfg_day between to_date('" +date1+ "','YYYY/mm/DD') and to_date('" +date2+ "','YYYY/mm/DD') " 
    mysql += r"where t2.test_op_id = 'CGL' " 
    mysql += r"and t2.model_no='" +model_no+ "' " 
    mysql += r"and t2.defect_code_desc in ('" +defect+ "') " 
    mysql += r"and t2.test_user='" +eqp+ "' " 
    mysql += r"and t2.major_defect_flag = 'Y' "
    mysql += r"and t2.grade in ('W','X') " 
    mysql += r"and t2.judge_flag = 'L' "
    mysql += r") b on a.chipid=b.chipid "
    logging.info(mysql)
    
    mysql = r"select t.tft_chip_id as chipid, t.test_time, t.model_no, t.test_user, t.defect_code_desc, t.test_signal_no as x, t.test_gate_no as y, t.pattern_code, t.img_file_path, t.img_file_name "
    #mysql = r"select *"
    mysql += r" from celods.h_dax_fbk_defect_ods t"
    mysql += r" where t.tft_chip_id='"+ chipid + "'"
    mysql += r" and t.major_defect_flag = 'Y' "
    mysql += r" and t.test_user='" +eqp+ "' " 
    mysql += r" and t.grade in ('W','X') " 
    mysql += r" and t.judge_flag = 'L' "
    
    try:
        ct1_summ2_chipid = ora2df(mysql)
        # Debug用
        
    except:
        logging.info('<h1>ora2df</h1>')
        return '<h1>ora2df</h1>'
    ct1_summ2_chipid.drop_duplicates(['CHIPID'], keep='last', inplace=True)
    
    pd.set_option('display.max_colwidth', None)
    #ya
    #v@m@@ x jp
    list0 = []
    proxies = {'http':'http://10.97.4.1:8080'}
    for i in ct1_summ2_chipid.index:
        # TccdvlistlAT]iimgLinks
        chipid = ct1_summ2_chipid.loc[i]['CHIPID']
        time00 = str(ct1_summ2_chipid.loc[i]['TEST_TIME'])[11:13]
        time35 = int(str(ct1_summ2_chipid.loc[i]['TEST_TIME'])[14:16])
        test_time_str = str(ct1_summ2_chipid.loc[i]['TEST_TIME'])
        test_date = test_time_str[0:4]+test_time_str[5:7]+test_time_str[8:10]
        ct1_summ2_chipid.loc[i, 'Check'] = 'N'
        defect = ct1_summ2_chipid.loc[i]['DEFECT_CODE_DESC']
        eqp = ct1_summ2_chipid.loc[i]['TEST_USER']
        pt = ct1_summ2_chipid.loc[i]['PATTERN_CODE']
        # IMG_FILE_PATHi none
        try:
            ora_imgpath = ct1_summ2_chipid.loc[i]['IMG_FILE_PATH']+ct1_summ2_chipid.loc[i]['IMG_FILE_NAME']
        except:
            ora_imgpath = 'NNNNNNNNNNNNN'
        
        

        # Wt  }o
        if ora_imgpath[2:12] == '10.10.10.4':
            print('to: 10.10.10.4!!!!!')
        
            aa = ora_imgpath[21:]
            imgPath = r'http://tcweb002.corpnet.auo.com/'+ eqp + r'/AOI%20Data'+aa
            sub_num = int(aa[17])
            
            if sub_num not in [1,2,3]:
                sub_num = 3
        #bbb = r'http://tcweb002.corpnet.auo.com/CCCGL1082/AOI%20Data/Defect_Image/Sub3/20211004/12/Defect/C95M6CC_C3_PB48L_TBP_D5268_G1941.bmp'
            for sub in [1,2,3]:
                if sub == sub_num:
                    list0.append(imgPath)
                else:
                    list0.append(' ')
            continue
        
        chipid_times = []
        if time00 == '00':
            chipid_times = [time00]
        elif time35 <= 6:
            chipid_times = [str(int(time00)-1).zfill(2)]
        else:
            chipid_times = [time00]#, str(int(time00)-1).zfill(2)]
        print(chipid_times)
        #P_pattern code@rO_r
        strlist_num = []
        for num in range(0,10):
            strlist_num.append(str(num))
        
        # BP (BMP)http://tcweb002.corpnet.auo.com/CCCGL7082/AOI%20Data/Defect_Image/Sub3/20210908/08/Defect/
        # H-open http://tcweb002.corpnet.auo.com/CCCGL6082/AOI%20Data/Defect_Image/Sub1/20210908/08/Defect/C8CL3CC_C1_PWHITE_TDP_D10327_G4.bmp
        # V-LINE S
        
        # v open http://tcweb002.corpnet.auo.com/CCCGL8082/AOI%20Data/Defect_Image/Sub2/20210908/07/Defect/
        subDefect_list = ['BP', 'H-OPEN', 'H-LINE', 'V-OPEN', 'V-LINE', 'X-SHORT', 'BP-PAIR']      
        ag_list = ['V-OPEN-BL', 'AROUND GAP MURA', 'WHITE SPOT', 'BLACK SPOT', 'H-BAND MURA']
        AO7_list = ['CCCGLA072', 'CCCGLA073']
        AO7Def_list = ['OTHER ALIGN DEFECT', 'OTHER GLASS DEFECT', 'OTHER APPEAR DEFECT']
        
        if defect in subDefect_list or ('BP' in defect):
            logging.info('  '+chipid+', Pattern Code = '+str(subDefect_list))
            list0 = subDefect(eqp, chipid, test_date, chipid_times, defect, pt)
        
        elif defect in ag_list:
            #http://tcweb002.corpnet.auo.com/CCCGL8082/AOI%20Data/Ori_Image/AreaGrabber1/20211024/07/Source/CAGX6ZF_C1_PM_LB_FMura_S1_WithDefect
            #http://tcweb002.corpnet.auo.com/CCCGL8082/AOI%20Data/Ori_Image/AreaGrabber1/20211024/07/Source/CAGX6ZF_C1PM_LB_FMura_S1_WithDefect.bmp
            print('ag_listo')
            AGs = ['AreaGrabber1/', 'AreaGrabber2/', 'AreaGrabber3/']
            for ag in AGs:
                for time0 in chipid_times:
                    pathImgs = [r'http://tcweb002.corpnet.auo.com/',  eqp,
                                r'/AOI%20Data/Ori_Image/',        ['AreaGrabber1/', 'AreaGrabber2/', 'AreaGrabber3/'],
                                test_date,     time0,
                                '/Source/']
                    
                    path0 = pathImgs[0]+pathImgs[1]+pathImgs[2]+ ag + pathImgs[4]+'/'+pathImgs[5]+pathImgs[6]
                    #print(path0)
                    # CAGX6ZF_C1_PM_LB_FMura_S1_WithDefect.bmp
                    print('bug檢查')
                    print(path0, chipid, ag[-2], pt)
                    print(ct1_summ2_chipid)
                    img_path = path0 + chipid +'_C'+ ag[-2] + '_P'+ str(pt) + '_FMura_S' + ag[-2] + '_WithDefect.bmp'
                    list0.append(img_path)
                                #break
        
        elif eqp in AO7_list and defect in AO7Def_list and 0:
            1
            #imguri = "http://tcweb002.corpnet.auo.com/" & test_user & "/AOI Data/Defect_Image/" & "AreaGrabber" & i & "/" & test_time & "/Source/"
            
            #imguri = "http://tcweb002.corpnet.auo.com/" & test_user & "/AOI Data/Ori_Image/" & "AreaGrabber" & i & "/" & test_time & "/Source/"
            

        
        # OADWs  mL
        elif defect in ['OTHER ALIGN DEFECT']:
            times = []
            for j in range(11):
               times.append(str(j).rjust(2,'0'))
            
            subs = ['Sub1/', 'Sub2/', 'Sub3/']
            for sub in subs:
                for time0 in chipid_times:
                    pathImgs = [r'http://tcweb002.corpnet.auo.com/',  eqp,
                        r'/AOI%20Data/Defect_Image/',        ['Sub1/', 'Sub2/', 'Sub3/'],
                        test_date,     time0,
                        '/OtherAlign/']
                    path0 = pathImgs[0]+pathImgs[1]+pathImgs[2]+ sub + pathImgs[4]+'/'+pathImgs[5]+pathImgs[6]
                    #print(path0)
                    imgs_list = AUOFab_PathList(path0)[1]
                    #print(imgs_list)
                        #print(imgs_list)
                    last_imgPath = ''
                    for img in imgs_list:
                        if img[0:7] == chipid:
                            print(path0+img)
                            logging.info('  chipid image:'+img)
                            last_imgPath = path0+img
                            #   hiAq@iNn(0,0 Lkd)
                    if last_imgPath != '':
                        list0.append(last_imgPath)
                    
        elif ct1_summ2_chipid.loc[i]['PATTERN_CODE'] is None:
            1
            #list0.append('PT None')
            #
        # L (OGD)
        elif ct1_summ2_chipid.loc[i]['PATTERN_CODE'][0] == 'L':
            logging.info('  '+chipid+', Pattern Code = L')
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
                    
                    if pt[0:3] == 'LW2':
                        img = chipid + '_C' + sub[-2] + '_PWHITE.tif'
                        #list0.append(path0+img)
                        req = req2(path0+img, proxies=proxies)
                        if req.status_code == 200:
                            list0.append(path0+img)
                        break
                    elif pt[0:2] == 'LB':
                        img = chipid + '_C' + sub[-2] + '_PBLACK.tif'
                        req = req2(path0+img, proxies=proxies)
                        if req.status_code == 200:
                            list0.append(path0+img)
                        break
                    elif pt[0:3] == 'LW4':
                        img = chipid + '_C' + sub[-2] + '_PB48L.tif'
                        req = req2(path0+img, proxies=proxies)
                        if req.status_code == 200:
                            list0.append(path0+img)
                        break
                    imgs_list = AUOFab_PathList(path0)[1]
                    
                    #print(imgs_list)
                        #print(imgs_list)
                    last_imgPath = ''
                    for img in imgs_list:
                        if img[0:7] == chipid:
                            print(path0+img)
                            logging.info('  chipid image:'+img)
                            last_imgPath = path0+img
                    if last_imgPath != '':
                        list0.append(last_imgPath)
                            #break
            
                
        # M
        #http://tcweb002.corpnet.auo.com/CCCGL1082/AOI%20Data/Ori_Image/AreaGrabber2/20210903/08/Source/C85T3YE_C2_PM_R_FMura_S2_WithDefect.bmp


        # @S: OGD  P_O_OGD
        elif ct1_summ2_chipid.loc[i]['DEFECT_CODE_DESC'] == 'OTHER GLASS DEFECT' and ct1_summ2_chipid.loc[i]['PATTERN_CODE'][0] == 'M':    
            logging.info('  '+chipid+', Pattern Code = OGD+M')
            print('OGDSpiJ')
            #http://tcweb002.corpnet.auo.com/CCCGL2082/AOI%20Data/Defect_Image/AreaGrabber1/20211011/01/Source/C9CV8CD_C1_PM_R_FMura_S1_0.bmp
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
                    # C9CV8CD_C1_PM_R_FMura_S1_0.bmp  C9B29VD_C1_PM_LM_FMura_S1_0.bmp
                    if pt[:-1] in ['M_R', 'M_G', 'M_LM', 'M_HM']:
                        img = chipid + '_C' + ag[-2] + '_P' + pt[:-1] +'_FMura_S' + ag[-2] + '_0.bmp'
                        list0.append(path0+img)
                        break
                    # CAJ65DD_C3_PMHGO3_FMura_S3_0.bmp
                    elif pt == 'MHGO3':
                        # ]iOMHGO 
                        img = chipid + '_C' + ag[-2] + '_P' + pt +'_FMura_S' + ag[-2] + '_0.bmp'
                        list0.append(path0+img)
                        break
                    elif pt == 'M_201':
                        img = chipid + '_C' + ag[-2] + '_P' + 'M_HM' +'_FMura_S' + ag[-2] + '_0.bmp'
                        list0.append(path0+img)
                        break
                    
                    else:
                        img = chipid + '_C' + ag[-2] + '_P' + pt[:-1] +'_FMura_S' + ag[-2] + '_0.bmp'
                        list0.append(path0+img)
                        break
                    
                    imgs_list = AUOFab_PathList(path0)[1]
                    #print(imgs_list)
                        #print(imgs_list)
                    for img in imgs_list:
                        if img[0:7] == chipid:
                            #print(path0+img)
                            
                            aaa = img.split('_', 4)
                            pc = ct1_summ2_chipid.loc[i]['PATTERN_CODE']
                            ptn_code = aaa[2][1:]+'_'+aaa[3]   
                            # strlist_num P_@rO_r
                            if pc[-1] in strlist_num:
                                pc = pc[:-1]
                            print(ptn_code, pc)
                            logging.info('  chipid image:'+img+', '+ptn_code+' =? '+pc)
                            # wpattern codev
                            if pc == ptn_code:
                                
                                list0.append(path0+img)
                                # h@iNn
                                break
                            
                    
                if len(list0) != int(ag[-2]):
                    list0.append(' ')
                    

        elif ct1_summ2_chipid.loc[i]['PATTERN_CODE'][0] == 'M':
            logging.info('  '+chipid+', Pattern Code = M')
            
            
            
            # @S: OGD  P_O_OGD
           
                
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
                            logging.info('  chipid image:'+img+', '+ptn_code+' =? '+pc)
                            # wpattern codev
                            if pc == ptn_code:
                                list0.append(path0+img)
                                #break
                if len(list0) != int(ag[-2]):
                    list0.append(' ')
        
                
        else:
            # bwd   T
            1    
    return list0


# oct單項找圖版
def octDefectImg(chipid, date_oct, eqp_oct, oct_def):
    octaoi_imgs = []
    octadc_imgs = []
    # 確認是否為有圖但找不到
    isOKDef = False
    isAOI = True
    isADC = True
    isCT1 = True
    isCT1D = False
    if eqp_oct in ['OTHER LINE DEFECT']:
        isAOI = True
        isADC = False
        isCT1 = True
        isCT1D = False
    elif oct_def in ['PAD CORROSION', 'OTHER APPEAR DEFECT', 'ABNORMAL DISPLAY']:
        isAOI = False
        isADC = False
        isCT1 = True
        isCT1D = False
    elif oct_def in ['OTHER GLASS DEFECT']:
        1
    #以下oct defect不用找aoi和adc影像
    if isOKDef:
        1#不找圖
    
    elif eqp_oct == 'CCOCT300':
        if isAOI:
            # AOI影像路徑
            web_mura = r"http://10.97.212.30/AOI_Data_D/GrabImage/Source/IP1/"+ date_oct +r"/"+ chipid+"/Mura/"
            web_func = r"http://10.97.212.30/AOI_Data_D/GrabImage/Source/IP1/"+ date_oct +r"/"+ chipid+"/FunctionError/"
               
            """
            imgs_path = AUOFab_PathList(web_mura)
            for img_idx in range(len(imgs_path[1])):
                if imgs_path[1][img_idx][-4:] in ['.bmp', '.BMP']:
                    octaoi_imgs.append(imgs_path[0][img_idx])
            """
            imgs_path = AUOFab_PathList(web_func)
            # 多圖對應表   會重覆蓋掉舊的
            imgs_dict = {}
            for img_idx in range(len(imgs_path[1])):
                if imgs_path[1][img_idx][-4:] in ['.tif', '.TIF']:
                    try:
                        spl = imgs_path[1][img_idx].split('_', 10)
                        spl_def1 = spl[4]
                        spl_def2 = spl[5]
                    except:
                        continue
                    imgs_dict[spl_def1+spl_def2] = img_idx
            maxXY_list = list(imgs_dict.values())
            #print(maxXY_list)
            for img_idx in maxXY_list:
                octaoi_imgs.append(web_func +'/'+imgs_path[1][img_idx])
        if isADC:
            # ADC影像路徑
            web_adc = r"http://10.97.212.30/AOI_Data_ADC/GrabImage/IP1/"+ date_oct +r"/"+ chipid+r"/"
            imgs_path = AUOFab_PathList(web_adc)
            for img_idx in range(len(imgs_path[1])):
                if imgs_path[1][img_idx][-4:] in ['.bmp', '.BMP']:
                    octadc_imgs.append(web_adc +'/'+imgs_path[1][img_idx])

    elif eqp_oct == 'CCOCT400':
        if isAOI:
            web_mura = r"http://10.97.212.99/AOI_Data_D/GrabImage/Defect/IP1/"+ date_oct +r"/"+ chipid+"/Mura/"
            web_func = r"http://10.97.212.99/AOI_Data_D/GrabImage/Defect/IP1/"+ date_oct +r"/"+ chipid+"/FunctionError/"
            
            """
            imgs_path = AUOFab_PathList(web_mura)
            for img_idx in range(len(imgs_path[1])):
                if imgs_path[1][img_idx][-4:] in ['.bmp', '.BMP']:
                    octaoi_imgs.append(web_mura +'/'+imgs_path[1][img_idx])
            """
            imgs_path = AUOFab_PathList(web_func)
            # 多圖對應表   會重覆蓋掉舊的
            imgs_dict = {}
            for img_idx in range(len(imgs_path[1])):
                if imgs_path[1][img_idx][-4:] in ['.bmp', '.tif']:
                    try:
                        spl = imgs_path[1][img_idx].split('_', 10)
                        spl_def1 = spl[4]
                        spl_def2 = spl[5]
                    except:
                        continue
                    imgs_dict[spl_def1+spl_def2] = img_idx
            maxXY_list = list(imgs_dict.values())
            #print(maxXY_list)
            for img_idx in maxXY_list:
                octaoi_imgs.append(web_func +'/'+imgs_path[1][img_idx])
                
        if isADC:
            # ADC影像路徑
            web_adc = r"http://10.97.212.99/AOI_Data_ADC/GrabImage/IP1/"+ date_oct +r"/"+ chipid+r"/"
            imgs_path = AUOFab_PathList(web_adc)
            for img_idx in range(len(imgs_path[1])):
                if imgs_path[1][img_idx][-4:] in ['.bmp', '.BMP']:
                    octadc_imgs.append(web_adc +'/'+imgs_path[1][img_idx])
    elif eqp_oct == 'CCCTS300':
        if isAOI:
            web_mura = r"http://10.97.213.216/AOI_Data_D/GrabImage/Source/IP1/"+ date_oct +r"/"+ chipid+"/Mura/"
            web_func = r"http://10.97.213.216/AOI_Data_D/GrabImage/Source/IP1/"+ date_oct +r"/"+ chipid+"/FunctionError/"
            
            """
            imgs_path = AUOFab_PathList(web_mura)
            for img_idx in range(len(imgs_path[1])):
                if imgs_path[1][img_idx][-4:] in ['.bmp', '.BMP']:
                    octaoi_imgs.append(web_mura +'/'+imgs_path[1][img_idx])
            """
    
            imgs_path = AUOFab_PathList(web_func)
            # 多圖對應表   會重覆蓋掉舊的
            imgs_dict = {}
            for img_idx in range(len(imgs_path[1])):
                if imgs_path[1][img_idx][-4:] in ['.bmp', '.tif']:
                    try:
                        spl = imgs_path[1][img_idx].split('_', 10)
                        spl_def1 = spl[4]
                        spl_def2 = spl[5]
                    except:
                        continue
                    imgs_dict[spl_def1+spl_def2] = img_idx
            maxXY_list = list(imgs_dict.values())
            #print(maxXY_list)
            for img_idx in maxXY_list:
                octaoi_imgs.append(web_func +'/'+imgs_path[1][img_idx])
            
        if isADC:
            # ADC影像路徑
            web_adc = r"http://10.97.213.216/AOI_Data_ADC/GrabImage/IP1/"+ date_oct +r"/"+ chipid+r"/"
            imgs_path = AUOFab_PathList(web_adc)
            for img_idx in range(len(imgs_path[1])):
                if imgs_path[1][img_idx][-4:] in ['.bmp', '.BMP']:
                    octadc_imgs.append(web_adc +'/'+imgs_path[1][img_idx]) 
                                                   
    elif eqp_oct == 'CCCTSA00':
        if isAOI:                          
            path_aoi1mura = r"http://10.97.213.56/D/AOI_Data_D/GrabImage/Defect/IP1/"+ date_oct +r"/"+ chipid+"/Mura/"
            path_aoi1func = r"http://10.97.213.56/D/AOI_Data_D/GrabImage/Defect/IP1/"+ date_oct +r"/"+ chipid+"/Func/"
            path_aoi2mura = r"http://10.97.213.56/E/AOI_Data_E/GrabImage/Defect/IP2/"+ date_oct +r"/"+ chipid+"/Mura/"
            path_aoi2func = r"http://10.97.213.56/E/AOI_Data_E/GrabImage/Defect/IP2/"+ date_oct +r"/"+ chipid+"/Func/"
            path_aoi3mura = r"http://10.97.213.56/F/AOI_Data_F/GrabImage/Defect/IP3/"+ date_oct +r"/"+ chipid+"/Mura/"
            path_aoi3func = r"http://10.97.213.56/F/AOI_Data_F/GrabImage/Defect/IP3/"+ date_oct +r"/"+ chipid+"/Func/"
            path_aoi4mura = r"http://10.97.213.56/G/AOI_Data_G/GrabImage/Defect/IP4/"+ date_oct +r"/"+ chipid+"/Mura/"
            path_aoi4func = r"http://10.97.213.56/G/AOI_Data_G/GrabImage/Defect/IP4/"+ date_oct +r"/"+ chipid+"/Func/"
            path_aoimuras = [path_aoi1mura, path_aoi2mura,path_aoi3mura,path_aoi4mura]
            path_aoifuncs = [path_aoi1func, path_aoi2func,path_aoi3func,path_aoi4func]
            
            
            for num in range(4):
                imgs_dict = {}
                imgs_path = AUOFab_PathList(path_aoimuras[num])
                for img_idx in range(len(imgs_path[1])):
                    if imgs_path[1][img_idx][-4:] in ['.bmp', '.tif22']:
                        #octaoi_imgs.append(path_aoimuras[num]+'/'+imgs_path[1][img_idx])
                        try:
                            spl = imgs_path[1][img_idx].split('_', 10)
                            spl_def1 = spl[4]
                            spl_def2 = spl[5]
                        except:
                            continue
                        imgs_dict[spl_def1+spl_def2] = img_idx
                maxXY_list = list(imgs_dict.values())
                for img_idx in maxXY_list:
                    octaoi_imgs.append(path_aoifuncs[num] +'/'+imgs_path[1][img_idx])
        
                imgs_path = AUOFab_PathList(path_aoifuncs[num])
                # 多圖對應表   會重覆蓋掉舊的
                imgs_dict = {}
                for img_idx in range(len(imgs_path[1])):
                    if imgs_path[1][img_idx][-4:] in ['.bmp', '.tif22']:
                        try:
                            spl = imgs_path[1][img_idx].split('_', 10)
                            spl_def1 = spl[4]
                            spl_def2 = spl[5]
                        except:
                            continue
                        imgs_dict[spl_def1+spl_def2] = img_idx
                maxXY_list = list(imgs_dict.values())
                #print(maxXY_list)
                for img_idx in maxXY_list:
                    octaoi_imgs.append(path_aoifuncs[num] +'/'+imgs_path[1][img_idx])
        
        if isADC:
            # ADC影像路徑
            web_adc = r"http://10.97.213.56/D/AOI_Data_ADC/GrabImage/IP1/"+ date_oct +r"/"+ chipid+r"/"
            imgs_path = AUOFab_PathList(web_adc)
            for img_idx in range(len(imgs_path[1])):
                if imgs_path[1][img_idx][-4:] in ['.bmp', '.BMP']:
                    octadc_imgs.append(web_adc +'/'+imgs_path[1][img_idx])
    
    elif eqp_oct == 'CCCTS500':
        isADC = True
        # ADC影像路徑
        web_adc = r"http://10.97.213.138/AOI_Data_ADC/GrabImage/IP1/"+ date_oct +r"/"+ chipid+r"/"
        imgs_path = AUOFab_PathList(web_adc)
        for img_idx in range(len(imgs_path[1])):
            if imgs_path[1][img_idx][-4:] in ['.bmp', '.BMP']:
                octadc_imgs.append(web_adc +'/'+imgs_path[1][img_idx])
                
    elif eqp_oct == 'CCCTS600':
        isADC = True
        # ADC影像路徑
        web_adc = r"http://10.97.213.39/AOI_Data_ADC/GrabImage/IP1/"+ date_oct +r"/"+ chipid+r"/"
        imgs_path = AUOFab_PathList(web_adc)
        for img_idx in range(len(imgs_path[1])):
            if imgs_path[1][img_idx][-4:] in ['.bmp', '.BMP']:
                octadc_imgs.append(web_adc +'/'+imgs_path[1][img_idx])
    
    elif eqp_oct == 'CCCTS900':
        isADC = True
        # ADC影像路徑
        web_adc = r"http://10.97.212.210/AOI_Data_ADC/GrabImage/IP1/"+ date_oct +r"/"+ chipid+r"/"
        imgs_path = AUOFab_PathList(web_adc)
        for img_idx in range(len(imgs_path[1])):
            if imgs_path[1][img_idx][-4:] in ['.bmp', '.BMP']:
                octadc_imgs.append(web_adc +'/'+imgs_path[1][img_idx])
    
    elif eqp_oct == 'CCOCTA00':
        isADC = True
        # ADC影像路徑
        web_adc = r"http://10.97.213.49/AOI_Data_ADC/GrabImage/IP1/"+ date_oct +r"/"+ chipid+r"/"
        imgs_path = AUOFab_PathList(web_adc)
        for img_idx in range(len(imgs_path[1])):
            if imgs_path[1][img_idx][-4:] in ['.bmp', '.BMP']:
                octadc_imgs.append(web_adc +'/'+imgs_path[1][img_idx])
                
    elif eqp_oct == 'CCOCTB00':
        isADC = True
        # ADC影像路徑
        web_adc = r"http://10.97.213.190/AOI_Data_ADC/GrabImage/IP1/"+ date_oct +r"/"+ chipid+r"/"
        imgs_path = AUOFab_PathList(web_adc)
        for img_idx in range(len(imgs_path[1])):
            if imgs_path[1][img_idx][-4:] in ['.bmp', '.BMP']:
                octadc_imgs.append(web_adc +'/'+imgs_path[1][img_idx])
                
    elif eqp_oct == 'CCOCTC00':
        isADC = True
        # ADC影像路徑
        web_adc = r"http://10.97.213.193/AOI_Data_ADC/GrabImage/IP1/"+ date_oct +r"/"+ chipid+r"/"
        imgs_path = AUOFab_PathList(web_adc)
        for img_idx in range(len(imgs_path[1])):
            if imgs_path[1][img_idx][-4:] in ['.bmp', '.BMP']:
                octadc_imgs.append(web_adc +'/'+imgs_path[1][img_idx])
    
    """
    if isADC and len(octadc_imgs) == 0:
        octadc_imgs.append(r"https://png.pngtree.com/element_our/20190528/ourmid/pngtree-fork-symbol-icon-design-image_1164181.jpg")
    if isAOI and len(octaoi_imgs) == 0:
        octaoi_imgs.append(r"https://png.pngtree.com/element_our/20190528/ourmid/pngtree-fork-symbol-icon-design-image_1164181.jpg")
    """
    # ct1
    # CAJN5SH_C1_PM_LM_FMura_S1_0.bmp
    # iL None
    """
    if isCT1:
        try:
            if int(mm_ct1) <= 6:
                chipid_times = str(int(hour_ct1)-1).zfill(2)
                hour_dir = chipid_times
            else:
                hour_dir = hour_ct1
        
            
            dir_path = r"http://tcweb002.corpnet.auo.com/"+eqp_ct1+r"/AOI%20Data/Defect_Image/AreaGrabber"
            imgNames = ['_C1_PM_HGO_FMura_S1_0.bmp', '_C2_PM_HGO_FMura_S2_0.bmp', '_C3_PM_HGO_FMura_S3_0.bmp',
                        '_C1_PM_RD_FMura_S1_0.bmp', '_C2_PM_RD_FMura_S2_0.bmp', '_C3_PM_RD_FMura_S3_0.bmp',
                        '_C1_PM_LD_FMura_S1_0.bmp', '_C2_PM_LD_FMura_S2_0.bmp', '_C3_PM_LD_FMura_S3_0.bmp',
                        '_C1_PM_LM_FMura_S1_0.bmp', '_C2_PM_LM_FMura_S2_0.bmp', '_C3_PM_LM_FMura_S3_0.bmp',
                        '_C1_PM_HGO3_FMura_S1_0.bmp', '_C2_PM_HGO3_FMura_S2_0.bmp', '_C3_PM_HGO3_FMura_S3_0.bmp']
            for name0 in imgNames:
                if isOKDef:
                    break
                ccd_num = name0[2]
                ct1_imgs.append(dir_path + ccd_num +r"/"+ date_ct1 +r"/" + hour_dir + r"/Source/" + chipid + name0)
            ct1img_list.append(ct1_imgs)
        except:
            ct1img_list.append(ct1_imgs)

    """
    return [octaoi_imgs, octadc_imgs]

def yieldSumm(user,name, auth, shift, date1, date2, req_list):
    
    today0 = datetime.date.today().strftime("%Y%m%d")
    today = today0[0:4]+'-'+today0[4:6]+'-'+today0[6:8]
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    logging.info('yieldSumm觸發, '+now)
    print(date1, date2)
        
    
             
    # 修正版oracle 與法
    mysql = "select t.model_no, t.test_user as LINE, count(*)as TOT"
    mysql += ",round(100*sum(decode(t.grade,'G',1,0))/count(*),2) as GO"
    mysql += ",round(100*sum(decode(t.defect_code_desc,'BP',1,0))/count(*),1) as BP"
    mysql += ",round(100*sum(decode(t.defect_code_desc,'V-OPEN',1,0))/count(*),1) as V_O"
    mysql += ",round(100*sum(decode(t.defect_code_desc,'V-LINE',1,0))/count(*),1) as V_L"
    mysql += ",round(100*sum(decode(t.defect_code_desc,'H-OPEN',1,0))/count(*),1) as H_O"
    mysql += ",round(100*sum(decode(t.defect_code_desc,'H-LINE',1,0))/count(*),1) as H_L"
    mysql += ",round(100*sum(decode(t.defect_code_desc,'X-SHORT',1,0))/count(*),1) as X_S"
    mysql += ",round(100*sum(decode(t.defect_code_desc,'V-OPEN-BL',1,0))/count(*),2) as VOBL"
    mysql += ",round(100*sum(decode(t.defect_code_desc,'H-BAND MURA',1,0))/count(*),1) as H_BAND_MURA"
    mysql += ",round(100*sum(decode(t.defect_code_desc,'WHITE SPOT',1,0))/count(*),1) as W_S"
    mysql += ",round(100*sum(decode(t.defect_code_desc,'BLACK SPOT',1,0))/count(*),1) as B_S"
    mysql += ",round(100*sum(decode(t.defect_code_desc,'AROUND GAP MURA',1,0))/count(*),1) as AGM"
    mysql += ",round(100*sum(decode(t.defect_code_desc,'OTHER ALIGN DEFECT',1,0))/count(*),2) as OAD"
    mysql += ",round(100*sum(decode(t.defect_code_desc,'OTHER APPEAR DEFECT',1,0))/count(*),2) as OAPD"
    mysql += ",round(100*sum(decode(t.defect_code_desc,'OTHER GLASS DEFECT',1,0))/count(*),2) as OGD"
    mysql += ",round(100*sum(decode(t.defect_code_desc,'DP',decode(t.grade,'W',1,0),0))/count(*),1) as DP_W"
    mysql += ",round(100*sum(decode(t.defect_code_desc,'DP-PAIR',decode(t.grade,'W',1,0),0))/count(*),1) as DPP_W"
    mysql += ",round(100*sum(decode(t.defect_code_desc,'DP-CLUSTER',1,0))/count(*),1) as DP_CLUSTER"
    mysql += ",round(100*sum(decode(t.defect_code_desc,'3DP-ADJ',1,0))/count(*),1) as DP_ADJ"
    mysql += ",round(100*sum(decode(t.defect_code_desc,'DP-NEAR',1,0))/count(*),1) as DP_NEAR"
    mysql += ",round(100*sum(decode(t.defect_code_desc,'BP-PAIR',1,0))/count(*),1) as BPP"
    mysql += ",round(100*sum(decode(t.defect_code_desc,'SMALL BP',decode(t.grade,'W',1,'X',1,0),0))/count(*),1) as SBP_XW"
    mysql += ",round(100*sum(decode(t.defect_code,'PD13',1,0))/count(*),1) as CP"
    mysql += ",round(100*sum(decode(t.defect_code_desc,'POINT-COUNT',1,0))/count(*),1) as POINT_COUNT"
    
    mysql += " from celods.h_dax_fbk_test_ods t where t.op_id='CGL' "
    mysql += " and t.mfg_day between to_date('" + date1 + "','yyyy-mm-dd') and to_date('" + date2 + "','yyyy-mm-dd')"
    mysql += " group by (t.model_no, t.test_user)"
    
    #修改撈法   只取sum　之後再另除以TOT
    mysql = "select t.model_no, t.test_user as LINE, count(*)as TOT"
    mysql += ", sum(decode(t.grade,'G',1,0)) as GO"
    mysql += ", sum(decode(t.defect_code_desc,'BP',1,0)) as BP"
    mysql += ", sum(decode(t.defect_code_desc,'V-OPEN',1,0)) as V_O"
    mysql += ", sum(decode(t.defect_code_desc,'V-LINE',1,0)) as V_L"
    mysql += ", sum(decode(t.defect_code_desc,'H-OPEN',1,0)) as H_O"
    mysql += ", sum(decode(t.defect_code_desc,'H-LINE',1,0)) as H_L"
    mysql += ", sum(decode(t.defect_code_desc,'X-SHORT',1,0)) as X_S"
    mysql += ", sum(decode(t.defect_code_desc,'V-OPEN-BL',1,0)) as VOBL"
    mysql += ", sum(decode(t.defect_code_desc,'H-BAND MURA',1,0)) as H_BAND_MURA"
    mysql += ", sum(decode(t.defect_code_desc,'WHITE SPOT',1,0)) as W_S"
    mysql += ", sum(decode(t.defect_code_desc,'BLACK SPOT',1,0)) as B_S"
    mysql += ", sum(decode(t.defect_code_desc,'AROUND GAP MURA',1,0)) as AGM"
    mysql += ", sum(decode(t.defect_code_desc,'OTHER ALIGN DEFECT',1,0)) as OAD"
    mysql += ", sum(decode(t.defect_code_desc,'OTHER APPEAR DEFECT',1,0)) as OAPD"
    mysql += ", sum(decode(t.defect_code_desc,'OTHER GLASS DEFECT',1,0)) as OGD"
    mysql += ", sum(decode(t.defect_code_desc,'DP',decode(t.grade,'W',1,0),0)) as DP_W"
    mysql += ", sum(decode(t.defect_code_desc,'DP-PAIR',decode(t.grade,'W',1,0),0)) as DPP_W"
    mysql += ", sum(decode(t.defect_code_desc,'DP-CLUSTER',1,0)) as DP_CLUSTER"
    mysql += ", sum(decode(t.defect_code_desc,'3DP-ADJ',1,0)) as DP_ADJ"
    mysql += ", sum(decode(t.defect_code_desc,'DP-NEAR',1,0)) as DP_NEAR"
    mysql += ", sum(decode(t.defect_code_desc,'BP-PAIR',1,0)) as BPP"
    mysql += ", sum(decode(t.defect_code_desc,'SMALL BP',decode(t.grade,'W',1,'X',1,0),0)) as SBP_XW"
    mysql += ", sum(decode(t.defect_code,'PD13',1,0)) as CP"
    mysql += ", sum(decode(t.defect_code_desc,'POINT-COUNT',1,0)) as POINT_COUNT"
    #mysql += ", sum(decode(t.defect_code_desc, NULL, 0, decode(t.grade,'W',1,'X',1,0))) as OTHERS"
    
    mysql += ", sum(decode(t.defect_code_desc, 'BP', 0, 'V-OPEN', 0, 'V-LINE', 0, 'H-OPEN', 0, 'H-LINE', 0, 'X-SHORT', 0, 'V-OPEN-BL', 0"
    mysql +=", 'H-BAND MURA', 0, 'WHITE SPOT', 0, 'BLACK SPOT', 0, 'AROUND GAP MURA', 0, 'OTHER ALIGN DEFECT', 0, 'OTHER APPEAR DEFECT', 0"
    mysql +=", 'OTHER GLASS DEFECT', 0, 'DP', 0, 'DP-PAIR', 0, 'DP-CLUSTER', 0, '3DP-ADJ', 0, 'DP-NEAR', 0, 'BP-PAIR', 0, 'SMALL BP', 0"
    mysql +=", 'PD13', 0, 'POINT-COUNT', 0, NULL, 0, decode(t.grade,'W',1,'X',1,0))) as OTHERS"
    
    #('BP', 'V-OPEN', 'V-LINE', 'H-OPEN', 'H-LINE', 'X-SHORT', 'V-OPEN-BL', 'H-BAND MURA', 'WHITE SPOT', 'BLACK SPOT', 'AROUND GAP MURA', 'OTHER ALIGN DEFECT', 'OTHER APPEAR DEFECT', 'OTHER GLASS DEFECT', 'DP', 'DP-PAIR', 'DP-CLUSTER', '3DP-ADJ', 'DP-NEAR', 'BP-PAIR', 'SMALL BP', 'PD13 ', 'POINT-COUNT')

    #mysql += ", sum(decode(t.defect_code,NULL,0,1)) as others"
    mysql += " from celods.h_dax_fbk_test_ods t where t.op_id='CGL' "
    mysql += " and t.mfg_day between to_date('" + date1 + "','yyyy-mm-dd') and to_date('" + date2 + "','yyyy-mm-dd')"
    
    
    mysql += " group by (t.model_no, t.test_user)"
    
    logging.info('sql: '+mysql)
    ct1_summ = ora2df(mysql)
    
    
    """
    # 增加other項目
    
    non_cols = ['OTHERS','MFG_DAY','MODEL_NO', 'TOT', 'GO', 'LINE', '已Check', 'Check總數', 'Real_Ratio']
    col_others = ct1_summ['OTHERS']
    for col0 in ct1_summ.columns:
        if col0 not in non_cols:
            col_others = col_others - ct1_summ[col0]
    ct1_summ['OTHERS'] = col_others
    
    """
    defs_list = []
    
    for item in req_list:
        if item[0:4] == 'chk_':
            defs_list.append(item[4:])
    original_col = list(ct1_summ.columns)
    print(original_col)
    # 從左邊項目點進來的
    if len(req_list) == 5:
        defs_list = original_col[4:]
    drop_col = []
    if len(defs_list) != 0: 
        for i in ct1_summ.columns[4:]:
            if i not in defs_list:
                drop_col.append(i)
        ct1_summ = ct1_summ.drop(columns=drop_col)
    print(drop_col)
    
    
    # 完整名稱的defect list
    defs_list2 = []
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
    
    for def0 in defs_list:
        if def0 in A2W_DEFECT_NAMES.keys():
            new_def0 = A2W_DEFECT_NAMES[def0]
            defs_list2.append(new_def0)
        else:
            defs_list2.append(def0)
    print('defs_list2', defs_list2)
    
    except_list = ['MFG_DAY', 'MODEL_NO', 'LINE','GO', 'TOT', 'Check總數', 'Real_Ratio', '已Check']
    
    #總已check 及 
    check_count = 0
    tot_count = 0
    # 計算real總數  最後一行用
    real_tot = 0
    except_cols = ['MFG_DAY','MODEL_NO', 'LINE', '已Check', 'Check總數', 'Real_Ratio']
    new_n = len(ct1_summ)
    for col0 in ct1_summ.columns:
        if col0 not in except_cols:
            ct1_summ.loc[new_n, col0] = 0
            defect_sum = ct1_summ[col0].sum()
            ct1_summ.loc[new_n, col0] = round(defect_sum, 2)
        else:
            ct1_summ.loc[new_n, col0] = '-'
            
            
            
    # 下載判圖記錄
    table = 'img_check_record'
    mfg_days = datesListStr(date1, date2)
    #mfg_days = ['2022-04-26', '2022-04-27',  '2022-04-25']
    sql_days0 = str(mfg_days)[1:-1]
    sql = r"select *"
    sql += r" from craig01.img_check_record t"
    sql += r" where t.TEST_TIME_MFG in (" + sql_days0 +")"
    df_img_record = sql2df(sql)
    
    
    print('mysql2df(table) ok')
    logging.info('mysql2df -> '+table+'   ok!!')
    ct1_summ['已Check'] = 0
    ct1_summ['Real_Ratio'] = 0
    for i in ct1_summ.index:
        
        if i == new_n:
            tot = ct1_summ.loc[i]['TOT']
            ct1_summ.iloc[i, 3:] = ct1_summ.iloc[i, 3:].apply(lambda x: round(100*x/tot, 2))
            continue
        tot = ct1_summ.loc[i]['TOT']
        check_tot = ct1_summ.iloc[i, 4:].sum()
        tot_count += check_tot
        #print(tot_count)
        ct1_summ.iloc[i, 3:] = ct1_summ.iloc[i, 3:].apply(lambda x: round(100*x/tot, 2))
        
        ct1_summ.loc[i, 'Check總數'] = check_tot
        
        
        #mfg_str = str(ct1_summ.loc[i]['MFG_DAY'])[:10]
        line0 = ct1_summ.loc[i]['LINE']
        model_no0 = ct1_summ.loc[i]['MODEL_NO']
        
    
        #df0 = df_img_record[(df_img_record['TEST_TIME_MFG'].isin(mfg_days)) & (df_img_record['TEST_USER']==line0)& (df_img_record['MODEL_NO']==model_no0)]
        df0 = df_img_record[(df_img_record['TEST_USER']==line0)& (df_img_record['MODEL_NO']==model_no0)]
        #
        #df0.drop_duplicates(['CHIPID','PATTERN_CODE'], keep='last', inplace=True)
        if len(df0) > 0:
            last_n = df0.index[-1]
            #df0.drop_duplicates(['CHIP_ID', 'OCT_DEFECT'], keep='last', inplace=True)
            df0 = df0[df0['DEFECT_CODE_DESC'].isin(defs_list2)].copy()
            ct1_summ.loc[i, '已Check'] = len(df0)
            check_count += len(df0)
            real_num0 = len(df0[df0['imgCheck']=='R'])
            real_tot += real_num0
            ct1_summ.loc[i, 'Real_Ratio'] = real_num0
            

        if ct1_summ.loc[i]['已Check'] == 0:
            ct1_summ.loc[i, 'Real_Ratio'] = r"N/A"
        else:
            ct1_summ.loc[i, 'Real_Ratio'] = round(100*ct1_summ.loc[i]['Real_Ratio']/ct1_summ.loc[i]['已Check'], 1)
        #ct1_summ.loc[i, '已Check'] = round(ct1_summ.loc[i]['已Check'], 0)
        #ct1_summ.loc[i, 'Check總數'] = round(ct1_summ.loc[i]['Check總數'], 0)
    
    
    
    
    ct1_summ.loc[new_n, 'LINE'] = '總數'
    ct1_summ.loc[new_n, '已Check'] = check_count
    ct1_summ.loc[new_n, 'Check總數'] = tot_count
    ct1_summ.loc[new_n, 'Real_Ratio'] = round(100*real_tot/ct1_summ.loc[i]['已Check'], 1)

    
    
    
    
    
        #df_img_record
    #mach = [ [0,'CCCGL1082',1], [1,'CCCGL1083',0], [2,'CCCGL2082', 1], [3,'CCCGL2083', 0] ]st.values.tolist(), maint_showIdx=maint_showIdx, mi 
    sectShow = 'ct1Summ'
    return render_template('userMain.html', user=str(user),name=name, auth=auth, shift=shift, today=today, sectShow=sectShow, ct1_summ=ct1_summ, date1=date1, date2=date2, drop_col=drop_col, original_col=original_col)



def blockCheck(user,name, auth, shift):
    
    sectShow = "blockCheck"
    
    
    #submit_list2 = [0,0,0]
    date = request.form.get('blockCheck_date')
    if date is None:
        date = datetime.date.today().strftime("%Y-%m-%d")
    model_no = request.form.get('model_no')
    site = request.form.get('site')
    if site == '1':
        site = 'CT1'
    elif site == '2':
        site = 'OCT'
    bc_list = []
    if model_no is not None:
        if site == 'CT1' and model_no[:] in ["T43QVN", "P43QVN", "T43QVN_P43QVN"]:
            
            bc00 = [""]
            bc1 = ["CH8", "CH12", "CH20", "CH2", "CH1", 
            		"CH18", "CH17", "CH16", "CH15", "CH14", 
            		"CH13", "CH10", "CH9", "CH21", "CH20", 
            		"CH11", "CH12"]
            bc2 = ["CH4", "CH5", "CH6", "CH3"]
            bc3 = ["CH12", "CH24", "CH19", "CH21", "CH23",
            		"CH22", "CH2", "CH1", "CH18", "CH17", 
            		"CH16", "CH15", "CH14", "CH13", "CH19",
            		"CH12", "CH8"]
            
            bc_list = [bc1, bc2, bc00, bc2, bc00, 
            			bc2, bc2, bc2, bc00, bc2, 
            			bc00, bc2, bc3]
      
        
        elif site == 'CT1' and model_no[:] in ["T500QVN", "P500QVN", "T500QVN_P500QVN"]:
            
            bc00 = [""]
            bc1 = ["CH8", "CH12", "CH20", "CH2", "CH1", 
            		"CH18", "CH17", "CH16", "CH15", "CH14", 
            		"CH13", "CH10", "CH9", "CH21", "CH20", 
            		"CH11", "CH12"]
            bc2 = ["CH4", "CH5", "CH6", "CH3"]
            bc3 = ["CH12", "CH24", "CH19", "CH21", "CH23",
            		"CH22", "CH2", "CH1", "CH18", "CH17", 
            		"CH16", "CH15", "CH14", "CH13", "CH19",
            		"CH12", "CH8"]
            
            bc_list = [bc1, bc2, bc00, bc2, bc00, 
            			bc2, bc2, bc2, bc00, bc2, 
            			bc00, bc2, bc3]
        elif site == 'CT1' and model_no[:] in ["T43HVN", "P43HVN", "T43HVN_P43HVN"]:
            
            bc00 = [""]
            bc1 = ["CH8", "CH7", "CH7", "CH6", "CH5", 
            		"CH4", "CH3", "CH2", "CH1", "CH23", 
            		"CH13", "CH10", "CH9", "CH21", "CH20", 
            		"CH22", "CH24", "CH00", "CH7", "CH9"]
            bc2 = ["CH10", "CH11", "CH12", "CH9"]
            bc3 = ["CH9", "CH7", "CH00", "CH24", "CH23",
            		"CH22", "CH18", "CH17", "CH16", "CH15", 
            		"CH14", "CH13", "CH7", "CH7", "CH8"]
            
            
            bc_list = [bc1, bc2, bc00, bc2, bc00, 
            			bc2, bc3]
        
        elif site == 'CT1' and model_no in ["P42IVN"]:
              
            bc1 = ["CH8", "CH19", "CH20", "CH18", "CH17",
             "CH16", "CH15", "CH14", "CH13", "CH23",
             "CH22", "CH21", "CH19", "CH24", "CH3"]
            
            bc2 = ["CH4", "CH5", "CH6", "CH3"]
            
            bc3 = ["CH12", "CH24", "CH19", "CH21", "CH23", 
            "CH22", "CH18", "CH17", "CH16", "CH15", 
            "CH14", "CH13", "CH20", "CH19", "CH8"]

            bc_list = [bc1, bc2, bc2, bc2, bc2, 
            			bc2, bc3]   
            
        elif site == 'CT1' and model_no in ["T420HVN02"]:

            bc00 = [""]
            
            bc1 = ["CH4", "CH8", "CH18", "CH17", "CH16",
                 "CH15", "CH14", "CH13", "CH23", "CH22",
                 "CH21", "CH19", "CH20", "CH12"]
                
            
            bc2 = ["CH4", "CH5", "CH6", "CH3"]
                
            
            bc3 = ["CH12", "CH20", "CH19", "CH21", "CH23",
                 "CH22", "CH18", "CH17", "CH16", "CH15",
                 "CH14", "CH13", "CH8", "CH4"]

            bc_list = [bc1, bc2, bc00, bc2, bc00, 
            			bc2, bc3]
            
        
        elif site == 'OCT' and model_no[:] in ["T43QVN", "P43QVN", "T43QVN_P43QVN"]:
        
            bc1 = ["CH8", "CH8", "CH20", "CH2", "CH1",
                   "CH18", "CH17", "CH16", "CH15", "CH14",
                   "CH13", "CH10", "CH9", "CH21", "CH20", 
                   "CH11", "CH12"]
            bc2 = ["CH4", "CH5", "CH6", "CH3"]
            bc3 = ["CH12", "CH24", "CH19", "CH21", "CH23",
                   "CH22", "CH2", "CH1", "CH18", "CH17", 
                   "CH16", "CH15", "CH14", "CH13", "CH19",
                   "CH8", "CH8"]
            bc_list = [bc1, bc2, bc2, bc2, bc2,
                       bc2, bc2, bc2, bc2, bc2,
                       bc2, bc2, bc3]
        
        elif site == 'OCT' and model_no[:] in ["T500QVN", "P500QVN", "T500QVN_P500QVN", "T430QVN03_8B"]:
            
            bc00 = [""]
            bc1 = ["CH8", "CH12", "CH20", "CH2", "CH1", 
            		"CH18", "CH17", "CH16", "CH15", "CH14", 
            		"CH13", "CH10", "CH9", "CH21", "CH20", 
            		"CH11", "CH12"]
            bc2 = ["CH4", "CH5", "CH6", "CH3"]
            bc3 = ["CH12", "CH24", "CH19", "CH21", "CH23",
            		"CH22", "CH2", "CH1", "CH18", "CH17", 
            		"CH16", "CH15", "CH14", "CH13", "CH19",
            		"CH12", "CH8"]
            
            bc_list = [bc1, bc2, bc00, bc2, bc00, 
            			bc2, bc2, bc2, bc00, bc2, 
            			bc00, bc2, bc3]
        elif site == 'OCT' and model_no[:] in ["T43HVN", "P43HVN", "T43HVN_P43HVN"]:
            
            bc00 = [""]
            bc1 = ["CH8", "CH7", "CH7", "CH6", "CH5", 
            		"CH4", "CH3", "CH2", "CH1", "CH23", 
            		"CH22", "CH24", "CH00", "CH19", "CH21"]
            bc2 = ["CH10", "CH11", "CH12", "CH9"]
            bc3 = ["CH21", "CH19", "CH00", "CH24", "CH23",
            		"CH22", "CH18", "CH17", "CH16", "CH15", 
            		"CH14", "CH13", "CH7", "CH7", "CH20"]
            
            bc_list = [bc1, bc2, bc2, bc2, bc2, 
            			bc2, bc3]
        
        elif site == 'OCT' and model_no in ["P42IVN"]:
            bc1 = ["CH8", "CH19", "CH20", "CH18", "CH17",
             "CH16", "CH15", "CH14", "CH13", "CH23", 
             "CH22", "CH21", "CH19", "CH24", "CH7"]
             
            bc2 = ["CH4", "CH5", "CH6", "CH3"]
            

            bc3 = ["CH7", "CH24", "CH19", "CH21", "CH23",
             "CH22", "CH18", "CH17", "CH16", "CH15",
             "CH14", "CH13", "CH20", "CH19", "CH8"]
            bc_list = [bc1, bc2, bc2, bc2, bc2, 
            			bc2, bc3]
        
        elif site == 'OCT2222' and model_no in ["T420HVN02"]:
             
            bc00 = [""]
             
            bc2 = ["CH3", "CH4", "CH5", "CH6"]
                

            bc_list = [bc2, bc2, bc2, bc2, bc2, 
            			bc2, bc2]
        
        
        
        
            
    table = "block_check"
    db_data = mysql2df(table)
    if request.form.get('blockCheck') == "資料上傳":
        req_list = list(request.form)
        
        df_record = pd.DataFrame(columns=['Date', 'OP_ID', 'Model_No',  'Status', 'Upload_Time'])
        df_record.loc[0, 'Date'] = date
        df_record.loc[0, 'OP_ID'] = site
        df_record.loc[0, 'Model_No'] = model_no
        now0 = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        df_record.loc[0, 'Upload_Time'] = now0
        
        df_record.loc[0, 'Upload_User'] = str(user)+name
        #　先假設ｏｋ
        okng0 = 'OK'
        # gate2的項目
        gate2_num = -1
        for req_name in req_list:
            if req_name[:2] in ['S0', 'S1']:
                block_val0 = request.form.get(req_name)
                # 未填寫則跳過
                if block_val0 == "":
                    continue
                s_num0 = int(req_name[1:3])
                #取得最大ｓ
                if s_num0 > gate2_num:
                    gate2_num = s_num0
                #spec0 = int(req_name[-2:])
                # ch名稱轉換為資料庫data
                #col0 = 'Data' + str(s_num0-1).zfill(2) + "_" + req_name[-2:]
                
                df_record.loc[0, req_name] = block_val0
                """
                if type(block_val0) == type(555) and round(block_val0) != spec0:
                    print('不符', req_name, block_val0)
                    okng0 = 'NG'
                elif type(block_val0) != type(555):
                    okng0 = 'NG'
                """
        
        # Gate column換算
        dic_rename = {}
        gate2_name = 'S' + str(gate2_num).zfill(2)
        for col0 in df_record.columns:
            if col0[:3] == 'S01':
                no0 = col0[-2:]
                dic_rename[col0] = 'Gate01_'+ no0
            elif col0[:3] == gate2_name:
                no0 = col0[-2:]
                dic_rename[col0] = 'Gate02_'+ no0
            elif col0[:2] in ['S0', 'S1']:
                data_num0 = int(col0[1:3]) - 1 
                no0 = col0[-2:]
                dic_rename[col0] = 'Data' + str(data_num0).zfill(2) + '_' + no0
        df_record.rename(columns=dic_rename, inplace=True)
        cols = list(df_record.columns)
        # 沒有的項目缺補-1
        for db_col in  db_data.columns:
            if db_col not in cols:
                df_record.loc[0, db_col] = -1
        df_record.fillna(-1, inplace=True)
        # 從bc_list的角度來檢查df)record
        for s_num in range(len(bc_list)):
            s0 = bc_list[s_num]
            # 先排除[""]項目
            if s0[0] == "":
                continue
            elif s_num == 0:
                col00 = 'Gate01_'
            elif s_num == (len(bc_list) - 1):
                col00 = 'Gate02_'
            else:
                col00 = 'Data' + str(s_num).zfill(2) + '_'
            for j in range(len(s0)):
                spec0 = int(s0[j][2:])
                if spec0 in [0]:
                    continue
                input_col0 = col00 + str(j+1).zfill(2)
                ch_input = df_record.loc[0][input_col0]
                if ch_input == -1:
                    #　必填項目改為－９９９
                    df_record.loc[0, input_col0] = -999
                    okng0 = 'NG'
                    print('NG2:',input_col0,ch_input, spec0 )
                elif spec0 != round(float(ch_input), 0):
                    okng0 = 'NG'
                    print('NG:',input_col0,ch_input, spec0 )
        df_record.loc[0, 'Status'] = okng0
                    
                    
                    
        print(df_record)
        #df_record.to_csv('df_record.csv',index=False, encoding='utf-8-sig')
        df2mysql_append(df_record, table)
        
        
        
        
        
    else:
        1
        #return render_template('userMain.html',sectShow=sectShow, user=str(user),name=name, auth=auth, shift=shift, date=date, model_no=model_no, site=site, bc_list=bc_list)
    
    df_record = mysql2df(table)
    df_record = df_record.replace({-999:"未填寫"}).copy()
    df_record = df_record.replace({-1:" "}).copy()
    cols = ["Date", "OP_ID", "Model_No", "Status", "Upload_Time", "Upload_User"]
    df_record = df_record[cols].copy()
    # 統一回到點檢頁面
    return render_template('userMain.html',sectShow=sectShow, user=str(user),name=name, auth=auth, shift=shift, 
                                                   date=date, model_no=model_no, site=site, bc_list=bc_list,
                                                   df_record=df_record)


def cpsEQP_Diff(date1, date2):
    """
    #修改撈法   只取sum　之後再另除以TOT
    mysql = "select t.model_no, t.test_user as EQP, count(*)as TOT"
    mysql += ", sum(decode(t.grade,'G',1,0)) as GO"
    mysql += ", sum(decode(t.defect_code_desc,'BP',1,0)) as BP"
    mysql += ", sum(decode(t.defect_code_desc,'V-OPEN',1,0)) as V_O"
    mysql += ", sum(decode(t.defect_code_desc,'V-LINE',1,0)) as V_L"
    mysql += ", sum(decode(t.defect_code_desc,'H-OPEN',1,0)) as H_O"
    mysql += ", sum(decode(t.defect_code_desc,'H-LINE',1,0)) as H_L"
    mysql += ", sum(decode(t.defect_code_desc,'X-SHORT',1,0)) as X_S"
    mysql += ", sum(decode(t.defect_code_desc,'V-OPEN-BL',1,0)) as VOBL"
    mysql += ", sum(decode(t.defect_code_desc,'H-BAND MURA',1,0)) as H_BAND_MURA"
    mysql += ", sum(decode(t.defect_code_desc,'WHITE SPOT',1,0)) as W_S"
    mysql += ", sum(decode(t.defect_code_desc,'BLACK SPOT',1,0)) as B_S"
    mysql += ", sum(decode(t.defect_code_desc,'AROUND GAP MURA',1,0)) as AGM"
    mysql += ", sum(decode(t.defect_code_desc,'OTHER ALIGN DEFECT',1,0)) as OAD"
    mysql += ", sum(decode(t.defect_code_desc,'OTHER APPEAR DEFECT',1,0)) as OAPD"
    mysql += ", sum(decode(t.defect_code_desc,'OTHER GLASS DEFECT',1,0)) as OGD"
    mysql += ", sum(decode(t.defect_code_desc,'DP',decode(t.grade,'W',1,0),0)) as DP_W"
    mysql += ", sum(decode(t.defect_code_desc,'DP-PAIR',decode(t.grade,'W',1,0),0)) as DPP_W"
    mysql += ", sum(decode(t.defect_code_desc,'DP-CLUSTER',1,0)) as DP_CLUSTER"
    mysql += ", sum(decode(t.defect_code_desc,'3DP-ADJ',1,0)) as DP_ADJ"
    mysql += ", sum(decode(t.defect_code_desc,'DP-NEAR',1,0)) as DP_NEAR"
    mysql += ", sum(decode(t.defect_code_desc,'BP-PAIR',1,0)) as BPP"
    mysql += ", sum(decode(t.defect_code_desc,'SMALL BP',decode(t.grade,'W',1,'X',1,0),0)) as SBP_XW"
    mysql += ", sum(decode(t.defect_code,'PD13',1,0)) as CP"
    mysql += ", sum(decode(t.defect_code_desc,'POINT-COUNT',1,0)) as POINT_COUNT"
    #mysql += ", sum(decode(t.defect_code_desc, NULL, 0, decode(t.grade,'W',1,'X',1,0))) as OTHERS"
    
    mysql += ", sum(decode(t.defect_code_desc, 'BP', 0, 'V-OPEN', 0, 'V-LINE', 0, 'H-OPEN', 0, 'H-LINE', 0, 'X-SHORT', 0, 'V-OPEN-BL', 0"
    mysql +=", 'H-BAND MURA', 0, 'WHITE SPOT', 0, 'BLACK SPOT', 0, 'AROUND GAP MURA', 0, 'OTHER ALIGN DEFECT', 0, 'OTHER APPEAR DEFECT', 0"
    mysql +=", 'OTHER GLASS DEFECT', 0, 'DP', 0, 'DP-PAIR', 0, 'DP-CLUSTER', 0, '3DP-ADJ', 0, 'DP-NEAR', 0, 'BP-PAIR', 0, 'SMALL BP', 0"
    mysql +=", 'PD13', 0, 'POINT-COUNT', 0, NULL, 0, decode(t.grade,'W',1,'X',1,0))) as OTHERS"
    
    #('BP', 'V-OPEN', 'V-LINE', 'H-OPEN', 'H-LINE', 'X-SHORT', 'V-OPEN-BL', 'H-BAND MURA', 'WHITE SPOT', 'BLACK SPOT', 'AROUND GAP MURA', 'OTHER ALIGN DEFECT', 'OTHER APPEAR DEFECT', 'OTHER GLASS DEFECT', 'DP', 'DP-PAIR', 'DP-CLUSTER', '3DP-ADJ', 'DP-NEAR', 'BP-PAIR', 'SMALL BP', 'PD13 ', 'POINT-COUNT')
    
    #mysql += ", sum(decode(t.defect_code,NULL,0,1)) as others"
    mysql += " from celods.h_dax_fbk_test_ods t where t.op_id='CGL' "
    mysql += " and t.mfg_day between to_date('" + date1 + "','yyyy-mm-dd') and to_date('" + date2 + "','yyyy-mm-dd')"
    
    
    mysql += " group by (t.model_no, t.test_user)"
    
    
    df0 = ora2df(mysql)
    df0.set_index([ 'MODEL_NO', 'EQP'], inplace=True)
    df0['GO'] = df0['GO']/ df0['TOT'] * 100
    
    point_bps = ['BP', 'BPP', 'SBP_XW', 'POINT_COUNT']
    
    point_dps = ['DP_W', 'DPP_W', 'DP_CLUSTER', 'DP_ADJ', 'DP_NEAR', 'CP']
    lines = ['V_O', 'V_L', 'H_O', 'H_L', 'X_S', 'VOBL', 'H_BAND_MURA']
    muras = ['W_S', 'B_S', 'AGM']
    oths = ['OAD', 'OAPD', 'OGD']
    
    df0['Point(BP)'] = 0
    df0['Point(DP)'] = 0
    df0['Line'] = 0
    df0['Mura'] = 0
    df0['Others'] = 0
    for col0 in point_bps:
        df0['Point(BP)'] += df0[col0]
    df0['Point(BP)'] = df0['Point(BP)']/ df0['TOT'] * 100
    
    for col0 in point_dps:
        df0['Point(DP)'] += df0[col0]
    df0['Point(DP)'] = df0['Point(DP)']/ df0['TOT'] * 100
    
    for col0 in lines:
        df0['Line'] += df0[col0]
    df0['Line'] = df0['Line']/ df0['TOT'] * 100
    
    for col0 in muras:
        df0['Mura'] += df0[col0]
    df0['Mura'] = df0['Mura']/ df0['TOT'] * 100
    
    for col0 in oths:
        df0['Others'] += df0[col0]
    df0['Others'] = df0['Others']/ df0['TOT'] * 100
    
    need_cols = ['GO', 'Point(BP)', 'Point(DP)', 'Line', 'Mura','Others']
    df0 = df0[need_cols].round(2)
    df0.reset_index(drop=False, inplace=True)
    df0['EQP'] = df0['EQP'].str[2:]
    df0.drop(columns=['MODEL_NO', 'GO'], inplace=True)
    """
    table = "cps_eqpdiff"
    df_report = mysql2df6878(table)
    
     # 去除全columns為None者
    spec_dic = {}
    df_report.dropna(how='all', axis = 0, inplace=True)
    df_report.fillna(-1, inplace=True)
    # spec計算
    for idx0 in df_report.index:
        md0 = df_report.loc[idx0]['MODEL_NO']
        eqp0 = df_report.loc[idx0]['EQP']
        #print(md0, eqp0)
        for col0 in ['Point(BP)', 'Point(DP)', 'Line', 'Mura', 'Others']:
            val0 = df_report.loc[idx0][col0]
            val0 = val0.round(5)
            key0 = (md0, col0)
            if val0 == -1:
                continue
            if key0 not in spec_dic.keys():
                spec_dic[key0] = [val0]
            else:
                list0 = spec_dic[key0]
                list0.append(val0)
                spec_dic[key0] = list0
    
    df_report.reset_index(drop=False, inplace=True)
    
    
    
    spec_thr =0.8
    alarm_idxs = []
    alarm_cols = ['EQP']
    for idx0 in df_report.index:
        md0 = df_report.loc[idx0]['MODEL_NO']
        eqp0 = df_report.loc[idx0]['EQP']
        
        for col0 in ['Point(BP)', 'Point(DP)', 'Line', 'Mura', 'Others']:
            val0 = df_report.loc[idx0][col0]
            key0 = (md0, col0)
            
            if val0 != -1:
                spec0 = sum(spec_dic[key0]) / len(spec_dic[key0])
                
                if len(spec_dic[key0]) > 1 and abs(val0-spec0) > spec_thr:
                    alarm_idxs.append(idx0)
                    print(md0, eqp0, col0, val0.round(1), spec0.round(1))
                    df_report.loc[idx0, "建議"] = "機差確認:" + col0
                    if col0 not in alarm_cols:
                        alarm_cols.append(col0)
    df0 = df_report.loc[alarm_idxs]
    df0['EQP'] = df0['EQP'].str[2:]
    return df0[['EQP', '建議']]
# 合併columns 增加row_cnt欄位
def makeRowCnt(df0, cnt_cols):
    for cnt_col0 in cnt_cols:
        df0['ROW_CNT_' + cnt_col0] = 1
        if len(df0) > 0:
            start_idx = df0.index[0]
            val0 = str(df0.loc[start_idx][cnt_col0])
        for idx in df0.index[1:]:
            next_val0 = str(df0.loc[idx][cnt_col0])
            if val0 == next_val0:
                df0.loc[start_idx, 'ROW_CNT_' + cnt_col0] = df0.loc[start_idx]['ROW_CNT_' + cnt_col0] + 1
                df0.loc[idx, 'ROW_CNT_' + cnt_col0] = -1
            else:
                start_idx = idx
                val0 = next_val0
    return df0

def edaHR(date_after = 2):
    table = 'c2_hr'
    df0 = mysql2df6878(table)

    df0.sort_values(by=['Date'], inplace=True)
    
    base_dtdate = datetime.datetime(2022,5,30) # B班最後一天
    #date1 = "2022-05-26"
    #date2 = "2022-06-04"
    #date_after = 2
    today_dt = datetime.date.today()
    date1 = today_dt.strftime("%Y-%m-%d")
    date2 = (today_dt + datetime.timedelta(days = date_after)).strftime('%Y-%m-%d')
    dates = dates2list(date1, date2, isDT=True)
    cols = ['Shift_AB', 'Job_Type'] 
    df_report = pd.DataFrame()
    
    for dt_date in dates:
        # 先算今天是A or B班
        date0_diff = (base_dtdate - dt_date).days
        if date0_diff%4 in [0, 1]:
            ab0 = 'B'
        if date0_diff%4 in [2, 3]:
            ab0 = 'A'
        
        
        
        date0 = dt_date.strftime("%Y-%m-%d")
        #dt_date = datetime.datetime(2022,5,31)
        #date0 = "2022-05-31"
        df0_tmp = df0.copy()
        df0_tmp['Date_Diff'] = df0_tmp['Date'].apply(lambda x: (dt_date - datetime.datetime.strptime(x, "%Y-%m-%d")  ).days )
    
        df0_tmp = df0_tmp[df0_tmp['Date_Diff'] >= 0].copy()
        df0_tmp.drop_duplicates(['AUO_No'], keep='last',inplace=True)
        df_report0 = df0_tmp[['AUO_No', 'Name', 'Job_Type', 'Shift_AB', 'Shift_DN']].copy()
        df_report0 = df_report0[df_report0['Shift_AB'].isin([ab0, 'Normal'])].copy()
        
        df_report0['Date'] = date0
        
        df_report0['Date_AB'] = ab0
        df_report = df_report.append(df_report0)
        df_report.reset_index(drop=True,inplace=True)
        df_report.sort_values(by=['Date', 'Shift_DN'], inplace=True)
        df_report.reset_index(drop=True,inplace=True)
        
        # 轉換為網頁顯示表格
        groups0 = ['Date', 'Shift_DN', 'Job_Type']
        # 排除kj & LV3
        wd0 = dt_date.weekday()
        if wd0 >= 5:
            exp_names = ["陳冠任", "尚怡璇"]
        else:
            exp_names = ["陳冠任"]
        df_report = df_report[~df_report['Name'].isin(exp_names)].copy()
        df_table = df_report.groupby(groups0).size().to_frame(name='TOT')
        #df_table = pd.DataFrame()
    for dt_date in dates:
        date0 = dt_date.strftime("%Y-%m-%d")
        wd0 = dt_date.weekday()
        
        date0_diff = (base_dtdate - dt_date).days
        if date0_diff%4 in [0, 1]:
            ab0 = 'B'
        if date0_diff%4 in [2, 3]:
            ab0 = 'A'
        
        # 出席類型
        if wd0 >= 5:
            work_types = [ 'DL']
            shifts_ab = ['A', 'B']
        else:
            work_types = ['IDL', 'DL']
            shifts_ab = ['A', 'B', 'Normal']
        for dn0 in ['D', 'N']:
            for type0 in work_types:
                filter0 = (df_report['Date'] ==date0 ) & (df_report['Shift_DN'] == dn0) & (df_report['Shift_AB'].isin(shifts_ab)) & (df_report['Job_Type'] == type0) & (df_report['Name'] != "陳冠任")
                df_tmp0 = df_report[filter0].copy()
                #print(len(df_tmp0))
                #ab0 = df_tmp0.loc[df_tmp0.index[0]]['Date_AB']
                word0 = ""
                for name0 in list(df_tmp0['Name']):
                    word0 += name0[1:] + ", "
                df_table.loc[(date0, dn0, type0), 'Working'] = word0[:-2]
                df_table.loc[(date0, dn0, type0), 'AB'] = ab0
    df_table.dropna(inplace=True)
    df_table.reset_index(drop=False, inplace=True)
    
    # Date增加ab班資訊
    for idx0 in df_table.index:
         ab0 = df_table.loc[idx0]['AB'] 
         df_table.loc[idx0, 'Date'] = df_table.loc[idx0]['Date'] + " (" + ab0 + ")"
    df_table.drop(columns=['AB'], inplace=True)
    df_table = makeRowCnt(df_table, ["Date", "Shift_DN"])
    df_table['TOT'] = df_table['TOT'].astype(int)
    
    return df_table

def hrMain(user,name, auth, shift, req_name):
    sectShow = req_name
    print(sectShow + 'Post')
    logging.info((sectShow + 'Post'))
    
    
    #table = 'user_data'
    #user_data = mysql2df(table)
    df_table = edaHR()
    
    return render_template('userMain.html', user=str(user),name=name, auth=auth, shift=shift, 
                               sectShow=sectShow, df_table=df_table)

def hr_changeShift(user,name, auth, shift):
    
    sectShow = "hr_changeShift"
    print(sectShow + 'Post')
    logging.info((sectShow + 'Post'))
    # 取得選單上的人名
    
    #table = 'user_data'
    #user_data = mysql2df(table)
    table = 'c2_hr'
    df_table = mysql2df6878(table)

    df_table.sort_values(by=['Date'], inplace=True)
    df_table = df_table[df_table['Shift_AB'] != 'Normal'].copy()
    hr_name = request.form.get('hr_changeShift')
    
    upload_ans = ""
    if hr_name == "upload":
        hr_name = request.form.get('hr_Name')
        hr_sh = request.form.get('hr_Shift')
        hr_sh_date = request.form.get('hr_Shift_Date')
        if hr_sh in ['DA', 'DB', 'NA', 'NB']:
            hr_sh_dn = hr_sh[0]
            hr_sh_ab = hr_sh[1]
           
            # 先找到本人
            df0 = df_table[df_table['Name'] == hr_name].copy()
            if len(df0) > 0:
                #取得樣本
                df0.drop_duplicates(["Name"], keep='last', inplace=True)
                df0.reset_index(drop=True, inplace=True)
                df0['Shift_AB'] = hr_sh_ab
                df0['Shift_DN'] = hr_sh_dn
                if len(hr_sh_date) == 10:
                    df0['Date'] = hr_sh_date
                    table = 'c2_hr'
                    df2mysql6878_app(df0, table)
                    #AUO_No, Name, Job_Type, Shift_AB, Shift_DN, Date
                    time.sleep(1)
                    
                    upload_ans = "上傳成功!!!"
                    table = 'c2_hr'
                    df_table = mysql2df6878(table)
                    df_table = df_table[df_table['Shift_AB'] != 'Normal'].copy()
                else:
                    upload_ans = "上傳失敗: 日期有誤"
                
                
            
            
        else:
            upload_ans = "上傳失敗: 班別有誤"
    
    print('hr_name', hr_name)
    
    
    todat_dt = datetime.datetime.today()
    df_table['Date_Diff'] = df_table['Date'].apply(lambda x: ( datetime.datetime.strptime(x, "%Y-%m-%d") - todat_dt).days )
        # 去除舊的資料，只留一筆(當前班別)
    filter0 = df_table["Date_Diff"] < 0 
    df_table.loc[filter0, 'Date_Diff'] = -9999
    df_table.drop_duplicates(["Name","Date_Diff"], keep='last', inplace=True)
    
    #df_indiv = df_indiv[df_indiv["Date_Diff"] >= 0 ].copy()
    cols = ["Name", "Shift_DN", "Shift_AB", "Date"]
    df_table = df_table[cols]
    df_table.reset_index(drop=True,inplace=True)
    
    
    
    if hr_name not in ["查詢&變更班別", "---", ""]:
        
        df_indiv = df_table[df_table['Name'] == hr_name].copy()
        """
        df_indiv['Date_Diff'] = df_indiv['Date'].apply(lambda x: ( datetime.datetime.strptime(x, "%Y-%m-%d") - todat_dt).days )
        # 去除舊的資料，只留一筆(當前班別)
        filter0 = df_indiv["Date_Diff"] <= 0 
        df_indiv.loc[filter0, 'Date_Diff'] = -9999
        df_indiv.drop_duplicates(["Name","Date_Diff"], keep='last', inplace=True)
        
        #df_indiv = df_indiv[df_indiv["Date_Diff"] >= 0 ].copy()
        cols = ["Name", "Shift_DN", "Shift_AB", "Date"]
        df_indiv = df_indiv[cols]
        """
        df_indiv.reset_index(drop=True,inplace=True)
        
        #df_indiv.drop_duplicates(cols, keep='last', inplace=True)
    else:
        cols = ["Name", "Shift_DN", "Shift_AB", "Date"]
        df_indiv = pd.DataFrame(columns=cols)
        df_indiv.loc[0, "Name"] = ""
        hr_name = ""
        
    return render_template('userMain.html', user=str(user),name=name, auth=auth, shift=shift, 
                           sectShow=sectShow, df_table=df_table, df_indiv=df_indiv, upload_ans=upload_ans)

def hr_changeShift_upload(user,name, auth, shift):
    1
