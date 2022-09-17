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
import pymysql
import numpy as np

from sqlalchemy import create_engine
from flask import Flask, render_template, request, redirect,flash
from flask import send_file, send_from_directory
from flask import app
from flask import url_for
from flask import flash
from mysql_to_df import *
print(101+int(time.strftime("%W")))
def mysql2df222(table):
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


def df2mysql222(df0, table):
    if 1:
            # pdData.index[pdData['Machine'] == 'CCCGL400'].tolist()[0]

            #回傳資料庫
        engine = create_engine("mysql+pymysql://craig945:ml7ac222@localhost:3306/craig01") 
        #delete = 'DROP TABLE IF EXISTS maint;'
        #engine.execute(delete)                 
        print('create_engine ok')
        df0.to_sql(table, engine, if_exists='replace',index=False) 
        print('to_sql ok')
        engine.dispose()
                              
    else:
        print('df2mysql -> '+table+'  發生except')
        logging.info('df2mysql -> '+table+'  發生except')
        engine.dispose()
        return 'except'

def df2mysql_app222(df0, table):
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
        return True
                              
    except:
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
    #print('yes')
    df_data = pd.DataFrame(cursor.fetchall())
    
    new_cols = [i[0] for i in cursor.description]
    old_cols = df_data.columns
    df_data.rename(columns=dict(zip(old_cols, new_cols)),inplace=True)
    return df_data

def req2(server_path, proxies = {'http':"http://10.97.4.1:8080",}):
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
    
def datesListStr(start_date, end_date):

    start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    date_generated = [start + datetime.timedelta(days=x) for x in range(0, (end-start).days+1)]
    date_list=[]
    for date in date_generated:
        date_list.append(date.strftime("%Y-%m-%d"))

    return date_list
    



def lsrCJScrapped(user,name, auth, shift, date, hd_filter,isSection = False):
    sectShow = 'lsrCJScrapped'
    today0 = datetime.date.today().strftime("%Y%m%d")
    today = today0[0:4]+'-'+today0[4:6]+'-'+today0[6:8]
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    logging.info('lsrCJScrapped, '+now)
    date_dt = datetime.datetime.strptime(date, "%Y-%m-%d")
    date_diff14 = (date_dt+datetime.timedelta(-14)).strftime("%Y-%m-%d")
    hd_range = list(range(500))
    if hd_filter in [0]:
        hd_range = list(range(0, 3))
    elif hd_filter in [3, 5]:
        hd_range = list(range(hd_filter, hd_filter+2))
    elif hd_filter == 7:
        hd_range = list(range(7, 10))
    elif hd_filter == 10:
        hd_range = list(range(10, 20))
    elif hd_filter == 20:
        hd_range = list(range(20, 500))
    today_dt = datetime.datetime.now()
    
    # 下載修片資料
    table = 'lsr_cj_scrapped'
    lsr_cj_scrapped = mysql2df(table)
    update_day = ""
    try:
        update_day = lsr_cj_scrapped.loc[0]['Update']
        lsr_cj_scrapped.drop(columns=['Update'], inplace=True)
    except:
        1
    
    
    defs_list = []
    original_col = []
    boxes_list = []
    holdNotes_list = []
    for i in range(len(lsr_cj_scrapped)):
        defect = lsr_cj_scrapped.loc[i]['DEFECT_CODE']
        box = lsr_cj_scrapped.loc[i]['BOX']
        hn = lsr_cj_scrapped.loc[i]['HOLD_NOTE']
        if defect not in original_col:
            original_col.append(defect)
        if box not in boxes_list:
            boxes_list.append(box)
        
    req_list = list(request.form)[:-1]
    select_box = request.form.get("select_box")
    select_holdNote = request.form.get("select_holdNote")
    button_val = request.form.get('lsrCJScrapped')
    if button_val is not None and  ("CJ 救報廢" in request.form.get('lsrCJScrapped')):
        isSection = True
    #判斷是不是從側邊按的
    if select_box is None:# or select_box == "NA":
        defs_list = original_col       
        
    else:
        for item in req_list:
            if item[0:6] == 'cjchk_':
                defs_list.append(item[6:])
    # hold date >3, >5, >7天的數量計算
    hdCount_list = [0, 0, 0, 0, 0, 0]
    drop_list = []
    total_count = len(lsr_cj_scrapped)
    
    
    lsr_cj_scrapped['HOLD_DATE'] = lsr_cj_scrapped['HOLD_DATE'].apply(lambda x: (today_dt - datetime.datetime.strptime(x, "%Y-%m-%d")).days)
    
    
    
    
    # 下載修片記錄
    table = 'lsr_cj_history'
    df_db_cjhistory = mysql2df(table)
    # 只去除當天判過的片子
    db_chipids = list(df_db_cjhistory[df_db_cjhistory['FIXED_DATE'].str.contains(today)]['TFT_CHIP_ID'])
    lsr_cj_scrapped2 = lsr_cj_scrapped[~lsr_cj_scrapped['TFT_CHIP_ID'].isin(db_chipids)].copy()
    if len(lsr_cj_scrapped2) == 0:
        lsr_cj_scrapped = pd.DataFrame(columns=lsr_cj_scrapped.columns)
    else:
        lsr_cj_scrapped = lsr_cj_scrapped2.copy()
    hdCount_list[5] = (lsr_cj_scrapped['HOLD_DATE']>= 20).sum()
    hdCount_list[4] = lsr_cj_scrapped['HOLD_DATE'].isin(list(range(10, 20))).sum()
    hdCount_list[3] = lsr_cj_scrapped['HOLD_DATE'].isin(list(range(7, 10))).sum()
    hdCount_list[2] = len(lsr_cj_scrapped[lsr_cj_scrapped['HOLD_DATE'].isin(list(range(5, 7)))])
    hdCount_list[1] = lsr_cj_scrapped['HOLD_DATE'].isin(list(range(3, 5))).sum()
    hdCount_list[0] = lsr_cj_scrapped['HOLD_DATE'].isin(list(range(0, 3))).sum()
    if hd_filter >= 0:
        lsr_cj_scrapped = lsr_cj_scrapped[lsr_cj_scrapped['HOLD_DATE'].isin(hd_range)].copy()
        print(hdCount_list[1], len(lsr_cj_scrapped))
    
    #lsr_cj_scrapped['HOLD_DATE'] = (today_dt - lsr_cj_scrapped['HOLD_DATE'].copy()).days
    
    #datetime.datetime.strptime(hold_date, "%Y-%m-%d")
    
    if not isSection:

        for i in lsr_cj_scrapped.index:
            chipid = lsr_cj_scrapped.loc[i]['TFT_CHIP_ID']
            db_date = lsr_cj_scrapped.loc[i]['START_DATE']
            defect = lsr_cj_scrapped.loc[i]['DEFECT_CODE']
            box = lsr_cj_scrapped.loc[i]['BOX']
            hn = lsr_cj_scrapped.loc[i]['HOLD_NOTE']
            #hold_date = lsr_cj_scrapped.loc[i]['HOLD_DATE']
            #hold_date_dt = datetime.datetime.strptime(hold_date, "%Y-%m-%d")
            #hd_days = (today_dt - hold_date_dt).days
            hd_days = lsr_cj_scrapped.loc[i]['HOLD_DATE']
            lsr_cj_scrapped.loc[i, 'HOLD_DATE'] = hd_days
            """
            if hd_days >= 20:
                hdCount_list[4] += 1
            elif hd_days in range(10, 20):
                hdCount_list[3] += 1
            elif hd_days in range(7, 10):
                hdCount_list[2] += 1
            elif hd_days in range(5, 7):
                hdCount_list[1] += 1
            elif hd_days in range(3, 5):
                hdCount_list[0] += 1
            """
            
            """
            # 過濾時才觸發
            if hd_filter > 0:
                if hd_days not in hd_range: 
                    drop_list.append(i)
                    continue
            """
            if str(db_date) != date_diff14:
                drop_list.append(i)
            elif defect not in defs_list:
                drop_list.append(i)
            elif select_box is not None and select_box != "ALL" and select_box != box:
                drop_list.append(i)
                #print(select_holdNote, hn)
            elif select_holdNote is not None and select_holdNote != "ALL" and select_holdNote != hn:
                drop_list.append(i)
            """
            else:
                df0 = df_db_cjhistory[(df_db_cjhistory['TFT_CHIP_ID']==chipid) ]
                if len(df0) > 0:
                    drop_list.append(i)
                      
            """
        
        lsr_cj_scrapped.drop(index=drop_list, inplace=True)
        lsr_cj_scrapped.reset_index(drop=True, inplace=True)
    else:
        for i in lsr_cj_scrapped.index:
            #hold_date = lsr_cj_scrapped.loc[i]['HOLD_DATE']
            #hold_date_dt = datetime.datetime.strptime(hold_date, "%Y-%m-%d")
            #hd_days = (today_dt - hold_date_dt).days
          
            hd_days = lsr_cj_scrapped.loc[i]['HOLD_DATE']
            """
            if hd_days >= 20:
                hdCount_list[4] += 1
            elif hd_days in range(10, 20):
                hdCount_list[3] += 1
            elif hd_days in range(7, 10):
                hdCount_list[2] += 1
            elif hd_days in range(5, 7):
                hdCount_list[1] += 1
            elif hd_days in range(3, 5):
                hdCount_list[0] += 1
            """
        lsr_cj_scrapped = pd.DataFrame(columns=lsr_cj_scrapped.columns)
        
    #mach = [ [0,'CCCGL1082',1], [1,'CCCGL1083',0], [2,'CCCGL2082', 1], [3,'CCCGL2083', 0] ]st.values.tolist(), maint_showIdx=maint_showIdx, mi 
    
    return render_template('userMain.html', user=str(user),name=name, auth=auth, shift=shift,
    sectShow=sectShow, lsr_cj_scrapped=lsr_cj_scrapped, date=date,
    defs_list=defs_list, original_col=original_col, boxes_list=boxes_list,
    select_box=select_box, select_holdNote=select_holdNote, hdCount_list=hdCount_list,
    total_count=total_count, update_day=update_day)
    

def lsrCJScrapped_Upload(user,name, auth, shift, date):
    sectShow = 'lsrCJScrapped'
    today_dt = datetime.datetime.now()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    date_diff14 = (today_dt+datetime.timedelta(-14)).strftime("%Y-%m-%d")
    hd_filter = 0
    logging.info('lsrCJScrapped_Upload, '+now)
    
    
    #號稱避免numpy.float64上傳錯誤
    pymysql.converters.encoders[np.float64] = pymysql.converters.escape_float
    pymysql.converters.encoders[np.int64] = pymysql.converters.escape_int
    pymysql.converters.conversions = pymysql.converters.encoders.copy()
    pymysql.converters.conversions.update(pymysql.converters.decoders)
    # 下載修片記錄
    table = 'lsr_cj_scrapped'
    lsr_cj_scrapped = mysql2df(table)
    
    req_list = list(request.form)[:-1]
    
    # 下載修片記錄
    table = 'lsr_cj_history'
    db_data = mysql2df(table)
    df_cjhistory = pd.DataFrame(columns=db_data.columns)
    
    save_list = ['cjFix_eqp', 'cjFix_method', 'cjFix_ok', 'cjFix_anotherMethod']
    #print(req_list)
    idx = 0
    for item in req_list:
        
        aaa = item.split('__', 2)
        if len(aaa) == 2 :

            chipid = aaa[0]
            col = aaa[1]
            
            # 手動輸入
            if len(chipid) <= 5:
                # 手動0~5 字樣
                idx = 500-int(chipid[2:])
                check_name0 = chipid + '__cjFix_ok'
                #print(idx, col)
                if col == 'cjFix_ok':
                    # 補上維修日期為當天
                    df_cjhistory.loc[idx, 'FIXED_DATE'] = now
                    df_cjhistory.loc[idx, 'FIXED_USER'] = user
                    df_cjhistory.loc[idx, 'FIXED_NAME'] = name
                    okng = request.form.get(item)
                    df_cjhistory.loc[idx, 'cjFix_ok'] = okng
                    continue
                elif check_name0 in req_list:
                    val0 = request.form.get(item)
                    df_cjhistory.loc[idx, col] = val0
                    
            elif col == 'cjFix_ok':
                # 補上維修日期為當天
                
                df0 = lsr_cj_scrapped[(lsr_cj_scrapped['START_DATE'] == date_diff14) & (lsr_cj_scrapped['TFT_CHIP_ID'] == chipid)]
                df_cjhistory.loc[idx] = df0.loc[df0.index[-1]].copy()
                df_cjhistory.loc[idx, 'FIXED_DATE'] = now
                df_cjhistory.loc[idx, 'FIXED_USER'] = user
                df_cjhistory.loc[idx, 'FIXED_NAME'] = name
                        
                """
                for i in range(len(lsr_cj_scrapped)):
                    db_date = lsr_cj_scrapped.loc[i]['START_DATE']
                    db_chipid = lsr_cj_scrapped.loc[i]['TFT_CHIP_ID']
                    if db_chipid == chipid and db_date == date_diff14:
                        for db_col in lsr_cj_scrapped.columns:
                            df_cjhistory.loc[idx, db_col] = lsr_cj_scrapped.loc[i][db_col]
                """
                for save_col in save_list:
                    req = request.form.get(chipid+'__'+save_col)
                    df_cjhistory.loc[idx, save_col] = req
                
                
                idx += 1
    #df_cjhistory.to_csv('df_cjhistory.csv', encoding = "utf-8",index=False)
    """
    for i in range(len(df_cjhistory)):
        for col in df_cjhistory.columns:
            #print(df_cjhistory.loc[i][col], type(df_cjhistory.loc[i][col]))
    """
    
    df_cjhistory.reset_index(drop=True, inplace=True)
    #(df_cjhistory)
    df2mysql_app(df_cjhistory, table)
    
    return lsrCJScrapped(user,name, auth, shift, date, hd_filter, isSection=True)       
    

    #lsr_cj_scrapped = lsr_cj_scrapped.drop(index=drop_list)
    #lsr_cj_scrapped = lsr_cj_scrapped.reset_index()
    #lsr_cj_scrapped = lsr_cj_scrapped.drop(columns=['index'])
    #return render_template('userMain.html', user=str(user),name=name, auth=auth, shift=shift, sectShow=sectShow, lsr_cj_scrapped=lsr_cj_scrapped)

def lsrCJScrapped_history(user,name, auth, shift , date1, date2):
    
    sectShow = 'lsrCJScrapped_history'
    date1_dt = datetime.datetime.strptime(date1, "%Y-%m-%d")
    date2_dt = datetime.datetime.strptime(date2, "%Y-%m-%d")
    date1_diff14 = (date1_dt+datetime.timedelta(-14)).strftime("%Y-%m-%d")
    date2_diff14 = (date2_dt+datetime.timedelta(-14)).strftime("%Y-%m-%d")

    date_list = datesListStr(date1, date2)
    dates_contains = ""
    for date0 in date_list:
        dates_contains += (date0 + '|')
    dates_contains = dates_contains[:-1]
    # 下載修片記錄
    table = 'lsr_cj_history'
    db_data0 = mysql2df(table)
    
    print(dates_contains)
    df_cjhistory = db_data0[db_data0['FIXED_DATE'].str.contains(dates_contains)]
    df_cjhistory.reset_index(drop=True, inplace=True)
    df_cjhistory.fillna(value = {'PRE_DEFECT_VALUE':'(手動KEY-IN)'}, inplace=True)
    try:
        btnName = list(request.form)[-1]
        filepath = r"static/csv/lsrCJScrapped_history_"+date1+"_"+date2+".csv"
        df_cjhistory.to_csv(filepath, index=False, encoding='utf-8-sig')
    except:
        print('csv儲存失敗:')
    #lsr_cj_scrapped = lsr_cj_scrapped.drop(index=drop_list)
    #lsr_cj_scrapped = lsr_cj_scrapped.reset_index()
    #lsr_cj_scrapped = lsr_cj_scrapped.drop(columns=['index'])
    
    return render_template('userMain.html', user=str(user),name=name, auth=auth, shift=shift, sectShow=sectShow, df_cjhistory=df_cjhistory, date1=date1, date2=date2)

# LASER單項找圖
def lsrDefectImg(chipid, eqp, isArray=False):
    dic_eqp2imgpath = {}
    dic_eqp2imgpath['CCLRA100'] = 'http://tcweb002.corpnet.auo.com/CCLRa102/CCLRa102/'
    dic_eqp2imgpath['CCLRA200'] = 'http://tcweb002.corpnet.auo.com/CCLRa202/CCLRa202/'
    dic_eqp2imgpath['CCLRB802'] = 'http://tcweb002.corpnet.auo.com/CCLRB802-laser/image/'
    dic_eqp2imgpath['CCLRB803'] = 'http://tcweb002.corpnet.auo.com/CCLRB803-laser/image/'
    dic_eqp2imgpath['CCLRB902'] = 'http://tcweb002.corpnet.auo.com/CCLRB902/image/'
    dic_eqp2imgpath['CCLRA702'] = 'http://tcweb002.corpnet.auo.com/CCLRA702/image/'
    dic_eqp2imgpath['CCLRA703'] = 'http://tcweb002.corpnet.auo.com/CCLRA703/image/'
    dic_eqp2imgpath['CCLRA802'] = 'http://tcweb002.corpnet.auo.com/CCLRA802/image/'
    if eqp not in dic_eqp2imgpath.keys():
        return []
    path_eqp = dic_eqp2imgpath[eqp]
    path_imgs = path_eqp+'/'+chipid[0:5]+'/'
    imgs_list =[]
    if eqp in ['CCLRA100', 'CCLRA200']:
        req = req2(path_imgs)
        webpage = html.fromstring(req.content)
        list_info = webpage.xpath('//pre/text()')
        list_dir = webpage.xpath('//a/text()')[1:]
        #imgs_list = AUOFab_PathList(path_imgs)[1]
        
        for idx in range(len(list_dir)):
            img_name = list_dir[idx]
            img = path_imgs + img_name
            
            if img_name[0:7] == chipid:
                imgs_list.append(img)
                #infos_list.append(list_info[idx])
                #df_chipImg.loc[newN, 'Info'] = list_info[idx]+'<br/>'+img_name
                
    elif eqp in ['CCLRB802', 'CCLRB803', 'CCLRB902', 'CCLRA702', 'CCLRA703', 'CCLRA802']:
        req = req2(path_imgs)
        webpage = html.fromstring(req.content)
        list_info = webpage.xpath('//pre/text()')
        list_dir = webpage.xpath('//a/text()')[1:]
        
        #imgs_list = AUOFab_PathList(path_imgs)[1]
        for idx in range(len(list_dir)):
            img_name = list_dir[idx]
            img = path_imgs + img_name
            if img_name[0:7] == chipid:
                imgs_list.append(img)
                #infos_list.append(list_info[idx])
                
                #df_chipImg.loc[newN, 'Info'] = list_info[idx]+'<br/>'+img_name
    return imgs_list

    if isArray:
        # array資料+影像
        sql = r"select t.LOT_ID, t.BOARD_ID, t.CHIP_ID, t.DATA_AX, t.GATE_AX,"
        sql += r" t.RP_FLAG, t.LSR_JUDGE, t.DFT_MODE, t.RETYPE, ROUTE" 
        #sql += r" ,t.image_no, t.image_path, t.image_file_name, t.image_start_seq_no"
        sql += r" from AT.ALR_RPF t"
        sql += r" where t.chip_id like '%"+chipid+"%'"
        df_arrayRaw = ora2df(sql)
        path0 = r"http://tcweb002.corpnet.auo.com/AcIMF001/Laser/Image/"
        for i in df_arrayRaw.index:
            lot_id = df_arrayRaw.loc[i]['LOT_ID']
            data_ax = df_arrayRaw.loc[i]['DATA_AX'].strip()
            gate_ax = df_arrayRaw.loc[i]['GATE_AX'].strip()
            route = df_arrayRaw.loc[i]['ROUTE'].strip()
            dft = df_arrayRaw.loc[i]['DFT_MODE']
            ax_keyword = data_ax +' '+ gate_ax 
            path_imgs = path0 + route + '/'+ lot_id
            #print(ax_keyword, dft)
            #imgs_list = []
            #infos_list = []
            req = req2(path_imgs)
            webpage = html.fromstring(req.content)
            list_info = webpage.xpath('//pre/text()')
            list_dir = webpage.xpath('//a/text()')[1:]
            img_count = 0
            #print(list_dir)
            for img in list_dir:
                if (ax_keyword in img) and (dft in img):
                    img_path = path_imgs +'/'+img
                    df_arrayRaw.loc[i, 'IMG_'+str(img_count)] = r"<a href='"+img_path+"'><img align='center' width='320' height='240' src='"+img_path+"'  ></a>"
                    img_count += 1
                    


def lsrBychip(user,name, auth, shift, chipid):
    sectShow = 'lsrBychip'
    print(chipid)
    isCell = False
    isArray = False
    Cell0 = request.form.get('Cell')
    Array0 = request.form.get('Array')
    print(Cell0, Array0)
    if Cell0 == 'on':
       isCell = True
    if Array0 == 'on':
       isArray = True
    proxies = {'http':'http://10.97.4.1:8080'}
    dic_eqp2imgpath = {}
    dic_eqp2imgpath['CCLRA100'] = 'http://tcweb002.corpnet.auo.com/CCLRa102/CCLRa102/'
    dic_eqp2imgpath['CCLRA200'] = 'http://tcweb002.corpnet.auo.com/CCLRa202/CCLRa202/'
    dic_eqp2imgpath['CCLRB802'] = 'http://tcweb002.corpnet.auo.com/CCLRB802-laser/image/'
    dic_eqp2imgpath['CCLRB803'] = 'http://tcweb002.corpnet.auo.com/CCLRB803-laser/image/'
    dic_eqp2imgpath['CCLRB902'] = 'http://tcweb002.corpnet.auo.com/CCLRB902/image/'
    dic_eqp2imgpath['CCLRA702'] = 'http://tcweb002.corpnet.auo.com/CCLRA702/image/'
    dic_eqp2imgpath['CCLRA703'] = 'http://tcweb002.corpnet.auo.com/CCLRA703/image/'
    dic_eqp2imgpath['CCLRA802'] = 'http://tcweb002.corpnet.auo.com/CCLRA802/image/'

    df_chipImg = pd.DataFrame(columns=['CHIP_ID', 'REWORK人員', '1st_TEST_DEFECT', '2nd_TEST_DEFECT', 'Info', 'IMAGE'])
    """
    if chipid is None:
        chipid = ""
    """
    df_chipRaw = pd.DataFrame()
    df_arrayRaw = pd.DataFrame()
        
    if chipid is not None:
        
        if isCell:
            sql = r"select distinct(t.tft_chip_id) as chip_id, t.pre_test_defect_code_desc as first_test_defect, "
            sql += r"t.rework_defect_code_desc as rework_defect, t.test_defect_code_desc as second_test_defect, "
            sql += r"t.grade,t.rework_user_id,t.eqp_id as EQ,t.rework_cnt " 
            sql += r"from celods.h_dax_rework_ods t "  
            sql += r"where t.site_type in ('BEOL') "  
            sql += r"and t.tft_chip_id = '" + chipid + "'"
            
            df_chipRaw = ora2df(sql)     
            df_chipRaw = df_chipRaw.rename(columns={'FIRST_TEST_DEFECT':'1st_TEST_DEFECT',
                                                    'SECOND_TEST_DEFECT':'2nd_TEST_DEFECT',
                                                    'REWORK_USER_ID':'REWORK人員'})
            
            
            
            newN = 0
            #path0 = r"http://tcweb002.corpnet.auo.com/"
            for i in range(len(df_chipRaw)):
                
                df_chipImg.loc[newN, 'Info'] = ' '
                df_chipImg.loc[newN, 'IMAGE'] = 'No image'
                df_chipImg.loc[newN, 'IMG_CNT'] = 0
                eqp = df_chipRaw.loc[i]['EQ']
                chipid = df_chipRaw.loc[i]['CHIP_ID']
                rework_id = df_chipRaw.loc[i]['REWORK人員']
                defect_1 = df_chipRaw.loc[i]['1st_TEST_DEFECT']
                defect_2 = df_chipRaw.loc[i]['2nd_TEST_DEFECT']
                try:
                    path_eqp = dic_eqp2imgpath[eqp]
                except: #Exception as e:
                    if eqp in ['CCCPD100']:
                        df_chipImg.loc[newN, 'CHIP_ID'] = chipid
                        df_chipImg.loc[newN, 'REWORK人員'] = rework_id
                        df_chipImg.loc[newN, '1st_TEST_DEFECT'] = defect_1
                        df_chipImg.loc[newN, '2nd_TEST_DEFECT'] = defect_2
                        df_chipImg.loc[newN, 'IMG_CNT'] = 1
                        newN += 1
                        continue
                    else:
                        df_chipImg.loc[newN, 'CHIP_ID'] = chipid
                        df_chipImg.loc[newN, 'REWORK人員'] = rework_id
                        df_chipImg.loc[newN, '1st_TEST_DEFECT'] = defect_1
                        df_chipImg.loc[newN, '2nd_TEST_DEFECT'] = defect_2
                        df_chipImg.loc[newN, 'IMG_CNT'] = 1
                        newN += 1
                        continue  
                    
                
                
                
                #path_img = path_eqp+'/'+rework_id[0:5]+'/'+rework_id+'_'+defect+'_'+signal+'_'+gate+'_'+alp+'.jpg'
                    
                    
                #img_list = AUOFab_PathList(path_imgs)[1]
                
              
                path_imgs = path_eqp+'/'+chipid[0:5]+'/'
                imgs_list = []
                infos_list = []
                if eqp in ['CCLRA100', 'CCLRA200']:
                    req = req2(path_imgs, proxies=proxies)
                    webpage = html.fromstring(req.content)
                    list_info = webpage.xpath('//pre/text()')
                    list_dir = webpage.xpath('//a/text()')[1:]
                    #imgs_list = AUOFab_PathList(path_imgs)[1]
                    first_newN = newN
                    for idx in range(len(list_dir)):
                        img_name = list_dir[idx]
                        img = path_imgs + img_name
                        
                        if img_name[0:7] == chipid:
                            imgs_list.append(img)
                            infos_list.append(list_info[idx])
                            df_chipImg.loc[newN, 'CHIP_ID'] = chipid
                            df_chipImg.loc[newN, 'REWORK人員'] = rework_id
                            df_chipImg.loc[newN, '1st_TEST_DEFECT'] = defect_1
                            df_chipImg.loc[newN, '2nd_TEST_DEFECT'] = defect_2
                            df_chipImg.loc[newN, 'Info'] = list_info[idx]+'<br/>'+img_name
                            df_chipImg.loc[newN, 'IMAGE'] = img
                            df_chipImg.loc[newN, 'IMG_CNT'] = 0
                            newN += 1
                    df_chipImg.loc[first_newN, 'IMG_CNT'] = newN - first_newN
                            
                elif eqp in ['CCLRB802', 'CCLRB803', 'CCLRB902', 'CCLRA702', 'CCLRA703', 'CCLRA802']:
                    req = req2(path_imgs, proxies=proxies)
                    webpage = html.fromstring(req.content)
                    list_info = webpage.xpath('//pre/text()')
                    list_dir = webpage.xpath('//a/text()')[1:]
                    first_newN = newN
                    #imgs_list = AUOFab_PathList(path_imgs)[1]
                    for idx in range(len(list_dir)):
                        img_name = list_dir[idx]
                        img = path_imgs + img_name
                        if img_name[0:7] == chipid:
                            imgs_list.append(img)
                            infos_list.append(list_info[idx])
                            df_chipImg.loc[newN, 'CHIP_ID'] = chipid
                            df_chipImg.loc[newN, 'REWORK人員'] = rework_id
                            df_chipImg.loc[newN, '1st_TEST_DEFECT'] = defect_1
                            df_chipImg.loc[newN, '2nd_TEST_DEFECT'] = defect_2
                            df_chipImg.loc[newN, 'Info'] = list_info[idx]+'<br/>'+img_name
                            df_chipImg.loc[newN, 'IMAGE'] = img
                            df_chipImg.loc[newN, 'IMG_CNT'] = 0
                            newN += 1
                    df_chipImg.loc[first_newN, 'IMG_CNT'] = newN - first_newN
                    
                    
                    
            
                            
                else:
                    continue
                if len(infos_list) > 0:
                    1
                    #df_chipRaw.loc[i, 'Info'] = infos_list[0]
                    #df_chipRaw.loc[i, 'IMAGE'] = imgs_list[0]
        
        if isArray:
            # array資料+影像
            sql = r"select t.LOT_ID, t.BOARD_ID, t.CHIP_ID, t.DATA_AX, t.GATE_AX,"
            sql += r" t.RP_FLAG, t.LSR_JUDGE, t.DFT_MODE, t.RETYPE, ROUTE" 
            #sql += r" ,t.image_no, t.image_path, t.image_file_name, t.image_start_seq_no"
            sql += r" from AT.ALR_RPF t"
            sql += r" where t.chip_id like '%"+chipid+"%'"
            df_arrayRaw = ora2df(sql)
            path0 = r"http://tcweb002.corpnet.auo.com/AcIMF001/Laser/Image/"
            for i in df_arrayRaw.index:
                lot_id = df_arrayRaw.loc[i]['LOT_ID']
                data_ax = df_arrayRaw.loc[i]['DATA_AX'].strip()
                gate_ax = df_arrayRaw.loc[i]['GATE_AX'].strip()
                route = df_arrayRaw.loc[i]['ROUTE'].strip()
                dft = df_arrayRaw.loc[i]['DFT_MODE']
                ax_keyword = data_ax +' '+ gate_ax 
                path_imgs = path0 + route + '/'+ lot_id
                #print(ax_keyword, dft)
                #imgs_list = []
                #infos_list = []
                req = req2(path_imgs, proxies=proxies)
                webpage = html.fromstring(req.content)
                list_info = webpage.xpath('//pre/text()')
                list_dir = webpage.xpath('//a/text()')[1:]
                img_count = 0
                #print(list_dir)
                for img in list_dir:
                    if (ax_keyword in img) and (dft in img):
                        img_path = path_imgs +'/'+img
                        df_arrayRaw.loc[i, 'IMG_'+str(img_count)] = r"<a href='"+img_path+"'><img align='center' width='320' height='240' src='"+img_path+"'  ></a>"
                        img_count += 1
            df_arrayRaw.fillna('無', inplace=True)
        
        
    else:
        df_chipRaw = pd.DataFrame()
        df_arrayRaw = pd.DataFrame()
   
    
    
        
    
    if chipid is None:
        chipid = ''
    
    return render_template('userMain.html', user=str(user),name=name, auth=auth, shift=shift, sectShow=sectShow,
                           df_chipRaw=df_chipRaw, df_chipImg=df_chipImg, df_arrayRaw=df_arrayRaw,
                           chipid=chipid)
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
    
    return [octaoi_imgs, octadc_imgs]




def rjCheck(date1, date2):
    #  RJ Check ZPN,RA,RB算成功 (Target:85%, > 30 Pcs)
    sql = r"select distinct(t.tft_chip_id) as chip_id,t.product_code, t.grade,t.defect_code_desc,t.test_user,t.tool_id,t.mfg_day, t.test_time"
    sql += r" from celods.h_dax_fbk_test_ods t"
    sql += r" where t.site_type in ('BEOL')"
    sql += r" and t.pre_grade in ('RJ')"
    sql += r" and t.pre_defect_code_desc in ('V-OPEN')"
    sql += r" and t.grade is not NULL"
    sql += r" and mfg_day between to_date('" + date1 + "','yyyy-mm-dd') and to_date('" + date2 + "','yyyy-mm-dd')"
    
    # 改良版本  追加defect Table資料(ct1坐標)
    sql = r"select distinct(t.tft_chip_id)as CHIP_ID,t.product_code, t.grade,t.defect_code_desc, t.judge_cnt,"
    sql += r" t.test_user, t.test_time,t.tool_id,t.mfg_day, b.test_user as ct1_eqp, b.defect_code_desc as ct1_defect,  b.test_signal_no as ct1_x, b.test_gate_no as ct1_y"
    sql += r" from("
    sql += r" select *"
    sql += r" from celods.h_dax_fbk_test_ods t"
    sql += r" where t.site_type in ('BEOL')"
    sql += r" and t.pre_grade in ('RJ')"
    sql += r" and t.pre_defect_code_desc in ('V-OPEN')"
    sql += r" and t.grade is not NULL"
    sql += r" and mfg_day between to_date('" + date1 + "','yyyy-mm-dd') and to_date('" + date2 + "','yyyy-mm-dd')"
    sql += r" )t"
    sql += r" left join celods.h_dax_fbk_defect_ods b on t.tft_chip_id = b.tft_chip_id"
    #sql += r" and b.judge_cnt < t.judge_cnt"
    sql += r" and b.test_op_id = 'CGL' and b.major_defect_flag = 'Y'"
    sql += r" and b.judge_flag = 'L'"
    sql += r" and b.test_mfg_day > (to_date('" + date1 + "','yyyy-mm-dd') - interval '90' day)"
    
    # 改良版本2  追加defect Table資料(oct覆判坐標)
    sql = r"select distinct(t.tft_chip_id)as CHIP_ID,t.product_code, t.grade,t.defect_code_desc, t.judge_cnt,"
    sql += r" t.test_user, t.test_time,t.tool_id,t.mfg_day, b.test_user as oct2_user, b.test_signal_no as oct2_x, b.test_gate_no as oct2_y"
    sql += r" from("
    sql += r" select *"
    sql += r" from celods.h_dax_fbk_test_ods t"
    sql += r" where t.site_type in ('BEOL')"
    sql += r" and t.pre_grade in ('RJ')"
    sql += r" and t.pre_defect_code_desc in ('V-OPEN')"
    sql += r" and t.grade is not NULL"
    sql += r" and mfg_day between to_date('" + date1 + "','yyyy-mm-dd') and to_date('" + date2 + "','yyyy-mm-dd')"
    sql += r" )t"
    sql += r" left join celods.h_dax_fbk_defect_ods b on t.tft_chip_id = b.tft_chip_id"
    sql += r" and b.test_judge_cnt = t.judge_cnt"
    #sql += r" and b.test_op_id = 'OCT2' 
    sql += r" and b.major_defect_flag = 'Y'"
    #sql += r" and b.judge_flag = 'L'"
    sql += r" and b.test_mfg_day > (to_date('" + date1 + "','yyyy-mm-dd') - interval '90' day)"
    
    
    

    
    raw_data0 = ora2df(sql)
    raw_data0.drop_duplicates(['CHIP_ID'], keep='last', inplace=True)
    raw_data0.reset_index(drop=True, inplace=True)
    return raw_data0

def lsrRJCheck(user,name, auth, shift, date1, date2):
    
    sectShow = 'lsrRJCheck'
    # Udefectq
    raw_data0 = rjCheck(date1, date2)
    #print(raw_data0)
    if len(raw_data0) == 0:
        lsrRJCheck = raw_data0
    else:
        raw_data0.fillna({'DEFECT_CODE_DESC':'   '}, inplace=True)
        raw_data1 = raw_data0.groupby(['PRODUCT_CODE', 'TOOL_ID', 'DEFECT_CODE_DESC'])
        raw_data2 = raw_data1.size().to_frame(name='COUNT')
        raw_data2 = raw_data2.reset_index()
        raw_data1 = raw_data0.groupby(['PRODUCT_CODE', 'TOOL_ID', 'GRADE'])
        raw_data3 = raw_data1.size().to_frame(name='COUNT')
        raw_data3 = raw_data3.reset_index()
        #print(raw_data3)
        #print(raw_data2)
        #[`w
        vo_raw = raw_data2[(raw_data2['DEFECT_CODE_DESC'].isin(['V-OPEN']))]
        df_vo = vo_raw.groupby(['PRODUCT_CODE', 'TOOL_ID'])['COUNT'].agg('sum').to_frame(name='VO')
        
        bls_raw = raw_data2[(raw_data2['DEFECT_CODE_DESC'].str.contains('-BL'))]
        df_bls = bls_raw.groupby(['PRODUCT_CODE', 'TOOL_ID'])['COUNT'].agg('sum').to_frame(name='BLs')
        # 名稱有other類的
        oths_raw = raw_data2[(raw_data2['DEFECT_CODE_DESC'].str.contains('OTHER'))]
        df_oths = oths_raw.groupby(['PRODUCT_CODE', 'TOOL_ID'])['COUNT'].agg('sum').to_frame(name='OTHERs')
        # 成功率計算  ZPN,RA,RB算成功 (Target:85%, > 30 Pcs)
        suc_raw = raw_data3[(raw_data3['GRADE'].isin(['Z', 'P', 'N', 'RA', 'RB']))]
        df_suc = suc_raw.groupby(['PRODUCT_CODE', 'TOOL_ID'])['COUNT'].agg('sum').to_frame(name='Target')
        
    
        df_tot = raw_data2.groupby(['PRODUCT_CODE', 'TOOL_ID'])['COUNT'].agg('sum').to_frame(name='總數')
          
         
        # X
        lsrRJCheck = pd.concat([df_vo, df_bls, df_oths, df_suc, df_tot], verify_integrity = True, axis=1)
        lsrRJCheck = lsrRJCheck.fillna(0)
        
        lsrRJCheck = lsrRJCheck.reset_index()
        
        #octADCRBSamp[['OGD', 'BPs', '', 'CP']] = octADCRBSuc[['OGD', 'BPs', '', 'CP']].astype('int')
        lsrRJCheck['VO(%)'] = 100*lsrRJCheck['VO'] / lsrRJCheck['總數']
        lsrRJCheck['BLs(%)'] = 100*lsrRJCheck['BLs'] / lsrRJCheck['總數']
        lsrRJCheck['OTHERs(%)'] = 100*lsrRJCheck['OTHERs'] / lsrRJCheck['總數']
        lsrRJCheck['Target'] = 100*lsrRJCheck['Target'] / lsrRJCheck['總數']
        
        
        #octADCRBSamp['總(%)'] = octADCRBSamp['ZP(%)'] + octADCRBSamp['Sampling(%)']
        lsrRJCheck['OCT人員漏檢'] = 0
        lsrRJCheck['OCT人員漏標'] = 0
        lsrRJCheck['來料Defect影響'] = 0
        lsrRJCheck['PFL貼附異常影響'] = 0
        lsrRJCheck['OCT機台誤判'] = 0
        lsrRJCheck['Laser修錯'] = 0
        lsrRJCheck['其他請說明'] = 0
        lsrRJCheck['待確認'] = lsrRJCheck['VO'] + lsrRJCheck['BLs'] + lsrRJCheck['OTHERs']


        
        table = 'lsr_rjcheck'
        db_data = mysql2df(table)
        
        for item in lsrRJCheck.index:
            
            tool_id = lsrRJCheck.loc[item]['TOOL_ID']
            pc = lsrRJCheck.loc[item]['PRODUCT_CODE']
            db_data1 = db_data[(db_data['TOOL_ID']==tool_id) & (db_data['PRODUCT_CODE']==pc)]
            
            defect_keys = 'V-OPEN|-BL|OTHER'
            #raw_data1 = raw_data0[(raw_data0['TOOL_ID'] == tool_id) & (raw_data0['PRODUCT_CODE'] == pc)]
            lsrRJCheckRaw = raw_data0[(raw_data0['DEFECT_CODE_DESC'].str.contains(defect_keys)) & (raw_data0['TOOL_ID'] == tool_id) & (raw_data0['PRODUCT_CODE'] == pc)].copy()
        

            for i in lsrRJCheckRaw.index:
                chipid0 = lsrRJCheckRaw.loc[i]['CHIP_ID']
                jud_cnt0 = str(lsrRJCheckRaw.loc[i]['JUDGE_CNT'])

                df0 = db_data1[(db_data1['CHIP_ID']==chipid0) & (db_data1['JUDGE_CNT']==jud_cnt0)]
                if len(df0) > 0:
                    last_n = df0.index[-1]
                    #df0.drop_duplicates(['CHIP_ID', 'OCT_DEFECT'], keep='last', inplace=True)
                    okng = df0.loc[last_n]['Check']
                    #remarks = df0.loc[last_n]['name']+', '+df0.loc[last_n]['Remarks']
                    
                    if okng in ['OCT人員漏檢', 'OCT人員漏標', '來料Defect影響', 'PFL貼附異常影響', 'OCT機台誤判', 'Laser修錯', '其他請說明']:
                        lsrRJCheck.loc[item, okng] = lsrRJCheck.loc[item][okng] + 1
                        lsrRJCheck.loc[item, '待確認'] = lsrRJCheck.loc[item]['待確認'] - 1
                        #octADCRBSuc.loc[item, def_col+'T{(%)'] = octADCRBSuc.loc[item][def_col+'T{(%)'] - 1
            #octADCRBSamp.loc[item, def_col+'T{(%)'] = 100*octADCRBSuc.loc[item][def_col+'T{(%)']/tot
       
        
        lsrRJCheck = lsrRJCheck.round(2)
        lsrRJCheck.loc[lsrRJCheck['總數'] < 30, 'Target'] = '片數<30'
    
    #lsrRJCheck = lsrRJCheck.astype('str')
    
    
    return render_template('userMain.html', user=str(user),name=name, auth=auth, shift=shift, sectShow=sectShow,
                           date1=date1, date2=date2, lsrRJCheck= lsrRJCheck)
    
def lsrRJCheckRaw(user,name, auth, shift, date1, date2, tool_id, pc, def_col):
    
    sectShow = 'lsrRJCheckRaw'
    
    raw_data0 = rjCheck(date1, date2)
    if def_col == 'VO':
        defect_key = 'V-OPEN'
    elif def_col == 'BLs':
        defect_key = '-BL'
    elif def_col == 'OTHERs':
        defect_key = 'OTHER'
    print(tool_id, pc, defect_key)
    lsrRJCheckRaw = raw_data0[(raw_data0['DEFECT_CODE_DESC'].str.contains(defect_key)) & (raw_data0['TOOL_ID'] == tool_id) & (raw_data0['PRODUCT_CODE'] == pc)].copy()
    #octADCRBSampRaw = octADCRBSampRaw.reset_index()
    #octADCRBSampRaw['IMG'] = 'NA'
    
    
    
    

    for idx in lsrRJCheckRaw.index:
        chipid0 = lsrRJCheckRaw.loc[idx]['CHIP_ID']
        cnt0 = lsrRJCheckRaw.loc[idx]['JUDGE_CNT']
        tool_id0 = lsrRJCheckRaw.loc[idx]['TOOL_ID']
        sql = r"select t.tft_chip_id, t.test_signal_no as x, t.test_gate_no as y, t.major_defect_flag, t.test_tool_id,"
        sql += r" t.test_op_id, t.test_time, t.test_user, t.test_judge_cnt as cnt, t.defect_code_desc"
        sql += r" from celods.h_dax_fbk_defect_ods t" 
        sql += r" where t.tft_chip_id = '"+ chipid0 +"'"
        sql += r" and t.test_mfg_day > (to_date('" + date1 + "','yyyy-mm-dd') - interval '90' day)"
    
        #sql += r" and t.test_user = 'CCCGL5083'"
        #sql += r" and t.test_op_id='CGL'"
        #sql += r" and t.major_defect_flag = 'Y'"
        sql += r" order by t.test_time"
        
        data0 = ora2df(sql)
        data1 = data0[(data0['CNT'] == cnt0-1) & (data0['MAJOR_DEFECT_FLAG'] == 'Y')]
        if len(data1) > 0:
            lsrRJCheckRaw.loc[idx, 'OCT1_USER'] = data1.loc[data1.index[-1]]['TEST_USER']
        data1 = data0[(data0['TEST_OP_ID'] == 'CGL')& (data0['MAJOR_DEFECT_FLAG'] == 'Y')]
        if len(data1) > 0:
            word0 = ""
            for iii in data1.index:
                word0 += data1.loc[iii]['DEFECT_CODE_DESC'] + ', '
            
            lsrRJCheckRaw.loc[idx, 'CT1_DEFECT'] = word0[:-2]
            
        #x0 = data1.loc[data1.index[-1]]['X']
        #y0 = data1.loc[data1.index[-1]]['Y']
        
        #lsrRJCheckRaw.loc[idx, 'OCT2_X'] = x0
        #lsrRJCheckRaw.loc[idx, 'OCT2_Y'] = y0

        x0 = lsrRJCheckRaw.loc[idx]['OCT2_X']
        y0 = lsrRJCheckRaw.loc[idx]['OCT2_Y']
        # 前一次oct是否同點
        df_isSame = data0[(data0['CNT'] == (cnt0-1)) & (data0['X'] == x0)  & (data0['Y'] == y0)]
        if len(df_isSame) > 0:
            lsrRJCheckRaw.loc[idx, 'isSameXY'] = 'Y'
        else:
            lsrRJCheckRaw.loc[idx, 'isSameXY'] = 'N'
        
        
       
        
        
        
        # 補LASER站點資料
        sql = r"select t.rework_user_id,t.eqp_id as laser_eqp, test_eqp_id, t.rework_signal_no as x, t.rework_gate_no as y"
        sql += r" from celods.h_dax_rework_ods t"   
        sql += r" where t.site_type in ('BEOL')"
        sql += r" and t.test_judge_cnt = "+ str(cnt0)
        sql += r" and t.tft_chip_id = '"+ chipid0 +"'"
        sql += r" order by t.rework_time"
        data0 = ora2df(sql)
        data1 = data0
        #data1 = data0[data0['TEST_EQP_ID'] == tool_id0]
        
        if len(data1) > 0:
            last_n = data1.index[-1]
            lsrRJCheckRaw.loc[idx, 'REWORK_USER_ID'] = data1.loc[last_n]['REWORK_USER_ID']
            lsrRJCheckRaw.loc[idx, 'LASER_EQP'] = data1.loc[last_n]['LASER_EQP']
            x0 = data1.loc[last_n]['X']
            color0 = int(x0)%3
            if color0 == 1:
                lsrRJCheckRaw.loc[idx, 'REPAIR_COLOR'] = 'RED'
            elif color0 == 2:
                lsrRJCheckRaw.loc[idx, 'REPAIR_COLOR'] = 'GREEN'
            elif color0 == 0:
                lsrRJCheckRaw.loc[idx, 'REPAIR_COLOR'] = 'BLUE'    
    lsrRJCheckRaw.reset_index(drop=True, inplace=True)
    lsrRJCheckRaw['確認'] = 'NA'
    lsrRJCheckRaw['說明'] = 'NA'
    #df_aoi = pd.DataFrame()
    #df_adc = pd.DataFrame()
    df_aoi = lsrRJCheckRaw[['CHIP_ID']].copy()
    df_adc = lsrRJCheckRaw[['CHIP_ID']].copy()
    df_lsr = lsrRJCheckRaw[['CHIP_ID', '確認', '說明' ]].copy()
    
    # d
    table = 'lsr_rjcheck'
    
    db_data = mysql2df(table)
    db_data1 = db_data[(db_data['TOOL_ID']==tool_id) & (db_data['PRODUCT_CODE']==pc)]
    
    for i in lsrRJCheckRaw.index:
        chipid = lsrRJCheckRaw.loc[i]['CHIP_ID']
        date0 = str(lsrRJCheckRaw.loc[i]['TEST_TIME'])
        date_oct = date0[0:4] + date0[5:7] + date0[8:10]
        eqp_oct = lsrRJCheckRaw.loc[i]['TOOL_ID']
        oct_def = lsrRJCheckRaw.loc[i]['DEFECT_CODE_DESC']
        #pre_test_user = octADCRBSamp.loc[i]['PRE_TEST_USER']
        laser_eqp = lsrRJCheckRaw.loc[i]['LASER_EQP']
        jud_cnt0 = str(lsrRJCheckRaw.loc[i]['JUDGE_CNT'])

        df0 = db_data1[(db_data1['CHIP_ID']==chipid) & (db_data1['JUDGE_CNT']==jud_cnt0)]
        if len(df0) > 0:
            last_n = df0.index[-1]
            #df0.drop_duplicates(['CHIP_ID', 'OCT_DEFECT'], keep='last', inplace=True)
            okng = df0.loc[last_n]['Check']
            remarks = df0.loc[last_n]['name']+', '+ str(df0.loc[last_n]['Remarks'])
            lsrRJCheckRaw.loc[i, '確認'] = str(okng)
            lsrRJCheckRaw.loc[i, '說明'] = str(remarks)
            df_lsr.loc[i, '確認'] = str(okng)
            df_lsr.loc[i, '說明'] = str(remarks)
        """
        octimgs = octDefectImg(chipid, date_oct, eqp_oct, oct_def)
        aoi_img = octimgs[0]
        adc_img = octimgs[1]
        
        for num0 in range(len(adc_img)):
            pattern= ""
            img_name = os.path.basename(adc_img[num0])
            spl = img_name.split('_')
            pattern = spl[3][1:]+'_'+spl[4] + '<br/>'
            df_adc.loc[i, 'IMG_'+str(num0)] = pattern + r"<a href='"+adc_img[num0]+"'><img align='center' width='160' height='120' src='"+adc_img[num0]+"'  ></a>"
        """
        # 找LASER影像
        
        lsrimgs = lsrDefectImg(chipid, laser_eqp)
        for num0 in range(len(lsrimgs)):
            df_lsr.loc[i, 'IMG_'+str(num0)] =  r"<a href='"+lsrimgs[num0]+"'><img align='center' width='160' height='120' src='"+lsrimgs[num0]+"'  ></a>"
        
    

 
    
    
    #print(octADCRBSampRaw)
    return render_template('userMain.html', user=str(user),name=name, auth=auth, shift=shift, sectShow=sectShow,
                           date1=date1, date2=date2, lsrRJCheckRaw= lsrRJCheckRaw, df_adc=df_adc, df_lsr=df_lsr)
def lsrRJCheckCT1(user,name, auth, shift, chipid):
    print(chipid)
    sectShow = 'lsrRJCheckCT1'
    sql = r"select t.tft_chip_id, t.test_signal_no, t.test_gate_no, t.major_defect_flag,"
    sql += r" t.test_time, t.test_user, t.defect_code_desc"
    sql += r" from celods.h_dax_fbk_defect_ods t" 
    sql += r" where t.tft_chip_id = '"+ chipid +"'"
    #sql += r" and t.test_user = 'CCCGL5083'"
    sql += r" and t.test_op_id='CGL'"
    sql += r" and t.test_mfg_day > (current_date - interval '90' day)"
    #sql += r" and t.major_defect_flag = 'Y'"
    sql += r" order by t.test_time"
    
    lsrRJCheckCT1 = ora2df(sql)
    return render_template('userMain.html', user=str(user),name=name, auth=auth, shift=shift, sectShow=sectShow,
                           lsrRJCheckCT1= lsrRJCheckCT1)
    
def lsrRJCheck_Upload(user,name, auth, shift, req_list):
    #^@h
    sectShow = 'lsrRJCheck'
    #sectShow = 'uploadOK'
    
    #df_dp2bp = pd.DataFrame(columns=['user', 'name', 'shift', 'auth']
    table = 'lsr_rjcheck'
    db_data = mysql2df(table)
    
    db_lsrRJCheck = pd.DataFrame(columns=db_data.columns)

    #db_lsrRJCheck = pd.DataFrame()
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
        if col in db_lsrRJCheck.columns or col in ['Check2', 'Remarks2']:
            #print(num, col, req)
            db_lsrRJCheck.loc[num, col] = req

    # OWHT
    cond0 = ~( (db_lsrRJCheck['Check2'].isin(['---'])) | (db_lsrRJCheck['Check2'].isnull()) )
    db_lsrRJCheck.loc[cond0, 'Check'] = db_lsrRJCheck.loc[cond0]['Check2']
    
    db_lsrRJCheck.loc[cond0, 'Remarks'] = db_lsrRJCheck.loc[cond0]['Remarks2']
    
    
    
    user_list = ['user', 'name', 'shift', 'auth']
    drop_list = []
    for m in db_lsrRJCheck.index:
        check0 = db_lsrRJCheck.loc[m]['Check']
        if check0 == '---' or check0 is None or pd.isna(check0):
            drop_list.append(m)
        for ii in user_list:
            req = request.form.get(ii)
            db_lsrRJCheck.loc[m, ii] = req
        db_lsrRJCheck.loc[m, 'Checked_Date'] = now_hm
        
        # sWMFG DATET
        #test_time = df_dp2bp.loc[newIdx+m]['TEST_TIME']
        #df_dp2bp.loc[newIdx+m,'TEST_TIME_MFG'] = testTime2MFG(str(test_time))
        
    db_lsrRJCheck.drop(index=drop_list, columns=['Check2', 'Remarks2'], inplace=True)
    print(db_lsrRJCheck)
    #db_ADCRBSuc.reset_index(inplace=True, drop=True)
    #db_ADCRBSuc = db_ADCRBSuc.drop(columns=['Check'])
    #print(db_ADCRBRej)
    df2mysql_app(db_lsrRJCheck, table)
    
    
    date1 = request.form.get('date1')
    date2 = request.form.get('date2')
    
    return lsrRJCheck(user,name, auth, shift, date1, date2)



