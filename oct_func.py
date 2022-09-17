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
    print('reuest中...   ', web0, end='   ')
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
    dates_list=[]
    for date in date_generated:
        dates_list.append(date.strftime("%Y-%m-%d"))

    return dates_list


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
    
    
def subDefect(eqp,chipid, test_date, chipid_times):
    # http://tcweb002.corpnet.auo.com/CCCGL8082/AOI%20Data/Defect_Image/Sub2/20210908/07/Defect/
    list0 = []
    
    
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
            last_imgPath = ''
            for img in imgs_list:
                if img.endswith('.tif'):
                    continue
                if img[0:7] == chipid:
                    last_imgPath = path0+img#break
            if last_imgPath != '':
                list0.append(last_imgPath)
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
            web_mura = r"http://10.97.212.30/AOI_Data_D/GrabImage/Source/IP1/"+ date_oct +r"/"+ chipid+"/"
            web_func = r"http://10.97.212.30/AOI_Data_D/GrabImage/Source/IP1/"+ date_oct +r"/"+ chipid+"/FunctionError/"
               
            
            imgs_path = AUOFab_PathList(web_mura)
            for img_idx in range(len(imgs_path[1])):
                if imgs_path[1][img_idx][-4:] in ['.bmp', '.BMP']:
                    octaoi_imgs.append(imgs_path[0][img_idx])
            
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
            web_func = r"http://10.97.212.99/AOI_Data_D/GrabImage/Defect/IP1/"+ date_oct +r"/"+ chipid+"/Func/"
            
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
                if imgs_path[1][img_idx][-4:] in ['.bmp']:
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
                    octaoi_imgs.append(path_aoimuras[num] +'/'+imgs_path[1][img_idx])
        
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
    

# 新版ct1找圖
def ct1DefectImg(date1, date2, model_no, defect, eqp, chipid):
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
    mysql += r"where t.test_mfg_day between to_date('" +date1+ "','YYYY/mm/DD') and to_date('" +date2+ "','YYYY/mm/DD') " 
    # 有些空值會遺漏
    mysql += r"and t.test_op_id = 'CGL' "
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
    mysql += r"where t2.test_mfg_day between to_date('" +date1+ "','YYYY/mm/DD') and to_date('" +date2+ "','YYYY/mm/DD') " 
    mysql += r"and t2.test_op_id = 'CGL' " 
    mysql += r"and t2.model_no='" +model_no+ "' " 
    mysql += r"and t2.defect_code_desc in ('" +defect+ "') " 
    mysql += r"and t2.test_user='" +eqp+ "' " 
    mysql += r"and t2.major_defect_flag = 'Y' "
    mysql += r"and t2.grade in ('W','X') " 
    mysql += r"and t2.judge_flag = 'L' "
    mysql += r") b on a.chipid=b.chipid and a.x=b.xx and a.y=b.yy "
    logging.info(mysql)
    try:
        ct1_summ2_chipid = ora2df(mysql)
        print(ct1_summ2_chipid)
    except:
        logging.info('<h1>ora2df失敗</h1>')
        return '<h1>ora2df失敗</h1>'
    pd.set_option('display.max_colwidth', None)
    #找圖ya
    #影像分成３個ｃｃｄ　依序放置ｌｉｓｔ　　３ x ｎ大小
    list0 = []
    proxies = {'http':'http://10.97.4.1:8080'}
    for i in range(len(ct1_summ2_chipid)):
        # 三顆ccd影像list初始化，三顆找完之後包進imgLinks中
        chipid = ct1_summ2_chipid.loc[i]['CHIPID']
        time00 = str(ct1_summ2_chipid.loc[i]['TEST_TIME'])[11:13]
        time35 = int(str(ct1_summ2_chipid.loc[i]['TEST_TIME'])[14:16])
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
        
        

        # 超高速串圖  開發中
        if ora_imgpath[2:12] == '10.10.10.4':
            print('高速找圖觸發: 10.10.10.4!!!!!')
            logging.info('高速bp找圖觸發: 10.10.10.4!!!!!')
            #aaa = r'\\10.10.10.4\AOI Data\Defect_Image\Sub3\20211004\12\Defect\C95M6CC_C3_PB48L_TBP_D5268_G1941.bmp'
            aa = ora_imgpath[21:]
            imgPath = r'http://tcweb002.corpnet.auo.com/'+ eqp + r'/AOI%20Data'+aa
            list0.append(imgPath)
            continue
       
        chipid_times = []
        if time00 == '00':
            chipid_times = [time00]
        elif time35 <= 6:
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
        subDefect_list = ['BP', 'H-OPEN', 'H-LINE', 'V-OPEN', 'V-LINE', 'X-SHORT', 'BP-PAIR']      
        ag_list = ['V-OPEN-BL', 'AROUND GAP MURA', 'WHITE SPOT', 'BLACK SPOT', 'H-BAND MURA']
        AO7_list = ['CCCGLA072', 'CCCGLA073']
        AO7Def_list = ['OTHER ALIGN DEFECT', 'OTHER GLASS DEFECT', 'OTHER APPEAR DEFECT']
        
        if defect in subDefect_list:
            logging.info('  '+chipid+', Pattern Code = '+str(subDefect_list))
            list0 = subDefect(eqp, chipid, test_date, chipid_times)
        
        elif defect in ag_list:
            #http://tcweb002.corpnet.auo.com/CCCGL8082/AOI%20Data/Ori_Image/AreaGrabber1/20211024/07/Source/CAGX6ZF_C1_PM_LB_FMura_S1_WithDefect
            #http://tcweb002.corpnet.auo.com/CCCGL8082/AOI%20Data/Ori_Image/AreaGrabber1/20211024/07/Source/CAGX6ZF_C1PM_LB_FMura_S1_WithDefect.bmp
            print('ag_list找圖觸發')
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
                    img_path = path0 + chipid +'_C'+ ag[-2] + '_P'+ pt + '_FMura_S' + ag[-2] + '_WithDefect.bmp'
                    list0.append(img_path)
                                #break
        
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
                    last_imgPath = ''
                    for img in imgs_list:
                        if img[0:7] == chipid:
                            print(path0+img)
                            logging.info('  找到chipid image:'+img)
                            last_imgPath = path0+img
                            #   多張的話，秀一張就好(坐標資料皆為0,0 無法查找)
                    if last_imgPath != '':
                        list0.append(last_imgPath)
                    
        elif ct1_summ2_chipid.loc[i]['PATTERN_CODE'] is None:
            1
            #list0.append('PT None')
            #暫不找圖
        # L模式 (OGD)
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
                            logging.info('  找到chipid image:'+img)
                            last_imgPath = path0+img
                    if last_imgPath != '':
                        list0.append(last_imgPath)
                            #break
            
                
        # M模式
        #http://tcweb002.corpnet.auo.com/CCCGL1082/AOI%20Data/Ori_Image/AreaGrabber2/20210903/08/Source/C85T3YE_C2_PM_R_FMura_S2_WithDefect.bmp


        # 有一特例: OGD  先判斷是否為OGD
        elif ct1_summ2_chipid.loc[i]['DEFECT_CODE_DESC'] == 'OTHER GLASS DEFECT' and ct1_summ2_chipid.loc[i]['PATTERN_CODE'][0] == 'M':    
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
        
                
        else:
            # 未在已知範圍   給三個空白
            1    
    return list0

#ｄｐ２ｂｐ專用
def ct1DefectImg_DP2BP(chipid, ct1_x, ct1_y):
    mysql = r""
    mysql += r" select t.tft_chip_id as chipid, t.test_time, t.model_no, t.test_user, t.defect_code_desc,"
    mysql += r" t.test_signal_no as x, test_gate_no as y, t.pattern_code, t.img_file_path, t.img_file_name"
    mysql += r" from celods.h_dax_fbk_defect_ods t"
    mysql += r" where t.tft_chip_id='"+chipid+"'"
    mysql += r" and t.test_OP_ID='CGL'"
    mysql += r" and t.defect_code_desc='DP'"
    mysql += r" and t.test_signal_no="+ct1_x
    mysql += r" and t.test_gate_no="+ct1_y
    
    logging.info(mysql)
    try:
        ct1_summ2_chipid = ora2df(mysql)
        print('ct1簡易找圖資料:')
        print(ct1_summ2_chipid)
    except:
        return '<h1>ora2df 失敗</h1>'
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
        subDefect_list = ['BP', 'DP', 'H-OPEN', 'H-LINE', 'V-OPEN', 'V-LINE', 'X-SHORT', 'BP-PAIR']      
        ag_list = ['V-OPEN-BL', 'AROUND GAP MURA', 'WHITE SPOT', 'BLACK SPOT', 'H-BAND MURA']
        AO7_list = ['CCCGLA072', 'CCCGLA073']
        AO7Def_list = ['OTHER ALIGN DEFECT', 'OTHER GLASS DEFECT', 'OTHER APPEAR DEFECT']
        
        if defect in subDefect_list:
            logging.info('  '+chipid+', Pattern Code = '+str(subDefect_list))
            list0 = subDefect(eqp, chipid, test_date, chipid_times)
        
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
                    img_path = path0 + chipid +'_C'+ ag[-2] + '_P'+ pt + '_FMura_S' + ag[-2] + '_WithDefect.bmp'
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
        
        if defect in subDefect_list:
            logging.info('  '+chipid+', Pattern Code = '+str(subDefect_list))
            list0 = subDefect(eqp, chipid, test_date, chipid_times)
        
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
                    img_path = path0 + chipid +'_C'+ ag[-2] + '_P'+ pt + '_FMura_S' + ag[-2] + '_WithDefect.bmp'
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




def octOLD(user,name, auth, shift, date1, date2, old_shift):
    sectShow = 'octOLD'
    today0 = datetime.date.today().strftime("%Y%m%d")
    today = today0[0:4]+'-'+today0[4:6]+'-'+today0[6:8]
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    date1_dt = datetime.datetime.strptime(date1, "%Y-%m-%d")
    from_date = (date1_dt+datetime.timedelta(-60)).strftime("%Y-%m-%d")
    ok_defects = ['H-OPEN', 'H-LINE', 'OTHER GLASS DEFECT', 'OTHER ALIGN DEFECT', 'X-SHORT','H-BAND MURA']
    logging.info(sectShow+',  '+now)
    
    sql = r""
    sql += r"select t.product_code, sum(decode(t.defect_code_desc,'OTHER LINE DEFECT',1,0)) as OLD, count(distinct t.tft_chip_id)as TOT, "
    #sql += r" "
    sql += r"100*round(sum(decode(t.defect_code_desc,'OTHER LINE DEFECT',1,0))/count(distinct t.tft_chip_id),3) as RATIO, '" + date1 +"' as Start_Day,'" + date2 +"' as End_Day, '"+ old_shift +"' as shift "
    sql += r"from celods.h_dax_fbk_test_ods t "
    sql += r"where t.first_yield_flag='Y' and t.pre_grade='G' and t.tool_id not in ('DMYG2Z') "
    sql += r"and t.mfg_day between to_date('" + date1 +"','yyyy-mm-dd') and to_date('" + date2 +"','yyyy-mm-dd') "
    sql += r"and t.test_user not like '%CC%' "
    #sql += r" and t.defect_code_desc not in ('H-OPEN', 'H-LINE', 'OTHER GLASS DEFECT', 'OTHER ALIGN DEFECT', 'X-SHORT','H-BAND MURA') "
    
    if old_shift == 'D':
        sql += r"and t.shift in ('DA', 'DB') "
    elif old_shift == 'N': 
        sql += r"and t.shift in ('NA', 'NB') "
    sql += r"group by t.product_code "
    sql += r"order by 1,2 "
    logging.info('octOLD_sy sql: '+sql)
    octOLD_sy = ora2df(sql)
    
    sql = r""
    sql += r"select t.product_code, t.tool_id as eqp, sum(decode(t.defect_code_desc,'OTHER LINE DEFECT',1,0)) as OLD, count(distinct t.tft_chip_id)as TOT, "
    sql += r"100*round(sum(decode(t.defect_code_desc,'OTHER LINE DEFECT',1,0))/count(distinct t.tft_chip_id),3) as RATIO, '" + date1 +"' as Start_Day,'" + date2 +"' as End_Day, '"+ old_shift +"' as shift "
    sql += r"from celods.h_dax_fbk_test_ods t "
    sql += r"where t.first_yield_flag='Y' and t.pre_grade='G' and t.tool_id not in ('DMYG2Z', 'CCDMYMFG3', 'CCOCTD00', 'CCOCTE00', 'CCDMYMFG2') " 
    sql += r"and t.mfg_day between to_date('" + date1 +"','yyyy-mm-dd') and to_date('" + date2 +"','yyyy-mm-dd') "
    #sql += r" and t.defect_code_desc not in ('H-OPEN', 'H-LINE', 'OTHER GLASS DEFECT', 'OTHER ALIGN DEFECT', 'X-SHORT','H-BAND MURA') "
    sql += r"and t.test_user not like '%CC%' "
    if old_shift == 'D':
        sql += r"and t.shift in ('DA', 'DB') "
    elif old_shift == 'N': 
        sql += r"and t.shift in ('NA', 'NB') "
    sql += r"group by t.product_code, t.tool_id "
    logging.info('octOLD_sy_raw sql: '+sql)
    octOLD_sy_raw = ora2df(sql)
    
    sql = r""
    sql += r"select t.product_code, sum(decode(t.defect_code_desc,'OTHER LINE DEFECT',1,0)) as OLD, count(distinct t.tft_chip_id)as TOT, "
    sql += r"100*round(sum(decode(t.defect_code_desc,'OTHER LINE DEFECT',1,0))/count(distinct t.tft_chip_id),3) as RATIO, '" + date1 +"' as Start_Day,'" + date2 +"' as End_Day, '"+ old_shift +"' as shift "
    sql += r" from celods.h_dax_fbk_test_ods t "
    sql += r" where t.op_id in ('OCT2','OCT1') "
    sql += r" and t.mfg_day between to_date('" + date1 +"','yyyy-mm-dd') and to_date('" + date2 +"','yyyy-mm-dd') "
    #sql += r" and t.pre_defect_code_desc not in ('H-OPEN', 'H-LINE', 'OTHER GLASS DEFECT', 'OTHER ALIGN DEFECT', 'X-SHORT','H-BAND MURA') "
    sql += r"and t.test_user not like '%CC%' "
    if old_shift == 'D':
        sql += r"and t.shift in ('DA', 'DB') "
    elif old_shift == 'N': 
        sql += r"and t.shift in ('NA', 'NB') "
    sql += r"group by t.product_code "
    sql += r"order by 1,2 "
    
    logging.info('octOLD_fy sql: '+sql)
    octOLD_fy = ora2df(sql)
    
    sql = r""
    sql += r"select t.product_code, t.tool_id as eqp, sum(decode(t.defect_code_desc,'OTHER LINE DEFECT',1,0)) as OLD, count(distinct t.tft_chip_id)as TOT, "
    sql += r"100*round(sum(decode(t.defect_code_desc,'OTHER LINE DEFECT',1,0))/count(distinct t.tft_chip_id),3) as RATIO, '" + date1 +"' as Start_Day,'" + date2 +"' as End_Day, '"+ old_shift +"' as shift "
    sql += r" from celods.h_dax_fbk_test_ods t "
    sql += r" where t.op_id in ('OCT2','OCT1') "
    sql += r" and t.mfg_day between to_date('" + date1 +"','yyyy-mm-dd') and to_date('" + date2 +"','yyyy-mm-dd') "
    #sql += r" and t.pre_defect_code_desc not in ('H-OPEN', 'H-LINE', 'OTHER GLASS DEFECT', 'OTHER ALIGN DEFECT', 'X-SHORT','H-BAND MURA') "
    sql += r"and t.tool_id not in ('DMYG2Z', 'CCDMYMFG3', 'CCOCTD00', 'CCOCTE00', 'CCDMYMFG2') " 
    sql += r"and t.test_user not like '%CC%' "
    if old_shift == 'D':
        sql += r"and t.shift in ('DA', 'DB') "
    elif old_shift == 'N': 
        sql += r"and t.shift in ('NA', 'NB') "
    sql += r"group by t.product_code, t.tool_id "
    
    logging.info('octOLD_fy_raw sql: '+sql)
    octOLD_fy_raw = ora2df(sql)
    
    
    # 搜尋判圖記錄
    
    # 下載判圖記錄
    table = 'oct_check_record'
    df_img_record = mysql2df(table)
    print('mysql2df -> '+table+'   ok!!')
    logging.info('mysql2df -> '+table+'   ok!!')
    dates_list = datesListStr(date1, date2)
    # octOLD_sy_raw的判圖記錄
    #sql += r"where t.first_yield_flag='Y' and t.pre_grade='G'
    for i in range(len(octOLD_sy_raw)):
        octOLD_sy_raw.loc[i, 'OK'] = 0
        octOLD_sy_raw.loc[i, 'NG'] = 0
        octOLD_sy_raw.loc[i, '待確認'] = int(octOLD_sy_raw.loc[i]['OLD'])
        octOLD_sy_raw.loc[i, 'NG_RATIO'] = octOLD_sy_raw.loc[i]['OLD']
        if octOLD_sy_raw.loc[i]['OLD'] == 0:
            octOLD_sy_raw.loc[i, 'NG_RATIO'] = 'N/A  '
            continue
        
        
        eqp = octOLD_sy_raw.loc[i]['EQP']
        pc =  octOLD_sy_raw.loc[i]['PRODUCT_CODE']
        
       
        # 調出他ct1的defect    指定項目皆為ok
        sql = " select a.create_dtm, a.test_time, b.product_code, a.model_no, a.tool_id as oct_eq, a.tft_chip_id as chip_id, a.defect_code_desc as oct_defect, b.test_user as ct1_eq, b.defect_code_desc as ct1_defect, b.test_time as ct1_time"
        sql += r" from"
        sql += r" ("
        sql += r" select t.create_dtm, t.product_code, t.tool_id, t.tft_chip_id, t.defect_code_desc,t.test_time, t.model_no"
        sql += r" from celods.h_dax_fbk_test_ods t "
        sql += r" where t.op_id in ('OCT2','OCT1') "
        sql += r" and t.first_yield_flag='Y' and t.pre_grade='G' "
        sql += r" and t.defect_code_desc in ('OTHER LINE DEFECT') "
        sql += r" and t.tool_id in ('" + eqp + "') "
        sql += r" and t.product_code in ('"+ pc +"') " 
        sql += r" and t.test_user not like '%CC%'"
        if old_shift == 'D':
            sql += r"and t.shift in ('DA', 'DB') "
        elif old_shift == 'N': 
            sql += r"and t.shift in ('NA', 'NB') "
        sql += r" and t.mfg_day between to_date('" + date1 + "','yyyy-mm-dd') and to_date('" + date2 + "','yyyy-mm-dd') "
        #sql += r" and t.pre_defect_code_desc not in ('H-OPEN', 'H-LINE', 'OTHER GLASS DEFECT', 'OTHER ALIGN DEFECT', 'X-SHORT','H-BAND MURA') "
        sql += r" )a"
        sql += r" Left Join"
        sql += r" ("
        sql += r" select t.tft_chip_id, t.product_code, t.test_user, t.defect_code_desc, t.test_time, t.model_no"
        sql += r" from celods.h_dax_fbk_test_ods t"
        sql += r" where t.site_type = 'BEOL'"
        sql += r" and t.site_id = 'L11'"
        sql += r" and t.op_id = 'CGL'"
        sql += r" and t.mfg_day >= to_date('" + from_date + "','yyyy-mm-dd')"
        sql += r" )b"
        sql += r" on a.tft_chip_id = b.tft_chip_id"
        sql += r" and a.product_code = b.product_code"
        logging.info('   sql: '+sql)
        octOLD_raw = ora2df(sql)
        #　去除重複ＩＤ
        #octOLD_raw.drop_duplicates('CHIP_ID', keep='first', inplace=True)
        octOLD_raw.reset_index(inplace=True, drop=True)
        
        for j in range(len(octOLD_raw)):
            
            chipid = octOLD_raw.loc[j]['CHIP_ID']
            model_no = octOLD_raw.loc[j]['MODEL_NO']
            if octOLD_raw.loc[j]['CT1_DEFECT'] in ok_defects:
                
                octOLD_sy_raw.loc[i, 'OK'] = octOLD_sy_raw.loc[i]['OK'] + 1
                octOLD_sy_raw.loc[i, 'NG_RATIO'] = octOLD_sy_raw.loc[i]['NG_RATIO'] - 1
                octOLD_sy_raw.loc[i, '待確認'] = octOLD_sy_raw.loc[i]['待確認'] - 1
                continue
            if octOLD_sy_raw.loc[i]['OK'] == octOLD_sy_raw.loc[i]['OLD']:
                break
            
            for k in range(len(df_img_record)):
                db_date = df_img_record.loc[k]['TEST_TIME_MFG']
                db_octeqp = df_img_record.loc[k]['OCT_EQ']
                db_model_no = df_img_record.loc[k]['MODEL_NO']
                db_chipid = df_img_record.loc[k]['CHIP_ID']
                try:
                    db_pc = db_model_no.split('_', 1)[0]
                except:
                    db_pc = db_model_no
                db_ok = df_img_record.loc[k]['Check']
                db_octdef = df_img_record.loc[k]['OCT_DEFECT']
                oct_def = 'OTHER LINE DEFECT'
                #dates_list = datesListStr(date1, date2)
                
                if db_chipid == chipid and db_octeqp == eqp and db_model_no == model_no and db_octdef == oct_def and db_date in dates_list:
                    if db_ok == 'OK':
                        octOLD_sy_raw.loc[i, 'OK'] = octOLD_sy_raw.loc[i]['OK'] + 1
                        octOLD_sy_raw.loc[i, 'NG_RATIO'] = octOLD_sy_raw.loc[i]['NG_RATIO'] - 1
                        octOLD_sy_raw.loc[i, '待確認'] = octOLD_sy_raw.loc[i]['待確認'] - 1
                        break
                    elif db_ok == 'NG':
                        octOLD_sy_raw.loc[i, 'NG'] = octOLD_sy_raw.loc[i]['NG'] + 1
                        octOLD_sy_raw.loc[i, '待確認'] = octOLD_sy_raw.loc[i]['待確認'] - 1
                        break 
            
        ngratio = 100*round(octOLD_sy_raw.loc[i]['NG_RATIO']/octOLD_sy_raw.loc[i]['TOT'], 3)
        octOLD_sy_raw.loc[i, 'NG_RATIO'] = round(ngratio, 1)
        
        
        
        
        
        
        
        
        
    
        for j in range(len(df_img_record)):
            db_date = df_img_record.loc[j]['TEST_TIME_MFG']
            db_octeqp = df_img_record.loc[j]['OCT_EQ']
            db_model_no = df_img_record.loc[j]['MODEL_NO']
            try:
                db_pc = db_model_no.split('_', 1)[0]
            except:
                db_pc = db_model_no
            db_ok = df_img_record.loc[j]['Check']
            db_octdef = df_img_record.loc[j]['OCT_DEFECT']
            oct_def = 'OTHER LINE DEFECT'
            
            if db_octeqp == eqp and db_pc == pc and db_octdef == oct_def and db_date in dates_list:
                if db_ok == 'OK':
                    octOLD_sy_raw.loc[i, 'OK'] = octOLD_sy_raw.loc[i]['OK'] + 1
                    octOLD_sy_raw.loc[i, 'NG_RATIO'] = octOLD_sy_raw.loc[i]['NG_RATIO'] - 1
                elif db_ok == 'NG':
                    octOLD_sy_raw.loc[i, 'NG'] = octOLD_sy_raw.loc[i]['NG'] + 1
                break
        
        octOLD_sy_raw.loc[i, 'NG_RATIO'] = round(100*octOLD_sy_raw.loc[i]['NG_RATIO']/octOLD_sy_raw.loc[i]['TOT'], 1)
        
    
    # octOLD_fy_raw的判圖記錄
    for i in range(len(octOLD_fy_raw)):
        octOLD_fy_raw.loc[i, 'OK'] = 0
        octOLD_fy_raw.loc[i, 'NG'] = 0
        octOLD_fy_raw.loc[i, '待確認'] = int(octOLD_fy_raw.loc[i]['OLD'])
        octOLD_fy_raw.loc[i, 'NG_RATIO'] = octOLD_fy_raw.loc[i]['OLD']
        if octOLD_fy_raw.loc[i]['OLD'] == 0:
            octOLD_fy_raw.loc[i, 'NG_RATIO'] = 'N/A  '
            continue
        
        eqp = octOLD_fy_raw.loc[i]['EQP']
        pc =  octOLD_fy_raw.loc[i]['PRODUCT_CODE']
        print(eqp, pc)
        
        # 調出他ct1的defect    指定項目皆為ok
        sql = " select a.create_dtm, a.test_time, b.product_code, a.model_no, a.tool_id as oct_eq, a.tft_chip_id as chip_id, a.defect_code_desc as oct_defect, b.test_user as ct1_eq, b.defect_code_desc as ct1_defect, b.test_time as ct1_time"
        sql += r" from"
        sql += r" ("
        sql += r" select t.create_dtm, t.product_code, t.tool_id, t.tft_chip_id, t.defect_code_desc,t.test_time, t.model_no"
        sql += r" from celods.h_dax_fbk_test_ods t "
        sql += r" where t.op_id in ('OCT2','OCT1') "
        sql += r" and t.defect_code_desc in ('OTHER LINE DEFECT') "
        sql += r" and t.tool_id in ('" + eqp + "') "
        sql += r" and t.product_code in ('"+pc+"') " 
        sql += r" and t.test_user not like '%CC%'"
        if old_shift == 'D':
            sql += r"and t.shift in ('DA', 'DB') "
        elif old_shift == 'N': 
            sql += r"and t.shift in ('NA', 'NB') "
        sql += r" and t.mfg_day between to_date('" + date1 + "','yyyy-mm-dd') and to_date('" + date2 + "','yyyy-mm-dd') "
        #sql += r" and t.pre_defect_code_desc not in ('H-OPEN', 'H-LINE', 'OTHER GLASS DEFECT', 'OTHER ALIGN DEFECT', 'X-SHORT','H-BAND MURA') "
        sql += r" )a"
        sql += r" Left Join"
        sql += r" ("
        sql += r" select t.tft_chip_id, t.product_code, t.test_user, t.defect_code_desc, t.test_time, t.model_no"
        sql += r" from celods.h_dax_fbk_test_ods t"
        sql += r" where t.site_type = 'BEOL'"
        sql += r" and t.site_id = 'L11'"
        sql += r" and t.op_id = 'CGL'"
        sql += r" and t.mfg_day >= to_date('" + from_date + "','yyyy-mm-dd')"
        sql += r" )b"
        sql += r" on a.tft_chip_id = b.tft_chip_id"
        sql += r" and a.product_code = b.product_code"
        logging.info('   sql: '+sql)
        octOLD_raw = ora2df(sql)
        #　去除重複ＩＤ
        #octOLD_raw.drop_duplicates('CHIP_ID', keep='first', inplace=True)
        octOLD_raw.reset_index(inplace=True, drop=True)
        
        for j in range(len(octOLD_raw)):
            
            chipid = octOLD_raw.loc[j]['CHIP_ID']
            model_no = octOLD_raw.loc[j]['MODEL_NO']
            test_time0 = str(octOLD_raw.loc[j]['TEST_TIME'])
            if octOLD_raw.loc[j]['CT1_DEFECT'] in ok_defects:
                print('  ct1來料:', chipid)
                octOLD_fy_raw.loc[i, 'OK'] = octOLD_fy_raw.loc[i]['OK'] + 1
                octOLD_fy_raw.loc[i, 'NG_RATIO'] = octOLD_fy_raw.loc[i]['NG_RATIO'] - 1
                octOLD_fy_raw.loc[i, '待確認'] = octOLD_fy_raw.loc[i]['待確認'] - 1
                continue
            if octOLD_fy_raw.loc[i]['OK'] == octOLD_fy_raw.loc[i]['OLD']:
                continue
            
            
            #filter0 = (df_img_record['CHIP_ID'] == chipid) & (df_img_record['OCT_EQ'] == eqp) & (df_img_record['MODEL_NO'] == model_no) & (df_img_record['OCT_DEFECT'] == oct_def) & (df_img_record['TEST_TIME_MFG'].isin(dates_list)) 
            #filter0 = (df_img_record['CHIP_ID'] == chipid) & (df_img_record['OCT_EQ'] == eqp)
            filter0 = (df_img_record['CHIP_ID'] == chipid) & (df_img_record['OCT_EQ'] == eqp) & (df_img_record['TEST_TIME'] == test_time0)
            
            df0 = df_img_record[filter0]
            if len(df0) > 0:
                db_ok = df0.loc[df0.index[-1]]['Check']
                if db_ok == 'OK':
                    octOLD_fy_raw.loc[i, 'OK'] = octOLD_fy_raw.loc[i]['OK'] + 1
                    octOLD_fy_raw.loc[i, 'NG_RATIO'] = octOLD_fy_raw.loc[i]['NG_RATIO'] - 1
                    octOLD_fy_raw.loc[i, '待確認'] = octOLD_fy_raw.loc[i]['待確認'] - 1
                    #break
                elif db_ok == 'NG':
                    octOLD_fy_raw.loc[i, 'NG'] = octOLD_fy_raw.loc[i]['NG'] + 1
                    octOLD_fy_raw.loc[i, '待確認'] = octOLD_fy_raw.loc[i]['待確認'] - 1
                    #break 
            
            """
            for k in range(len(df_img_record)):
                db_date = df_img_record.loc[k]['TEST_TIME_MFG']
                db_octeqp = df_img_record.loc[k]['OCT_EQ']
                db_model_no = df_img_record.loc[k]['MODEL_NO']
                db_chipid = df_img_record.loc[k]['CHIP_ID']
                try:
                    db_pc = db_model_no.split('_', 1)[0]
                except:
                    db_pc = db_model_no
                db_ok = df_img_record.loc[k]['Check']
                db_octdef = df_img_record.loc[k]['OCT_DEFECT']
                oct_def = 'OTHER LINE DEFECT'
                #dates_list = datesListStr(date1, date2)
                
                if db_chipid == chipid and db_model_no == model_no and db_octdef == oct_def and db_date in dates_list:
                    if db_ok == 'OK':
                        print('  ok:', chipid)
                        octOLD_fy_raw.loc[i, 'OK'] = octOLD_fy_raw.loc[i]['OK'] + 1
                        octOLD_fy_raw.loc[i, 'NG_RATIO'] = octOLD_fy_raw.loc[i]['NG_RATIO'] - 1
                        octOLD_fy_raw.loc[i, '待確認'] = octOLD_fy_raw.loc[i]['待確認'] - 1
                        break
                    elif db_ok == 'NG':
                        print('  ng:', chipid)
                        octOLD_fy_raw.loc[i, 'NG'] = octOLD_fy_raw.loc[i]['NG'] + 1
                        octOLD_fy_raw.loc[i, '待確認'] = octOLD_fy_raw.loc[i]['待確認'] - 1
                        break
                """
        ngratio = 100*round(octOLD_fy_raw.loc[i]['NG_RATIO']/octOLD_fy_raw.loc[i]['TOT'], 3)
        octOLD_fy_raw.loc[i, 'NG_RATIO'] = round(ngratio, 1)
        # 避免出現1.0
        #octOLD_fy_raw.loc[i, '未確認'] = round(octOLD_fy_raw.loc[i]['未確認'], 0)
        #octOLD_fy_raw.loc[i, 'NG_RATIO'] = round(100*octOLD_fy_raw.loc[i]['NG_RATIO']/octOLD_fy_raw.loc[i]['TOT'], 1)
        
    #df_img_record
    #mach = [ [0,'CCCGL1082',1], [1,'CCCGL1083',0], [2,'CCCGL2082', 1], [3,'CCCGL2083', 0] ]st.values.tolist(), maint_showIdx=maint_showIdx, mi 
    
    return render_template('userMain.html', user=str(user),name=name, auth=auth, shift=shift, sectShow=sectShow,
                           octOLD_sy=octOLD_sy,octOLD_sy_raw = octOLD_sy_raw, octOLD_fy=octOLD_fy, octOLD_fy_raw=octOLD_fy_raw,
                           date1=date1, date2=date2, old_shift=old_shift)


# 三合一
def octOGDOAD(user,name, auth, shift, date1, date2, sql_shift, oct_def, isCT1data):
    
    ok_defects = []
    
    
    if oct_def == 'OTHER GLASS DEFECT':
        oct_def_abbr = 'OGD'
        ok_defects = ['OTHER ALIGN DEFECT', 'OTHER GLASS DEFECT', 'V-LINE', 'V-OPEN','V-OPEN-BL']
        sectShow = 'octOGD'
    elif oct_def == 'OTHER APPEAR DEFECT':
        oct_def_abbr = 'OAPD'
        ok_defects = ['OTHER ALIGN DEFECT', 'OTHER GLASS DEFECT', 'V-LINE', 'V-OPEN','V-OPEN-BL']
        sectShow = 'octOAPD'
    elif oct_def == 'ABNORMAL DISPLAY':
        oct_def_abbr = 'AD'
        sectShow = 'octAD'    
    else:
        oct_def_abbr = oct_def
    today0 = datetime.date.today().strftime("%Y%m%d")
    today = today0[0:4]+'-'+today0[4:6]+'-'+today0[6:8]
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    date1_dt = datetime.datetime.strptime(date1, "%Y-%m-%d")
    from_date60 = (date1_dt+datetime.timedelta(-60)).strftime("%Y-%m-%d")
    from_date5 = (date1_dt+datetime.timedelta(-5)).strftime("%Y-%m-%d")
    #ok_defects = ['H-OPEN', 'H-LINE', 'OTHER GLASS DEFECT', 'OTHER ALIGN DEFECT', 'X-SHORT','H-BAND MURA']
    
    
    logging.info(sectShow+',  '+now)
    
    sql = r""
    sql += r"select t.product_code, sum(decode(t.defect_code_desc,'" + oct_def + "',1,0)) as " + oct_def_abbr + ", count(distinct t.tft_chip_id)as TOT, "
    #sql += r" "
    sql += r"100*round(sum(decode(t.defect_code_desc,'" + oct_def + "',1,0))/count(distinct t.tft_chip_id),3) as RATIO, '" + date1 +"' as Start_Day,'" + date2 +"' as End_Day, '"+ sql_shift +"' as shift, '"
    sql += oct_def +"' as oct_def, '"+ oct_def_abbr +"' as oct_def_abbr "
    sql += r"from celods.h_dax_fbk_test_ods t "
    sql += r"where t.first_yield_flag='Y' and t.pre_grade='G' and t.tool_id not in ('DMYG2Z', 'CCDMYMFG3', 'CCOCTD00', 'CCOCTE00', 'CCDMYMFG2') " 
    sql += r"and t.mfg_day between to_date('" + date1 +"','yyyy-mm-dd') and to_date('" + date2 +"','yyyy-mm-dd') "
    #sql += r" and t.defect_code_desc not in ('H-OPEN', 'H-LINE', 'OTHER GLASS DEFECT', 'OTHER ALIGN DEFECT', 'X-SHORT','H-BAND MURA') "
    sql += r"and t.test_user not like '%CC%' "
    if sql_shift == 'D':
        sql += r"and t.shift in ('DA', 'DB') "
    elif sql_shift == 'N': 
        sql += r"and t.shift in ('NA', 'NB') "
    sql += r"group by t.product_code "
    sql += r"order by 1,2 "
    logging.info('octOGDOAD_sy sql: '+sql)
    octOGD_sy = ora2df(sql)
    
    
    
    
    sql = r""
    sql += r"select t.product_code, t.tool_id as eqp, sum(decode(t.defect_code_desc,'" + oct_def + "',1,0)) as " + oct_def_abbr + ", count(distinct t.tft_chip_id)as TOT, "
    sql += r"100*round(sum(decode(t.defect_code_desc,'" + oct_def + "',1,0))/count(distinct t.tft_chip_id),3) as RATIO, '" + date1 +"' as Start_Day,'" + date2 +"' as End_Day, '"+ sql_shift +"' as shift, '"
    sql += oct_def +"' as oct_def, '"+ oct_def_abbr +"' as oct_def_abbr "
    sql += r"from celods.h_dax_fbk_test_ods t "
    sql += r"where t.first_yield_flag='Y' and t.pre_grade='G' and t.tool_id not in ('DMYG2Z', 'CCDMYMFG3', 'CCOCTD00', 'CCOCTE00', 'CCDMYMFG2') " 
    sql += r"and t.mfg_day between to_date('" + date1 +"','yyyy-mm-dd') and to_date('" + date2 +"','yyyy-mm-dd') "
    #sql += r" and t.defect_code_desc not in ('H-OPEN', 'H-LINE', 'OTHER GLASS DEFECT', 'OTHER ALIGN DEFECT', 'X-SHORT','H-BAND MURA') "
    sql += r"and t.test_user not like '%CC%' "
    if sql_shift == 'D':
        sql += r"and t.shift in ('DA', 'DB') "
    elif sql_shift == 'N': 
        sql += r"and t.shift in ('NA', 'NB') "
    sql += r"group by t.product_code, t.tool_id "
    logging.info('octOGDOAD_sy_raw sql: '+sql)
    octOGD_sy_raw = ora2df(sql)
    
    
    
    
    
    sql = r""
    sql += r" select a.product_code, "
    sql += r" sum(decode(a.defect_code_desc,'" + oct_def + "',1,0)) as " + oct_def_abbr + ", count(distinct a.tft_chip_id)as TOT, "
    sql += r" 100*round(sum(decode(a.defect_code_desc,'" + oct_def + "',1,0))/count(distinct a.tft_chip_id),3) as RATIO, '" +sql_shift+"' as shift, '"
    sql += oct_def +"' as oct_def, '"+ oct_def_abbr +"' as oct_def_abbr "
    sql += r" from "
    sql += r" ( "
    sql += r" select t.product_code,t.tft_chip_id,t.defect_code_desc,nvl(t.pre_grade,'no_grade') as pre_grade "
    sql += r" from celods.h_dax_fbk_test_ods t "
    sql += r" where t.site_type = 'BEOL' "
    sql += r" and t.op_id in ('OCT2','OCT1') "
    sql += r" and t.mfg_day between to_date('" + date1 +"','yyyy/mm/dd') and to_date('" + date2 +"','yyyy/mm/dd') "
    sql += r"and t.test_user not like '%CC%' "
    if sql_shift == "D" :
        sql += r"and t.shift in ('DA', 'DB') "
    elif sql_shift == "N" :
        sql += r"and t.shift in ('NA', 'NB') "

    sql += r" )a "
    sql += r" group by  a.product_code "
    sql += r" order by a.product_code "
    
    logging.info('octOGDOAD_fy sql: '+sql)
    octOGD_fy = ora2df(sql)
    
    sql = r""
    sql += r" select a.product_code,a.tool_id as eqp , "
    sql += r" sum(decode(a.defect_code_desc,'" + oct_def + "',1,0)) as " + oct_def_abbr + ", count(distinct a.tft_chip_id)as TOT, "
    sql += r" 100*round(sum(decode(a.defect_code_desc,'" + oct_def + "',1,0))/count(distinct a.tft_chip_id),3) as RATIO,'" + date1 +"' as Start_Day,'" + date2 +"' as End_Day, '" +sql_shift+"' as shift, '"
    sql += oct_def +"' as oct_def, '"+ oct_def_abbr +"' as oct_def_abbr "
    sql += r" from "
    sql += r" ( "
    sql += r" select t.product_code,t.tool_id,t.tft_chip_id,t.defect_code_desc,nvl(t.pre_grade,'no_grade') as pre_grade "
    sql += r" from celods.h_dax_fbk_test_ods t "
    sql += r" where t.site_type = 'BEOL' "
    sql += r" and t.op_id in ('OCT2','OCT1') "
    sql += r" and t.tool_id not in ('DMYG2Z', 'CCDMYMFG3', 'CCOCTD00', 'CCOCTE00', 'CCDMYMFG2') " 
    sql += r" and t.mfg_day between to_date('" + date1 +"','yyyy/mm/dd') and to_date('" + date2 +"','yyyy/mm/dd') "
    sql += r"and t.test_user not like '%CC%' "
    if sql_shift == "D" :
        sql += r"and t.shift in ('DA', 'DB') "
    elif sql_shift == "N" :
        sql += r"and t.shift in ('NA', 'NB') "
    sql += r" )a "
    sql += r" group by  a.product_code,a.tool_id "
    sql += r" order by a.product_code,a.tool_id "

    
    logging.info('octOGDOAD_fy_raw sql: '+sql)
    octOGD_fy_raw = ora2df(sql)
    
    
    # 搜尋判圖記錄
    
    # 下載判圖記錄
    table = 'oct_check_record'
    df_img_record = mysql2df(table)
    print('mysql2df -> '+table+'   ok!!')
    logging.info('mysql2df -> '+table+'   ok!!')
    dates_list = datesListStr(date1, date2)
    # octOGD_sy_raw的判圖記錄
    for i in range(len(octOGD_sy_raw)):
        octOGD_sy_raw.loc[i, 'OK'] = 0
        octOGD_sy_raw.loc[i, 'NG'] = 0
        octOGD_sy_raw.loc[i, '待確認'] = int(octOGD_sy_raw.loc[i][oct_def_abbr])
        octOGD_sy_raw.loc[i, 'NG_RATIO'] = octOGD_sy_raw.loc[i][oct_def_abbr]
        if octOGD_sy_raw.loc[i][oct_def_abbr] == 0:
            octOGD_sy_raw.loc[i, 'NG_RATIO'] = 'N/A  '
            continue
        
        eqp = octOGD_sy_raw.loc[i]['EQP']
        pc =  octOGD_sy_raw.loc[i]['PRODUCT_CODE']
        
        #Simple追加條件 sql += r"where t.first_yield_flag='Y' and t.pre_grade='G' "
        # 調出他ct1的defect    指定項目皆為ok
        sql = " select a.create_dtm, a.test_time, b.product_code, a.model_no, a.tool_id as oct_eq, a.tft_chip_id as chip_id, a.defect_code_desc as oct_defect, b.test_user as ct1_eq, b.defect_code_desc as ct1_defect, b.test_time as ct1_time"
        sql += r" from"
        sql += r" ("
        sql += r" select t.create_dtm, t.product_code, t.tool_id, t.tft_chip_id, t.defect_code_desc,t.test_time, t.model_no "
        sql += r" from celods.h_dax_fbk_test_ods t "
        sql += r" where t.op_id in ('OCT2','OCT1') "
        sql += r" and t.defect_code_desc in ('"+ oct_def +"') "
        sql += r" and t.tool_id in ('" + eqp + "') "
        sql += r" and t.product_code in ('"+pc+"') " 
        sql += r" and t.first_yield_flag='Y' and t.pre_grade='G' "
        sql += r" and t.test_user not like '%CC%' "
        if sql_shift == 'D':
            sql += r"and t.shift in ('DA', 'DB') "
        elif sql_shift == 'N': 
            sql += r"and t.shift in ('NA', 'NB') "
        sql += r" and t.mfg_day between to_date('" + date1 + "','yyyy-mm-dd') and to_date('" + date2 + "','yyyy-mm-dd') "
        #sql += r" and t.pre_defect_code_desc not in ('H-OPEN', 'H-LINE', 'OTHER GLASS DEFECT', 'OTHER ALIGN DEFECT', 'X-SHORT','H-BAND MURA') "
        sql += r" )a"
        sql += r" Left Join"
        sql += r" ("
        sql += r" select t.tft_chip_id, t.product_code, t.test_user, t.defect_code_desc, t.test_time, t.model_no"
        sql += r" from celods.h_dax_fbk_test_ods t"
        sql += r" where t.site_type = 'BEOL'"
        sql += r" and t.site_id = 'L11'"
        sql += r" and t.op_id = 'CGL'"
        sql += r" and t.mfg_day >= to_date('" + from_date60 + "','yyyy-mm-dd')"
        sql += r" )b"
        sql += r" on a.tft_chip_id = b.tft_chip_id"
        sql += r" and a.product_code = b.product_code"
        logging.info('   sql: '+sql)
        octOGD_raw = ora2df(sql)
        #　去除重複ＩＤ
        #octOGD_raw.drop_duplicates('CHIP_ID', keep='first', inplace=True)
        octOGD_raw.reset_index(inplace=True, drop=True)
            
        for j in range(len(octOGD_raw)):
            chipid = octOGD_raw.loc[j]['CHIP_ID']
            model_no = octOGD_raw.loc[j]['MODEL_NO']
            
            if octOGD_raw.loc[j]['CT1_DEFECT'] in ok_defects:
                1
                octOGD_sy_raw.loc[i, 'OK'] = octOGD_sy_raw.loc[i]['OK'] + 1
                octOGD_sy_raw.loc[i, 'NG_RATIO'] = octOGD_sy_raw.loc[i]['NG_RATIO'] - 1
                octOGD_sy_raw.loc[i, '待確認'] = octOGD_sy_raw.loc[i]['待確認'] - 1
                continue
            
            
            if octOGD_sy_raw.loc[i]['OK'] == octOGD_sy_raw.loc[i][oct_def_abbr]:
                break
            for k in range(len(df_img_record)):
                db_date = df_img_record.loc[k]['TEST_TIME_MFG']
                db_octeqp = df_img_record.loc[k]['OCT_EQ']
                db_model_no = df_img_record.loc[k]['MODEL_NO']
                db_chipid = df_img_record.loc[k]['CHIP_ID']
                try:
                    db_pc = db_model_no.split('_', 1)[0]
                except:
                    db_pc = db_model_no
                db_ok = df_img_record.loc[k]['Check']
                db_octdef = df_img_record.loc[k]['OCT_DEFECT']
                #oct_def = 'OTHER LINE DEFECT'
                #dates_list = datesListStr(date1, date2)
                if db_chipid == chipid and db_octeqp == eqp and db_model_no == model_no and db_octdef == oct_def and db_date in dates_list:
                    if db_ok == 'OK':
                        octOGD_sy_raw.loc[i, 'OK'] = octOGD_sy_raw.loc[i]['OK'] + 1
                        octOGD_sy_raw.loc[i, 'NG_RATIO'] = octOGD_sy_raw.loc[i]['NG_RATIO'] - 1
                        octOGD_sy_raw.loc[i, '待確認'] = octOGD_sy_raw.loc[i]['待確認'] - 1
                        break
                    elif db_ok == 'NG':
                        octOGD_sy_raw.loc[i, 'NG'] = octOGD_sy_raw.loc[i]['NG'] + 1
                        octOGD_sy_raw.loc[i, '待確認'] = octOGD_sy_raw.loc[i]['待確認'] - 1
                        break 

        ngratio = 100*round(octOGD_sy_raw.loc[i]['NG_RATIO']/octOGD_sy_raw.loc[i]['TOT'], 3)
        octOGD_sy_raw.loc[i, 'NG_RATIO'] = round(ngratio, 1)

    
    # octOGD_fy_raw的判圖記錄
    for i in range(len(octOGD_fy_raw)):
        octOGD_fy_raw.loc[i, 'OK'] = 0
        octOGD_fy_raw.loc[i, 'NG'] = 0
        octOGD_fy_raw.loc[i, '待確認'] = int(octOGD_fy_raw.loc[i][oct_def_abbr])
        octOGD_fy_raw.loc[i, 'NG_RATIO'] = octOGD_fy_raw.loc[i][oct_def_abbr]
        if octOGD_fy_raw.loc[i][oct_def_abbr] == 0:
            octOGD_fy_raw.loc[i, 'NG_RATIO'] = 'N/A'
            
            continue
        
        eqp = octOGD_fy_raw.loc[i]['EQP']
        pc =  octOGD_fy_raw.loc[i]['PRODUCT_CODE']
        
        
        # 調出他ct1的defect    指定項目皆為ok
        sql = " select a.create_dtm, a.test_time, b.product_code, a.model_no, a.tool_id as oct_eq, a.tft_chip_id as chip_id, a.defect_code_desc as oct_defect, b.test_user as ct1_eq, b.defect_code_desc as ct1_defect, b.test_time as ct1_time"
        sql += r" from"
        sql += r" ("
        sql += r" select t.create_dtm, t.product_code, t.tool_id, t.tft_chip_id, t.defect_code_desc,t.test_time, t.model_no "
        sql += r" from celods.h_dax_fbk_test_ods t "
        sql += r" where t.op_id in ('OCT2','OCT1') "
        sql += r" and t.defect_code_desc in ('"+ oct_def +"') "
        sql += r" and t.tool_id in ('" + eqp + "') "
        sql += r" and t.product_code in ('"+pc+"') " 
        sql += r" and t.test_user not like '%CC%' "
        if sql_shift == 'D':
            sql += r"and t.shift in ('DA', 'DB') "
        elif sql_shift == 'N': 
            sql += r"and t.shift in ('NA', 'NB') "
        sql += r" and t.mfg_day between to_date('" + date1 + "','yyyy-mm-dd') and to_date('" + date2 + "','yyyy-mm-dd') "
        #sql += r" and t.pre_defect_code_desc not in ('H-OPEN', 'H-LINE', 'OTHER GLASS DEFECT', 'OTHER ALIGN DEFECT', 'X-SHORT','H-BAND MURA') "
       
        sql += r" )a"
        sql += r" Left Join"
        sql += r" ("
        sql += r" select t.tft_chip_id, t.product_code, t.test_user, t.defect_code_desc, t.test_time, t.model_no"
        sql += r" from celods.h_dax_fbk_test_ods t"
        sql += r" where t.site_type = 'BEOL'"
        sql += r" and t.site_id = 'L11'"
        sql += r" and t.op_id = 'CGL'"
        sql += r" and t.mfg_day >= to_date('" + from_date60 + "','yyyy-mm-dd')"
        sql += r" )b"
        sql += r" on a.tft_chip_id = b.tft_chip_id"
        sql += r" and a.product_code = b.product_code"
        logging.info('   sql: '+sql)
        octOGD_raw = ora2df(sql)
        #　去除重複ＩＤ
        #octOGD_raw.drop_duplicates('CHIP_ID', keep='first', inplace=True)
        octOGD_raw.reset_index(inplace=True, drop=True)
            
        for j in range(len(octOGD_raw)):
            chipid = octOGD_raw.loc[j]['CHIP_ID']
            model_no = octOGD_raw.loc[j]['MODEL_NO']
            test_time0 = str(octOGD_raw.loc[j]['TEST_TIME'])
            if octOGD_raw.loc[j]['CT1_DEFECT'] in ok_defects:
                1
                octOGD_fy_raw.loc[i, 'OK'] = octOGD_fy_raw.loc[i]['OK'] + 1
                octOGD_fy_raw.loc[i, 'NG_RATIO'] = octOGD_fy_raw.loc[i]['NG_RATIO'] - 1
                octOGD_fy_raw.loc[i, '待確認'] = octOGD_fy_raw.loc[i]['待確認'] - 1
                continue
            
            
            if octOGD_fy_raw.loc[i]['OK'] == octOGD_fy_raw.loc[i][oct_def_abbr]:
                continue
            
            #filter0 = (df_img_record['CHIP_ID'] == chipid) & (df_img_record['OCT_EQ'] == eqp) & (df_img_record['MODEL_NO'] == model_no) & (df_img_record['OCT_DEFECT'] == oct_def) & (df_img_record['TEST_TIME_MFG'].isin(dates_list)) 
            #filter0 = (df_img_record['CHIP_ID'] == chipid) & (df_img_record['OCT_EQ'] == eqp)
            filter0 = (df_img_record['CHIP_ID'] == chipid) & (df_img_record['OCT_EQ'] == eqp) & (df_img_record['TEST_TIME'] == test_time0)
            df0 = df_img_record[filter0]
            if len(df0) > 0:
                db_ok = df0.loc[df0.index[-1]]['Check']
                if db_ok == 'OK':
                        octOGD_fy_raw.loc[i, 'OK'] = octOGD_fy_raw.loc[i]['OK'] + 1
                        octOGD_fy_raw.loc[i, 'NG_RATIO'] = octOGD_fy_raw.loc[i]['NG_RATIO'] - 1
                        octOGD_fy_raw.loc[i, '待確認'] = octOGD_fy_raw.loc[i]['待確認'] - 1
                        #break
                elif db_ok == 'NG':
                    octOGD_fy_raw.loc[i, 'NG'] = octOGD_fy_raw.loc[i]['NG'] + 1
                    octOGD_fy_raw.loc[i, '待確認'] = octOGD_fy_raw.loc[i]['待確認'] - 1
                    #break 
            """
            for k in range(len(df_img_record)):
                db_date = df_img_record.loc[k]['TEST_TIME_MFG']
                db_octeqp = df_img_record.loc[k]['OCT_EQ']
                db_model_no = df_img_record.loc[k]['MODEL_NO']
                db_chipid = df_img_record.loc[k]['CHIP_ID']
                try:
                    db_pc = db_model_no.split('_', 1)[0]
                except:
                    db_pc = db_model_no
                db_ok = df_img_record.loc[k]['Check']
                db_octdef = df_img_record.loc[k]['OCT_DEFECT']
                #oct_def = 'OTHER LINE DEFECT'
                #dates_list = datesListStr(date1, date2)
                if db_chipid == chipid and db_octeqp == eqp and db_model_no == model_no and db_octdef == oct_def and db_date in dates_list:
                    if db_ok == 'OK':
                        octOGD_fy_raw.loc[i, 'OK'] = octOGD_fy_raw.loc[i]['OK'] + 1
                        octOGD_fy_raw.loc[i, 'NG_RATIO'] = octOGD_fy_raw.loc[i]['NG_RATIO'] - 1
                        octOGD_fy_raw.loc[i, '待確認'] = octOGD_fy_raw.loc[i]['待確認'] - 1
                        break
                    elif db_ok == 'NG':
                        octOGD_fy_raw.loc[i, 'NG'] = octOGD_fy_raw.loc[i]['NG'] + 1
                        octOGD_fy_raw.loc[i, '待確認'] = octOGD_fy_raw.loc[i]['待確認'] - 1
                        break 
            """
        ngratio = 100*round(octOGD_fy_raw.loc[i]['NG_RATIO']/octOGD_fy_raw.loc[i]['TOT'], 3)
        octOGD_fy_raw.loc[i, 'NG_RATIO'] = round(ngratio, 1)
    #df_img_record
    #mach = [ [0,'CCCGL1082',1], [1,'CCCGL1083',0], [2,'CCCGL2082', 1], [3,'CCCGL2083', 0] ]st.values.tolist(), maint_showIdx=maint_showIdx, mi 
    
    #與ｃｔ１的比對資料
    if isCT1data:
        # ct1對應機台與片數
        sql = r""
        sql += r" select a.ct1_eq, a.oct_eq "
        sql += r" ,sum(decode(a.oct_defect,'"+ oct_def +"',1,0)) as "+ oct_def_abbr +"_pcs, count(*) as total "
        sql += r" ,round(100*sum(decode(a.oct_defect,'"+ oct_def +"',1,0))/count(*),1) as Ratio "
        sql += r" from "
        sql += r" ( "
        sql += r" select a.tft_chip_id, a.product_code, a.tool_id as oct_eq, a.defect_code_desc as oct_defect, b.tool_id as ct1_eq, b.defect_code_desc as ct1_defect "
        sql += r" from "
        sql += r" ( "
        sql += r" select t.tft_chip_id, t.product_code,t.tool_id, t.defect_code_desc "
        sql += r" from celods.h_dax_fbk_test_ods t "
        sql += r" where t.site_type = 'BEOL' "
        sql += r" and t.site_id = 'L11' "
        sql += r" and t.op_id  in ('OCT2','OCT1') "
        if oct_def_abbr == 'OGD':
            sql += r" and t.first_yield_flag = 'Y' "
        sql += r" and t.tool_id <> 'DMYG2Z' "
        if sql_shift == "D" :
            sql += r"and t.shift in ('DA', 'DB') "
        elif sql_shift == "N" :
            sql += r"and t.shift in ('NA', 'NB') "
        sql += r" and t.mfg_day between to_date('" + date1 +"','yyyy/mm/dd') and to_date('" + date2 +"','yyyy/mm/dd') "
        sql += r" )a "
        sql += r" Left Join "
        sql += r" ( "
        sql += r" select t.tft_chip_id, t.product_code, t.tool_id,t.defect_code_desc "
        sql += r" from celods.h_dax_fbk_test_ods t "
        sql += r" where t.site_type = 'BEOL' "
        sql += r" and t.site_id = 'L11' "
        sql += r" and t.op_id = 'CGL' "
        sql += r" and t.mfg_day >= to_date('" + from_date5 + "','yyyy/mm/dd') "
        sql += r" )b "
        sql += r" on a.tft_chip_id = b.tft_chip_id "
        sql += r" and a.product_code = b.product_code "
        sql += r" )a"
        sql += r" group by a.ct1_eq, a.oct_eq order by 1,2 "
        logging.info('octOGD_ct1eqp sql: '+sql)
        octOGD_ct1eqp = ora2df(sql)
        
        first_idx = -1
        first_eqp = ''
        rowspan = 1
        for i in range(len(octOGD_ct1eqp)):
            octOGD_ct1eqp.loc[i, 'rowspan'] = 1
            ct1eqp = octOGD_ct1eqp.loc[i]['CT1_EQ']
            if ct1eqp != first_eqp:
                if first_idx >= 0:
                    octOGD_ct1eqp.loc[first_idx, 'rowspan'] = rowspan
            
                first_eqp = ct1eqp
                first_idx = i
                rowspan = 1
         
            else:
                rowspan += 1
                continue
 
        # ct1對應defect        
        sql = r""
        sql += r" select a.ct1_eq, a.oct_eq, a.ct1_defect, count(*) as PCS "
        sql += r" from "
        sql += r" ( "
        sql += r" select a.tft_chip_id, a.product_code, a.tool_id as oct_eq, a.defect_code_desc as oct_defect, b.tool_id as ct1_eq, b.defect_code_desc as ct1_defect "
        sql += r" from "
        sql += r" ( "
        sql += r" select t.tft_chip_id, t.product_code,t.tool_id, t.defect_code_desc "
        sql += r" from celods.h_dax_fbk_test_ods t "
        sql += r" where t.site_type = 'BEOL' "
        sql += r" and t.site_id = 'L11' "
        sql += r" and t.op_id  in ('OCT2','OCT1') "
        if oct_def_abbr == 'OGD':
            sql += r" and t.first_yield_flag = 'Y' "
        sql += r" and t.tool_id <> 'DMYG2Z' "
        if sql_shift == "D" :
            sql += r"and t.shift in ('DA', 'DB') "
        elif sql_shift == "N" :
            sql += r"and t.shift in ('NA', 'NB') "
        sql += r" and t.mfg_day between to_date('" + date1 +"','yyyy/mm/dd') and to_date('" + date2 +"','yyyy/mm/dd') "
        sql += r" )a "
        sql += r" Left Join "
        sql += r" ( "
        sql += r" select t.tft_chip_id, t.product_code, t.tool_id,t.defect_code_desc "
        sql += r" from celods.h_dax_fbk_test_ods t "
        sql += r" where t.site_type = 'BEOL' "
        sql += r" and t.site_id = 'L11' "
        sql += r" and t.op_id = 'CGL' "
        sql += r" and t.mfg_day >= to_date('" + from_date5 + "','yyyy/mm/dd') "
        sql += r" )b "
        sql += r" on a.tft_chip_id = b.tft_chip_id "
        sql += r" and a.product_code = b.product_code "
        sql += r" )a "
        sql += r" where a.ct1_defect in ('OTHER ALIGN DEFECT','OTHER APPEAR DEFECT','OTHER GLASS DEFECT') "
        sql += r" group by a.ct1_eq,a.ct1_defect, a.oct_eq  order by 1,2 "

        logging.info('octOGD_ct1def sql: '+sql)
        octOGD_ct1def = ora2df(sql)
        
        
        first_idx = -1
        first_eqp = ''
        rowspan = 1
        for i in range(len(octOGD_ct1def)):
            octOGD_ct1def.loc[i, 'rowspan'] = 1
            ct1eqp = octOGD_ct1def.loc[i]['CT1_EQ']
            if ct1eqp != first_eqp:
                if first_idx >= 0:
                    octOGD_ct1def.loc[first_idx, 'rowspan'] = rowspan
            
                first_eqp = ct1eqp
                first_idx = i
                rowspan = 1
         
            else:
                rowspan += 1
                continue
        
        return render_template('userMain.html', user=str(user),name=name, auth=auth, shift=shift, sectShow=sectShow,
               octOGD_sy=octOGD_sy,octOGD_sy_raw = octOGD_sy_raw, octOGD_fy=octOGD_fy, octOGD_fy_raw=octOGD_fy_raw,
               octOGD_ct1def=octOGD_ct1def, octOGD_ct1eqp=octOGD_ct1eqp, date1=date1, date2=date2, sql_shift=sql_shift, isCT1data=isCT1data)
        
    else:
        return render_template('userMain.html', user=str(user),name=name, auth=auth, shift=shift, sectShow=sectShow,
               octOGD_sy=octOGD_sy,octOGD_sy_raw = octOGD_sy_raw, octOGD_fy=octOGD_fy, octOGD_fy_raw=octOGD_fy_raw,
               date1=date1, date2=date2, sql_shift=sql_shift, isCT1data=isCT1data)




    
    












def octOLDRaw(user,name, auth, shift, date1, date2, old_shift, eqp, pc, oct_def,isSY):
    
    date1_dt = datetime.datetime.strptime(date1, "%Y-%m-%d")
    from_date = (date1_dt+datetime.timedelta(-60)).strftime("%Y-%m-%d")
    sectShow = 'octOLDRaw'
    #直接ｏｋ的ｄｅｆｅｃｔ　
    ok_defects = []
    if oct_def == 'OTHER GLASS DEFECT':
        ok_defects = ['OTHER ALIGN DEFECT', 'OTHER GLASS DEFECT', 'V-LINE', 'V-OPEN','V-OPEN-BL']
    elif oct_def == 'OTHER APPEAR DEFECT':
        ok_defects = ['OTHER ALIGN DEFECT', 'OTHER GLASS DEFECT', 'V-LINE', 'V-OPEN','V-OPEN-BL']
    elif oct_def == 'OTHER LINE DEFECT':
        ok_defects = ['H-OPEN', 'H-LINE', 'OTHER GLASS DEFECT', 'OTHER ALIGN DEFECT', 'X-SHORT','H-BAND MURA']
    # Simple 追加條件"where t.first_yield_flag='Y' and t.pre_grade='G' "
    sql = " select a.test_time, a.model_no, a.tool_id as oct_eq, a.tft_chip_id as chip_id, a.test_user, a.defect_code_desc as oct_defect, b.test_user as ct1_eq, b.defect_code_desc as ct1_defect, b.test_time as ct1_time"
    sql += r" from"
    sql += r" ("
    sql += r" select t.create_dtm, t.product_code, t.tool_id, t.tft_chip_id, t.defect_code_desc,t.test_time, t.model_no, t.test_user "
    sql += r" from celods.h_dax_fbk_test_ods t "
    sql += r" where t.op_id in ('OCT2','OCT1') "
    sql += r" and t.defect_code_desc in ('"+oct_def+"') "
    if oct_def not in ["PAD CORROSION"]:
        sql += r" and t.product_code in ('"+pc+"') "        
    sql += r" and t.tool_id in ('" + eqp + "') "
    sql += r" and t.test_user not like '%CC%'"
    if oct_def == "OTHER LINE DEFECT":
        1
        #sql += r" and t.pre_defect_code_desc not in ('H-OPEN', 'H-LINE', 'OTHER GLASS DEFECT', 'OTHER ALIGN DEFECT', 'X-SHORT','H-BAND MURA') "
    if old_shift == 'D':
        sql += r"and t.shift in ('DA', 'DB') "
    elif old_shift == 'N': 
        sql += r"and t.shift in ('NA', 'NB') "
    if isSY:
        sql += r" and t.first_yield_flag='Y' and t.pre_grade='G' "
    sql += r" and t.mfg_day between to_date('" + date1 + "','yyyy-mm-dd') and to_date('" + date2 + "','yyyy-mm-dd') "
    sql += r" order by t.tft_chip_id"
    sql += r" )a"
    sql += r" Left Join"
    sql += r" ("
    sql += r" select t.tft_chip_id, t.product_code, t.test_user, t.defect_code_desc, t.test_time, t.model_no"
    sql += r" from celods.h_dax_fbk_test_ods t"
    sql += r" where t.site_type = 'BEOL'"
    sql += r" and t.site_id = 'L11'"
    sql += r" and t.op_id = 'CGL'"
    sql += r" and t.mfg_day >= to_date('" + from_date + "','yyyy-mm-dd')"
    sql += r" )b"
    sql += r" on a.tft_chip_id = b.tft_chip_id"
    sql += r" and a.product_code = b.product_code"
    logging.info('   sql: '+sql)
    octOLD_raw = ora2df(sql)
    
    #　去除重複ＩＤ
    #octOLD_raw.drop_duplicates('CHIP_ID', keep='first', inplace=True)
    octOLD_raw.reset_index(inplace=True, drop=True)
    """
    drop_idxs = []
    for i in range(len(octOLD_raw)-1):
        chipid = octOLD_raw.loc[i]['CHIP_ID']
        next_id = octOLD_raw.loc[i+1]['CHIP_ID']
        if chipid == next_id:
            drop_idxs.append(i+1)
    
    if len(drop_idxs) != 0:
        octOLD_raw = octOLD_raw.drop(drop_idxs)
    """
    
    """
    #ｃｔ１影像
    sql = r""
    sql += r"select  r.tft_chip_id,r.defect_code_desc,r.model_no,r.test_time,r.test_user,r.pattern_code,r.img_file_path, r.img_file_name, r.update_dtm, r.grade "
    sql += r"from celods.h_dax_fbk_defect_ods r "
    sql += r"where r.test_mfg_day between to_date('" + date1 + "','yyyy/mm/dd') and to_date(" + date1 + ",'yyyy/mm/dd')
    sql += r"and r.test_OP_id = 'OCT2' "
    sql += r"and r.grade <> ('G') "
    sql += r"and r.tft_chip_id = '"+ chipid +"' "
    sql += r"and r.product_code= "+ model_no +"' "
    sql += r"and r.defect_code_desc= "+ defect +"' "
    sql += r"order by r.tft_chip_id, r.update_dtm
    """
    
    
    #OCT　ｏｌｄ影像位置：
    # http://tcweb002.corpnet.auo.com/CCCGL3082/AOI%20Data/Defect_Image/Sub2/20211011/16/OtherGlass/C9D44KH_C2_PWHITE.tif
    octaoi_list = []
    octadc_list = []
    ct1img_list = []
    ct1_subImgsList = []
    ct1_areaImgsList = []
    ct1_othersImgsList = []
    
    # 避免沒資料時錯誤
    if len(octOLD_raw) == 0:
        octaoi_imgs = []
        octadc_imgs = []
        ct1_imgs = []
        
    # 下載判圖記錄
    table = 'oct_check_record'
    df_img_record = mysql2df(table)
    print('mysql2df -> '+table+'   ok!!')
    logging.info('mysql2df -> '+table+'   ok!!')
    for i in range(len(octOLD_raw)):
        chipid = octOLD_raw.loc[i]['CHIP_ID']
        oct_user = octOLD_raw.loc[i]['OCT_EQ']
        
        # 加入box_id資訊
        sql = r"select T.SHEET_ID_CHIP_ID,t.cassette_id as boxid "
        sql += r" from celods.r_chip_wip_ods t"
        sql += r" WHERE T.SHEET_ID_CHIP_ID='" + chipid + "'"
        df_boxid = ora2df(sql)
        df_boxid.fillna('   ', inplace=True)
        if len(df_boxid) >= 1:
            box_id = df_boxid.loc[len(df_boxid)-1]['BOXID']
            if box_id == '   ':
                box_id = oct_user+'中'
        else:
            box_id = 'No sql record'
            
        octOLD_raw.loc[i, 'BOX_ID'] = box_id
        
        
        
        
        time_ct1_str = str(octOLD_raw.loc[i]['CT1_TIME'])
        date_ct1 = time_ct1_str[0:4]+time_ct1_str[5:7]+time_ct1_str[8:10]
        hour_ct1 = time_ct1_str[11:13]
        mm_ct1 = time_ct1_str[14:16]
        print('ct1時間:'+hour_ct1, mm_ct1)
        time_oct_str = str(octOLD_raw.loc[i]['TEST_TIME'])
        date_oct = time_oct_str[0:4]+time_oct_str[5:7]+time_oct_str[8:10]
        hour_oct = time_oct_str[11:13]
        eqp_ct1 = octOLD_raw.loc[i]['CT1_EQ']
        eqp_oct = octOLD_raw.loc[i]['OCT_EQ']
        defect_ct1 = octOLD_raw.loc[i]['CT1_DEFECT']
        defect_oct = octOLD_raw.loc[i]['OCT_DEFECT']
        model_no = octOLD_raw.loc[i]['MODEL_NO']
        test_time0 = str(octOLD_raw.loc[i]['TEST_TIME'])
        # oct的AOI & ADC影像以list依序儲存
        octaoi_imgs = []
        octadc_imgs = []
        ct1_imgs = []
        suffix = ['.bmp', '.BMP']
                
        
        octOLD_raw.loc[i, 'OCT_IMAGE_AOI'] = '   '
        octOLD_raw.loc[i, 'OCT_IMAGE_ADC'] = '   '
        octOLD_raw.loc[i, 'CT1_IMAGE'] = '   '
        octOLD_raw.loc[i, 'Check'] = 'NN'
        octOLD_raw.loc[i, 'Reason'] = '   '
        octOLD_raw.loc[i, 'Explain'] = '   '
        #octOLD_raw.loc[i, 'BOX/CST ID'] = '   '
        
        isOKDef = False
        if defect_ct1 in ok_defects:
            octOLD_raw.loc[i, 'Check'] = 'OK'
            octOLD_raw.loc[i, 'Reason'] = 'CT1來料相關呈像'
            isOKDef = True
        
        
        
        #filter0 = (df_img_record['CHIP_ID'] == chipid) & (df_img_record['OCT_EQ'] == eqp)
        filter0 = (df_img_record['CHIP_ID'] == chipid) & (df_img_record['OCT_EQ'] == eqp_oct) & (df_img_record['TEST_TIME'] == test_time0)
            
        #filter0 = (df_img_record['CHIP_ID'] == chipid) & (df_img_record['OCT_EQ'] == eqp) & (df_img_record['TEST_TIME'] == test_time0)
               
        df0 = df_img_record[filter0]
        if len(df0) > 0:
            last_n = df0.index[-1]
            octOLD_raw.loc[i, 'Check'] = df0.loc[last_n]['Check']
            octOLD_raw.loc[i, 'Reason'] = df0.loc[last_n]['Reason']
            octOLD_raw.loc[i, 'Explain'] = df0.loc[last_n]['name']+', '+df0.loc[last_n]['Explain']
            #print(octOLD_raw.loc[i]['Explain'] )
        """
        for j in range(len(df_img_record)):
            db_chipid = df_img_record.loc[j]['CHIP_ID']
            db_testtime = str(df_img_record.loc[j]['TEST_TIME'])
            db_octeqp = df_img_record.loc[j]['OCT_EQ']
            db_model_no = df_img_record.loc[j]['MODEL_NO']
            
            db_ok = df_img_record.loc[j]['Check']
            db_octdef = df_img_record.loc[j]['OCT_DEFECT']
            oct_def = 'OTHER LINE DEFECT'
            #OLD第一頁的判斷邏輯
            # if db_octeqp == eqp and db_pc == pc and db_octdef == oct_def and db_date in dates_list:
            #db_ct1def = df_img_record.loc[j]['CT1_DEFFECT']
            if chipid == db_chipid and model_no == db_model_no and eqp_oct == db_octeqp and defect_oct == db_octdef and time_oct_str == db_testtime:
                octOLD_raw.loc[i, 'Check'] = df_img_record.loc[j]['Check']
                octOLD_raw.loc[i, 'Reason'] = df_img_record.loc[j]['Reason']
                octOLD_raw.loc[i, 'Explain'] = df_img_record.loc[j]['name']+', '+df_img_record.loc[j]['Explain']
        """
        
        """    
        CCOCT303    OCT300    ADC    http://10.97.212.30/AOI_Data_ADC/GrabImage/IP1/                                
                              AOI    http://10.97.212.30/AOI_Data_D/GrabImage/Defect/IP1/                                
        CCOCT403    OCT400    ADC    http://10.97.212.99/AOI_Data_ADC/GrabImage/IP1/                                
                    OCT400    AOI    http://10.97.212.99/AOI_Data_D/GrabImage/Defect/IP1/                                
        CCCTS303    CTS300    ADC    http://10.97.213.216/AOI_Data_ADC/GrabImage/IP1/                                
                              AOI    http://10.97.213.216/AOI_Data_D/GrabImage/Defect/IP1/ 
                              改AOI  http://10.97.213.216/AOI_Data_D/GrabImage/Source/IP1/20211118/CBDW5BH/FunctionError/CBDW5BH_C1_1_PF_RD_[Line_Too_Much].tif

        CCCTSA04    CTSA00    ADC    http://10.97.213.56/D/AOI_Data_ADC/GrabImage/IP1/                                
                              AOI    http://10.97.213.56/D/AOI_Data_D/GrabImage/Defect/IP1/                                
                              AOI    http://10.97.213.56/E/AOI_Data_E/GrabImage/Defect/IP2/                                
                              AOI    http://10.97.213.56/F/AOI_Data_F/GrabImage/Defect/IP3/                                
                              AOI    http://10.97.213.56/G/AOI_Data_G/GrabImage/Defect/IP4/                                
                                            
        CCCTS503    CTS500    ADC    http://10.97.213.138/AOI_Data_ADC/GrabImage/IP1/                                
        CCCTS603    CTS600    ADC    http://10.97.213.39/AOI_Data_ADC/GrabImage/IP1/                                
        CCCTS903    CTS900    ADC    http://10.97.212.210/AOI_Data_ADC/GrabImage/IP1/                                
        CCOCTA03    OCTA00    ADC    http://10.97.213.49/AOI_Data_ADC/GrabImage/IP1/                                
        CCOCTC03    OCTB00    ADC    http://10.97.213.190/AOI_Data_ADC/GrabImage/IP1/                                
        CCOCTC03    OCTC00    ADC    http://10.97.213.193/AOI_Data_ADC/GrabImage/IP1/                                

        """    
        # http://10.97.212.30/AOI_Data_D/GrabImage/Defect/IP1/20211014/C9CU9HF/Mura/
        # http://10.97.212.30/AOI_Data_D/GrabImage/Defect/IP1/20211014/CADK4GA/Func/CADK4GA_C1_1_PF_L0_TBP_X6101_Y2412_D4758_G105.bmp
        
        # 確認是否為有圖但找不到
        isAOI = True
        isADC = True
        isCT1 = True
        isCT1D = False
        if oct_def in ['OTHER LINE DEFECT']:
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
            #CCD1---http://10.97.213.56/D/AOI_Data_D/GrabImage/Defect/IP1/
            #CCD2---http://10.97.213.56/E/AOI_Data_E/GrabImage/Defect/IP1/
            #CCD3---http://10.97.213.56/F/AOI_Data_F/GrabImage/Defect/IP1/
            #CCD4---http://10.97.213.56/G/AOI_Data_G/GrabImage/Defect/IP1/"

            
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
                        octaoi_imgs.append(path_aoimuras[num] +'/'+imgs_path[1][img_idx])
            
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
        octaoi_list.append(octaoi_imgs)
        octadc_list.append(octadc_imgs)
        # ct1找圖
        # CAJN5SH_C1_PM_LM_FMura_S1_0.bmp
        # 有可能無時間 為None
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
                continue
        ct1_subImgs = []
        ct1_areaImgs = []
        ct1_othersImgs = []
        if isCT1D:
            if int(hour_ct1) <= 6  or (int(hour_ct1) == 7 and int(mm_ct1) < 30):
                date0 = date_ct1[0:4]+'-'+date_ct1[4:6]+'-'+date_ct1[6:8]
                date0_dt = datetime.datetime.strptime(date0, "%Y-%m-%d")
                mfgday_ct1 = (date0_dt+datetime.timedelta(-1)).strftime("%Y-%m-%d")
            else:
                mfgday_ct1 = date_ct1[0:4]+'-'+date_ct1[4:6]+'-'+date_ct1[6:8]
                
            #ct1_imgs = findct1Img(mfgday_ct1, mfgday_ct1, eqp_ct1, model_no, defect_ct1, chipid)
            imgs = ct1DefectImg(mfgday_ct1, mfgday_ct1, model_no, defect_ct1, eqp_ct1, chipid)
            ct1_subImgs = []
            ct1_areaImgs = []
            ct1_othersImgs = []
            for img in imgs:
                key_word1 = img[66:69]
                key_word2 = img[63:66]
                
                if key_word1 == 'Sub' or key_word2 == 'Sub':
                    ct1_subImgs.append(img)
                elif key_word1 == 'Are' or key_word2 == 'Are':
                    ct1_areaImgs.append(img)
                else:
                    ct1_othersImgs.append(img)
            
            print('ok')
        else:
            #ct1img_list.append(ct1_imgs)
            continue
        
        
        ct1_subImgsList.append(ct1_subImgs)
        ct1_areaImgsList.append(ct1_areaImgs)
        ct1_othersImgsList.append(ct1_othersImgs)
    
    print('ct1img_list >>>>>>>>>>>> ')
    #print(ct1img_list)
    
    
    
    return render_template('userMain.html', user=str(user),name=name, auth=auth, shift=shift, sectShow=sectShow,
                           octOLD_raw= octOLD_raw, octaoi_list=octaoi_list, octadc_list=octadc_list, 
                           ct1img_list=ct1img_list,
                           ct1_subImgsList=ct1_subImgsList, ct1_areaImgsList=ct1_areaImgsList, ct1_othersImgsList=ct1_othersImgsList)


def octCheckUpload(user,name, auth, shift, req_list):
    #df_img_record = pd.DataFrame()
    table = 'oct_check_record'
    db_data = mysql2df(table)
    df_img_record = pd.DataFrame(columns=db_data.columns)
    cols = df_img_record.columns
    newIdx = len(df_img_record)
    sectShow = 'uploadOK'
    now_hm = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    for item in req_list:
        req = request.form.get(item)
        name_idx = newIdx
        # 第四項前的是身分資訊   無編號會進到EXCEPT
        try:
            aaa = item.split('__',2)
            col = aaa[0]
            num = int(aaa[1])
            if col in df_img_record.columns:
                df_img_record.loc[newIdx+num, col] = req
        except:
            continue
        
        #　imgCheck'為每一個Ｉｄ的最後一項
        if col == 'Check':
            name_idx += 1
    # 個別補上個人資訊
    user_list = ['user', 'name', 'shift', 'auth']
    
    drops = []
    for m in range(num+1):
        for ii in user_list:
            req = request.form.get(ii)
            df_img_record.loc[newIdx+m, ii] = req
        if 'Checked_Date' in df_img_record.columns:
            df_img_record.loc[newIdx+m, 'Checked_Date'] = now_hm
        imgCheck = df_img_record.loc[newIdx+m]['Check']
        if imgCheck is None or pd.isna(imgCheck):
            drops.append(newIdx+m)
        # 新增MFG DATE轉換資訊
        if 'TEST_TIME' in df_img_record.columns:
            test_time = df_img_record.loc[newIdx+m]['TEST_TIME']
            df_img_record.loc[newIdx+m,'TEST_TIME_MFG'] = testTime2MFG(str(test_time))
        if imgCheck is None or pd.isna(imgCheck):
            drops.append(newIdx+m)
    
    df_img_record = df_img_record.drop(drops)
    df_img_record.reset_index(drop=True, inplace=True)
    #print(df_img_record)
    df2mysql_append(df_img_record, table)
    
    #sectShow = 'ct1Summ'
    sql_shift = 'ALL'
    date1 = now_hm[:10]
    date2 = date1
    oct_def = df_img_record.loc[len(df_img_record)-1]['OCT_DEFECT'] 
    if oct_def == 'OTHER LINE DEFECT':
        return octOLD(user,name, auth, shift, date1, date2, sql_shift)
    else:
        isCT1data = False
        return octOGDOAD(user,name, auth, shift, date1, date2, sql_shift, oct_def, isCT1data)
    
    
    #return render_template('userMain.html', user=str(user),name=name, auth=auth, shift=shift, sectShow=sectShow)

    



# OCT PAD CORROSION Monitor
def octPADCOR(user,name, auth, shift, date1, date2):
    sectShow = 'octPADCOR'
    sql = r""
    sql += r"select a.tool_id as eqp,sum(a.PAD_CORROSION) as PAD_COUNT,sum(a.TOT) as TOT,round(sum(a.PAD_CORROSION)/sum(a.TOT),4) as RATIO,'"+ date1 +"' as Start_Day,'"+ date2 +"' as End_Day "
    sql += r"from ( "
    sql += r"select t.tool_id ,nvl(t.pre_grade,'W') as pre_grade , count(distinct t.tft_chip_id)as TOT, " 
    sql += r"sum(decode(t.defect_code_desc,'PAD CORROSION',1,0)) as PAD_CORROSION " 
    sql += r"from celods.h_dax_fbk_test_ods t " 
    sql += r"where t.op_id in ('OCT2','OCT1') " 
    sql += r"and t.tool_id not in ('DMYG2Z', 'CCDMYMFG3', 'CCOCTD00', 'CCOCTE00', 'CCDMYMFG2') " 
    sql += r"and t.mfg_day between to_date('"+ date1 +"','yyyy/mm/dd') and to_date('"+ date2 +"','yyyy/mm/dd') " 
    sql += r"and t.test_user not like '%CC%' "
    sql += r"group by  t.tool_id ,t.pre_grade "
    sql += r"order by t.product_code,t.tool_id " 
    sql += r")a "
    sql += r"group by a.tool_id "
    
    logging.info('octPADCOR sql: '+sql)
    octPADCOR1 = ora2df(sql)
    
    sql = r""
    sql += r"select t.op_id, t.product_code, t.tft_chip_id, t.tool_id, t.defect_code_desc, t.grade "
    sql += r"from celods.h_dax_fbk_test_ods t "
    sql += r"where t.mfg_day between to_date('"+ date1 +"','yyyy/mm/dd') and to_date('"+ date2 +"','yyyy/mm/dd') " 
    sql += r"and t.op_id in ('OCT2','OCT1') " 
    sql += r"and t.tool_id <> 'DMYG2Z' "
    sql += r"and defect_code_desc = 'PAD CORROSION' "
    sql += r"and t.test_user not like '%CC%' "
    logging.info('octPADCOR2 sql: '+sql)
    octPADCOR2 = ora2df(sql)
    
    return render_template('userMain.html', user=str(user),name=name, auth=auth, shift=shift, sectShow=sectShow,
                           date1=date1, date2=date2,octPADCOR1= octPADCOR1, octPADCOR2=octPADCOR2)
    
def octDP2BP(user,name, auth, shift, date1, date2):
    sectShow = 'octDP2BP'
    sql = " select b.tool_id,b.product_code,a.RB,b.total "
    sql += " from "
    sql += " ("
    sql += " select a.test_tool_id,a.product_code,count(distinct a.tft_chip_id) as RB "
    sql += " from "
    sql += " ("
    sql += " select a.test_time,a.test_tool_id,a.product_code,a.tft_chip_id,a.OCT_defect,a.OCT_X,a.OCT_Y,a.CT1_defect,a.CT1_X,a.CT1_Y,a.X_error,a.Y_error,"
    sql += " Case "
    sql += " when X_error <= 10 and Y_error <= 10 then 1 End as N"
    sql += " from "
    
    sql += " ("
    sql += " select b.test_time,b.test_tool_id,b.product_code,b.tft_chip_id,b.defect_code_desc as OCT_defect,b.test_signal_no as OCT_X,b.test_gate_no as OCT_Y,a.defect_code_desc as CT1_defect,a.test_signal_no as CT1_X,a.test_gate_no as CT1_Y,abs(a.test_signal_no-b.test_signal_no) as X_error,abs(a.test_gate_no-b.test_gate_no) as Y_error"
    sql += " from "
    sql += " ("
    sql += " select distinct t.tft_chip_id,t.test_tool_id,t.product_code,t.defect_code_desc,t.test_signal_no,t.test_gate_no"
    sql += " from celods.h_dax_fbk_defect_ods t"
    sql += " where t.site_type = 'BEOL'"
    sql += " and t.site_id = 'L11'"
    sql += " and t.test_op_id = 'CGL'"
    sql += " and t.defect_code_desc in ('DP')"
    sql += " and t.tft_chip_id in"
    sql += " ("
    sql += " select distinct t.tft_chip_id"
    sql += " from celods.h_dax_fbk_test_ods t"
    sql += " where t.site_type = 'BEOL'"
    sql += " and t.site_id = 'L11'"
    sql += " and t.tool_id <> 'DMYG2Z'"
    sql += " and t.op_id in ('OCT1','OCT2')"
    sql += " and t.first_yield_flag = 'Y'"
    sql += " and t.mfg_day between to_date('" + date1 + "','yyyy-mm-dd') and to_date('" + date2 + "','yyyy-mm-dd')"
    sql += " and t.defect_code_desc in ('BP','BP IN GOMI','BP IN GRAY') "
    sql += r" and t.test_user not like '%CC%' "
    sql += " )"
    sql += " )a"
    sql += " Right Join"
    sql += " ("
    sql += " select distinct t.tft_chip_id,t.test_tool_id,t.product_code,t.defect_code_desc,t.test_signal_no,t.test_gate_no,t.test_time"
    sql += " from celods.h_dax_fbk_defect_ods t"
    sql += " where t.site_type = 'BEOL'"
    sql +=  " and t.site_id = 'L11'"
    sql += " and t.test_op_id in ('OCT2','OCT1')"
    sql += " and t.major_defect_flag = 'Y'"
    sql += " and t.defect_code_desc in ('BP','BP IN GOMI','BP IN GRAY') "
    sql += " and t.tft_chip_id in"
    sql += " ("
    sql += " select distinct t.tft_chip_id"
    sql += " from celods.h_dax_fbk_test_ods t"
    sql += " where t.site_type = 'BEOL'"
    sql += " and t.site_id = 'L11'"
    sql += " and t.tool_id <> 'DMYG2Z'"
    sql += " and t.op_id in ('OCT1','OCT2')"
    sql += " and t.first_yield_flag = 'Y'"
    sql += " and t.mfg_day between to_date('" + date1 + "','yyyy-mm-dd') and to_date('" + date2 + "','yyyy-mm-dd')"
    sql += " and t.defect_code_desc in ('BP','BP IN GOMI','BP IN GRAY') "
    sql += " )"
    sql += " )b"
    sql += " on a.tft_chip_id = b.tft_chip_id"
    sql += " )a"
    sql += " )a"
    sql += " where a.N = 1"
    sql += " group by a.test_tool_id,a.product_code"
    sql += " )a"
    sql += " Right Join"
    sql += " ("
    sql += " select a.tool_id,a.product_code,nvl(sum(NN),0) as total"
    sql += " from "
    sql += " ("
    sql +=  " select a.tool_id,a.tft_chip_id, a.product_code,a.OCT_defect,a.CT1_defect, a.mfg_day,"
    sql += " Case "
    sql += " when (a.OCT_defect in ('BP','BP IN GOMI','BP IN GRAY') and a.CT1_defect in ('DP','DP-PAIR','3DP-ADJ','DP-CLUSTER','DP-NEAR')) then 1 End as N,"
    sql += " Case "
    sql += " when a.CT1_defect in ('DP') then 1 End as NN"
    sql += " from"
    sql += " ("
    sql += " select distinct b.tft_chip_id,b.tool_id,b.product_code,b.defect_code_desc as OCT_defect,a.defect_code_desc as CT1_defect, b.mfg_day "
    sql += " from "
    sql += " ("
    sql += " select t.tft_chip_id,t.product_code,t.defect_code_desc"
    sql += " from celods.h_dax_fbk_defect_ods t"
    sql += " where t.site_type = 'BEOL'"
    sql += " and t.site_id = 'L11'"
    sql += " and t.test_op_id = 'CGL'"
    sql += " and t.defect_code_desc in ('DP')"
    sql += " )a"
    sql += " Right Join"
    sql += " ("
    sql += " select t.tft_chip_id,t.tool_id,t.product_code,t.defect_code_desc, t.mfg_day "
    sql += " from celods.h_dax_fbk_test_ods t"
    sql += " where t.site_type = 'BEOL'"
    sql += " and t.site_id = 'L11'"
    sql += " and t.tool_id <> 'DMYG2Z'"
    sql += " and t.op_id in ('OCT1','OCT2')"
    sql += " and t.first_yield_flag = 'Y'"
    sql += " and t.mfg_day between to_date('" + date1 + "','yyyy-mm-dd') and to_date('" + date2 + "','yyyy-mm-dd')"
    sql += " )b"
    sql += " on a.tft_chip_id = b.tft_chip_id"
    sql += " )a"
    sql += " )a"
    sql += " where NN = 1 "
    sql += " group by a.tool_id,a.product_code order by 1"
    sql += " )b"
    sql += " on a.test_tool_id = b.tool_id"
    sql += " where a.product_code = b.product_code"
    sql += " order by 1"

    logging.info('octDP2BP sql: '+sql)
    octDP2BP = ora2df(sql)
   
    
    
    
    date12_list = datesListStr(date1, date2)
    table = 'oct_dp2bp'
    db_data = mysql2df(table)
    #db_data = db_data[db_data['TEST_TIME_MFG'].isin(date12_list)]
    #print(db_data)
    for i in range(len(octDP2BP)):
        tool_id = octDP2BP.loc[i]['TOOL_ID']
        pc = octDP2BP.loc[i]['PRODUCT_CODE']
        
        df_rawData = dp2bpRaw(date1, date2, tool_id, pc)
        ok_count = 0
        ng_count = 0
        df_rawData.drop_duplicates(['CHIP_ID', 'OCT_DEFECT'], keep='last', inplace=True)
        df_rawData.reset_index(inplace=True, drop=True)
        # 初始化
        df0 = []
        for j in range(len(df_rawData)):
            chipid = df_rawData.loc[j]['CHIP_ID']
            #print(chipid)
            test_time = str(df_rawData.loc[j]['TEST_TIME'])
            #  
            #print(test_time)
            #print(str(db_data['TEST_TIME']))
            df0 = db_data[(db_data['CHIP_ID']==chipid) & (db_data['TEST_TIME']==test_time)]
            
            df0.drop_duplicates(['CHIP_ID', 'OCT_DEFECT'], keep='last', inplace=True)
            df0_ok = df0[df0['octDP2BP_OK'] == 'OK']
            df0_ng = df0[df0['octDP2BP_OK'] == 'NG']
            ok_count += len(df0_ok) 
            ng_count += len(df0_ng) 
        #print(tool_id, pc)
        #df0 = db_data[(db_data['PRODUCT_CODE']==pc) & (db_data['TOOL_ID']==tool_id)]
        #df0.drop_duplicates(['CHIP_ID'], keep='last', inplace=True)
        #df0_count = len(df0)
        
        octDP2BP.loc[i, 'OK總數'] = str(int(ok_count))
        octDP2BP.loc[i, 'NG總數'] = str(int(ng_count))
        octDP2BP.loc[i, '待確認'] = str(int(octDP2BP.loc[i]['RB'] - ng_count - ok_count))
        octDP2BP.loc[i, '異常說明'] = '無'
        if len(df0) > 0:
            octDP2BP.loc[i, '異常說明'] = df0.loc[df0.index[-1]]['octDP2BP_OK_rem']
    return render_template('userMain.html', user=str(user),name=name, auth=auth, shift=shift, sectShow=sectShow,
                           date1=date1, date2=date2,octDP2BP= octDP2BP)

def dp2bpRaw(date1, date2, tool_id, pc):
    sql = "select *"
    sql += " from "
    sql += " ("
    sql += " select a.test_mfg_day,a.test_time,a.tft_chip_id as chip_id, a.OCT_defect,a.OCT_X,a.OCT_Y,a.CT1_defect,a.CT1_X,a.CT1_Y,a.X_error,a.Y_error, a.test_user, a.model_no as CT1_model, a.oct_user,"
    sql += " Case "
    sql += " when X_error <= 10 and Y_error <= 10 then 1 End as N"
    sql += " from "
    
    sql += " ("
    sql += " select b.test_mfg_day,b.test_time,b.tft_chip_id,b.defect_code_desc as OCT_defect,b.test_signal_no as OCT_X,b.test_gate_no as OCT_Y,a.defect_code_desc as CT1_defect,a.test_signal_no as CT1_X,a.test_gate_no as CT1_Y, b.test_user as oct_user,abs(a.test_signal_no-b.test_signal_no) as X_error,abs(a.test_gate_no-b.test_gate_no) as Y_error, a.test_user, a.model_no"
    sql += " from "
    sql += " ("
    sql += " select distinct t.tft_chip_id,t.defect_code_desc,t.test_signal_no,t.test_gate_no, t.test_user, t.model_no"
    sql += " from celods.h_dax_fbk_defect_ods t"
    sql += " where t.site_type = 'BEOL'"
    sql += " and t.site_id = 'L11'"
    sql += " and t.test_op_id = 'CGL'"
    sql += " and t.defect_code_desc in ('DP')"
    sql += " and t.tft_chip_id in"
    sql += " ("
    sql += " select distinct t.tft_chip_id"
    sql += " from celods.h_dax_fbk_test_ods t"
    sql += " where t.site_type = 'BEOL'"
    sql += " and t.site_id = 'L11'"
    sql += " and t.tool_id <> 'DMYG2Z'"
    sql += " and t.op_id in ('OCT1','OCT2')"
    sql += " and t.first_yield_flag = 'Y'"
    sql += " and t.tool_id = '" + tool_id + "'"
    sql += " and t.product_code = '" + pc + "'"
    
    sql += " and t.mfg_day between to_date('" + date1 + "','yyyy-mm-dd') and to_date('" + date2 + "','yyyy-mm-dd')"
    sql += " and t.defect_code_desc in ('BP','BP IN GOMI','BP IN GRAY') "
    sql += " )"
    sql += " )a"
    sql += " Right Join "
    sql += " ("
    sql += " select distinct t.tft_chip_id,t.defect_code_desc,t.test_signal_no,t.test_gate_no, t.test_user,t.test_time, t.test_mfg_day"
    sql += " from celods.h_dax_fbk_defect_ods t"
    sql += " where t.site_type = 'BEOL'"
    sql += " and t.site_id = 'L11'"
    sql += " and t.test_op_id in ('OCT2','OCT1')"
    sql += " and t.major_defect_flag = 'Y'"
    sql += " and t.defect_code_desc in ('BP','BP IN GOMI','BP IN GRAY') "
    sql += r" and t.test_user not like '%CC%' "
    sql += " and t.tft_chip_id in"
    sql += " ("
    sql += " select distinct t.tft_chip_id"
    sql += " from celods.h_dax_fbk_test_ods t"
    sql += " where t.site_type = 'BEOL'"
    sql += " and t.site_id = 'L11'"
    sql += " and t.tool_id <> 'DMYG2Z'"
    sql += " and t.op_id in ('OCT1','OCT2')"
    sql += " and t.first_yield_flag = 'Y'"
    sql += " and t.tool_id = '" + tool_id + "'"
    sql += " and t.product_code = '" + pc + "'"
    sql += " and t.mfg_day between to_date('" + date1 + "','yyyy-mm-dd') and to_date('" + date2 + "','yyyy-mm-dd')"
    sql += " and t.defect_code_desc in ('BP','BP IN GOMI','BP IN GRAY') "
    sql += " )"
    sql += " )b"
    sql += " on a.tft_chip_id = b.tft_chip_id"
    sql += " )a"
    sql += " )a"
    sql += " where a.N = 1"
    sql += " order by 1,2,3"
    
    logging.info('octDP2BPRAW sql: '+sql)
    octDP2BPRaw = ora2df(sql)
    octDP2BPRaw.drop_duplicates(['CHIP_ID'], keep='last', inplace=True)
    octDP2BPRaw.reset_index(drop=True, inplace=True)
    return octDP2BPRaw


def octDP2BPRaw(user,name, auth, shift, date1, date2, tool_id, pc):
    sectShow = 'octDP2BPRaw'
    
    octDP2BPRaw = dp2bpRaw(date1, date2, tool_id, pc)
    print(octDP2BPRaw)
    
    # 紀錄查詢
    table = 'oct_dp2bp'
    db_data = mysql2df(table)
    #db_data = db_data[db_data['TEST_TIME_MFG'].isin(date12_list)]
    #print(db_data)
    
    
    first_idx = 0
    if len(octDP2BPRaw) != 0:
        df_adc = octDP2BPRaw[['CHIP_ID']]
        df_aoi = octDP2BPRaw[['CHIP_ID']]
        df_ct1 = octDP2BPRaw[['CHIP_ID']]
        octDP2BPRaw = octDP2BPRaw.drop(columns=['N', 'TEST_USER'])
    else:
        df_adc = pd.DataFrame()
        df_aoi = pd.DataFrame()
        df_ct1 = pd.DataFrame()
    
    # 取最新的一筆
    
    for i in range(len(octDP2BPRaw)):
        
        chipid = octDP2BPRaw.loc[i]['CHIP_ID']
        test_time = str(octDP2BPRaw.loc[i]['TEST_TIME'])
        oct_def = octDP2BPRaw.loc[i]['OCT_DEFECT']
        
        
        
        
        # [Jbox_id
        sql = r"select T.SHEET_ID_CHIP_ID,t.cassette_id as boxid "
        sql += r" from celods.r_chip_wip_ods t"
        sql += r" WHERE T.SHEET_ID_CHIP_ID='" + chipid + "'"
        df_boxid = ora2df(sql)
        df_boxid.fillna('   ', inplace=True)
        if len(df_boxid) >= 1:
            box_id = df_boxid.loc[len(df_boxid)-1]['BOXID']
            if box_id == '   ':
                box_id = octDP2BPRaw.loc[i, 'OCT_USER']+''
        else:
            box_id = 'No sql record'
            
        octDP2BPRaw.loc[i, 'BOX_ID'] = box_id
        
        
        df0 = db_data[(db_data['CHIP_ID']==chipid) & (db_data['TEST_TIME']==test_time) & (db_data['OCT_DEFECT']==oct_def)]
        if len(df0) > 0:
            last_n = df0.index[-1]
            #df0.drop_duplicates(['CHIP_ID', 'OCT_DEFECT'], keep='last', inplace=True)
            okng = df0.loc[last_n]['octDP2BP_OK']
            octDP2BPRaw.loc[i, 'Check'] = okng
        else:
            octDP2BPRaw.loc[i, 'Check'] = '未確認'
            
            
        
            
            
        octDP2BPRaw.loc[i, 'ID_CNT'] = 0
        
        if i <= len(octDP2BPRaw) - 2:
            
            next_chipid = octDP2BPRaw.loc[i+1]['CHIP_ID']
            oct_def = octDP2BPRaw.loc[i]['OCT_DEFECT']
            next_oct_def = octDP2BPRaw.loc[i+1]['OCT_DEFECT']

            
            if (chipid != next_chipid) or (oct_def != next_oct_def):
                octDP2BPRaw.loc[first_idx, 'ID_CNT'] = i - first_idx + 1
                first_idx = i+1
            else:
                1
        # 最後一筆也要計算張數
        else:
            octDP2BPRaw.loc[first_idx, 'ID_CNT'] = i - first_idx + 1
        
        
        
        # 找aoi adc的func圖
        octaoi_imgs = []
        octadc_imgs = []
        isAOI = True
        isADC = True
        isCT1 = True
        isCT1D = False
        eqp_oct = tool_id
        date_oct = test_time[0:4] + test_time[5:7] + test_time[8:10]
        print('oct_IMG',chipid, date_oct, eqp_oct, oct_def)
        octimgs = octDefectImg(chipid, date_oct, eqp_oct, oct_def)
        #ct1_def = octDP2BPRaw.loc[i]['TEST_USER']
        ct1_defect = octDP2BPRaw.loc[i]['CT1_DEFECT']
        ct1_defect = 'DP'
        ct1_model = octDP2BPRaw.loc[i]['CT1_MODEL']
        #ct1_img = ct1DefectImg(date1, date2, ct1_model, ct1_defect, ct1_def, chipid)
        #ct1_img = ct1DefectImg2(ct1_defect, ct1_def, chipid)
        
        ct1_x = str(octDP2BPRaw.loc[i]['CT1_X'])
        ct1_y = str(octDP2BPRaw.loc[i]['CT1_Y'])
        ct1_img = ct1DefectImg_DP2BP(chipid, ct1_x, ct1_y)
        aoi_img = octimgs[0]
        adc_img = octimgs[1]
        for img in adc_img:
            1
            #img_html += r"<a href='"+img+"'><img align='center' width='160' height='120' src='"+img+"'  ></a>"
        #octADCRBSucRaw.loc[i, 'IMG'] = img_html
        
        
        
        
        
        for num0 in range(len(adc_img)):
            pattern= ""
            img_name = os.path.basename(adc_img[num0])
            spl = img_name.split('_')
            pattern = spl[3][1:]+'_'+spl[4] + '<br/>'
            df_adc.loc[i, 'IMG_'+str(num0)] = pattern + r"<a href='"+adc_img[num0]+"'><img align='center' width='160' height='120' src='"+adc_img[num0]+"'  ></a>"
        for num0 in range(len(aoi_img)):
            pattern= ""
            img_name = os.path.basename(aoi_img[num0])
            spl = img_name.split('_')
            pattern = spl[3][1:]+'_'+spl[4] + '<br/>'
            df_aoi.loc[i, 'IMG_'+str(num0)] = pattern + r"<a href='"+aoi_img[num0]+"'><img align='center' width='160' height='120' src='"+aoi_img[num0]+"'  ></a>"
        
        for num0 in range(len(ct1_img)):
            pattern= ""
            img_name = os.path.basename(ct1_img[num0])
            spl = img_name.split('_')
            #pattern = spl[3][1:]+'_'+spl[4] + '<br/>'
            df_ct1.loc[i, 'IMG_'+str(num0)] = r"<a href='"+ct1_img[num0]+"'><img align='center' width='160' height='120' src='"+ct1_img[num0]+"'  ></a>"
        
        
        
            
        
        
    
    
    
    
    
    return render_template('userMain.html', user=str(user),name=name, auth=auth, shift=shift, sectShow=sectShow,
                           tool_id=tool_id, pc=pc, octDP2BPRaw= octDP2BPRaw, 
                           df_aoi=df_aoi, df_adc=df_adc, df_ct1=df_ct1)
    
    
def octDP2BP_Upload(user,name, auth, shift, req_list):
    #返回第一層
    sectShow = 'octDP2BP'
    #sectShow = 'uploadOK'
    
    #df_dp2bp = pd.DataFrame(columns=['user', 'name', 'shift', 'auth'])
    table = 'oct_dp2bp'
    df_data = mysql2df(table)
    df_dp2bp = pd.DataFrame(columns=df_data.columns)
    newIdx = len(df_dp2bp)
    
    now_hm = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    check = request.form.get('octDP2BP_OK')
    check_rem = request.form.get('octDP2BP_OK_rem')
    for item in req_list:
        if '__' not in item:
            continue
        
        req = request.form.get(item)
        name_idx = newIdx
        try:
            aaa = item.split('__',2)
            num = int(aaa[0])
            col = aaa[1]
            
        except:
            continue
        df_dp2bp.loc[newIdx+num, col] = req
        #　imgCheck'為每一個Ｉｄ的最後一項
        1
    # 個別補上個人資訊
    user_list = ['user', 'name', 'shift', 'auth', 'TOOL_ID', 'PRODUCT_CODE', 'octDP2BP_OK', 'octDP2BP_OK_rem']
    drop_list = []
    for m in range(num+1):
        check0 = df_dp2bp.loc[newIdx+m]['Check']
        if check0 != '未確認' or check0 is None or pd.isna(check0):
            drop_list.append(newIdx+m)
        for ii in user_list:
            req = request.form.get(ii)
            df_dp2bp.loc[newIdx+m, ii] = req
        df_dp2bp.loc[newIdx+m, 'Checked_Date'] = now_hm
        
        # 新增MFG DATE轉換資訊
        #test_time = df_dp2bp.loc[newIdx+m]['TEST_TIME']
        #df_dp2bp.loc[newIdx+m,'TEST_TIME_MFG'] = testTime2MFG(str(test_time))
        
    df_dp2bp = df_dp2bp.drop(drop_list)
    df_dp2bp.reset_index(inplace=True, drop=True)
    df_dp2bp = df_dp2bp.drop(columns=['Check'])
    print(df_dp2bp)
    df2mysql_append(df_dp2bp, table)
    
    today = datetime.date.today().strftime("%Y-%m-%d")
    date1 = today
    date2 = today
    
    return octDP2BP(user,name, auth, shift, date1, date2)
    



def octADCRBSuc(user,name, auth, shift, date1,date2):
    
    sectShow = 'octADCRBSuc'
    sql = r" select distinct t.tft_chip_id AS CHip_ID,t.mfg_day,t.test_time,t.tool_id,t.product_code,t.pre_grade,"
    sql += r" t.grade,t.defect_code_desc as defect,t.pre_defect_code_desc,b.test_user as PRE_test_user,t.abbr_no,"
    sql += r" case when t.defect_code_desc like '%BP%' THEN 'BP'"
    sql += r"      when t.defect_code_desc like 'OTHER GLASS DEFECT' THEN 'OGD'"
    sql += r"      when t.defect_code_desc like '%CELL PARTICLE%' THEN 'CP'"
    sql += r"      ELSE t.defect_code_desc"
    sql += r"      END AS type_group"
         
    sql += r" from("
    sql += r" select *"
    sql += r" from celods.h_dax_fbk_test_ods"
    #sql += r" where mfg_day > current_date - interval '1' DAY"
    sql += r" where mfg_day between to_date('" + date1 + "','yyyy-mm-dd') and to_date('" + date2 + "','yyyy-mm-dd')"
    
    sql += r" and site_type='BEOL'"
    sql += r" and site_id='L11'"
    sql += r" and op_id='ADC2'"
    sql += r" and pre_grade in ('X','W')"
    sql += r" and abbr_no not like '%RK%'"
    sql += r" and pre_defect_code_desc like '%BP%'"
    sql += r" )t"
    sql += r" left join celods.h_dax_fbk_test_ods b on"
    sql += r" t.tft_chip_id=b.tft_chip_id"
    sql += r" and t.product_code=b.product_code"
    sql += r" and b.judge_cnt < t.judge_cnt"
    sql += r" and b.op_id='CGL'"
    sql += r" and b.mfg_day > (to_date('" + date1 + "','yyyy-mm-dd') - interval '60' day)"
    # 建立各defect的數量
    raw_data0 = ora2df(sql)
    
    if len(raw_data0) == 0:
        table = 'octADCRBSuc'
        octADCRBSuc = pd.DataFrame(columns =["該日期無資料"])
        return render_template('userMain.html', user=str(user),name=name, auth=auth, shift=shift, sectShow=sectShow,
                               date1=date1, date2=date2, octADCRBSuc= octADCRBSuc)
        
    raw_data0.fillna({'DEFECT':'   '}, inplace=True)
    raw_data1 = raw_data0.groupby(['PRODUCT_CODE', 'TOOL_ID', 'DEFECT'])
    raw_data2 = raw_data1.size().to_frame(name='COUNT')
    raw_data2 = raw_data2.reset_index()
    
    #加總指定ｄｅｆｅｃｔ
    bp_raw = raw_data2[(raw_data2['DEFECT'].str.contains('BP'))]
    df_bps = bp_raw.groupby(['PRODUCT_CODE', 'TOOL_ID'])['COUNT'].agg('sum').to_frame(name='BPs')
    
    ogd_raw = raw_data2[(raw_data2['DEFECT'].str.contains('OTHER GLASS DEFECT'))]
    df_ogd = ogd_raw.groupby(['PRODUCT_CODE', 'TOOL_ID'])['COUNT'].agg('sum').to_frame(name='OGD')
    
    none_raw = raw_data2[(raw_data2['DEFECT'].str.contains('   '))]
    df_none = none_raw.groupby(['PRODUCT_CODE', 'TOOL_ID'])['COUNT'].agg('sum').to_frame(name='空白')
        
    cp_raw = raw_data2[(raw_data2['DEFECT'].str.contains('CELL PARTICLE'))]
    df_cp = cp_raw.groupby(['PRODUCT_CODE', 'TOOL_ID'])['COUNT'].agg('sum').to_frame(name='CP')
      
    df_tot = raw_data2.groupby(['PRODUCT_CODE', 'TOOL_ID'])['COUNT'].agg('sum').to_frame(name='總數')
      
    
    # 合併表格
    octADCRBSuc = pd.concat([df_bps, df_ogd,df_none, df_cp, df_tot], verify_integrity = True, axis=1)
    octADCRBSuc = octADCRBSuc.fillna(0)
    
    octADCRBSuc = octADCRBSuc.reset_index()
    
    octADCRBSuc[['OGD', 'BPs', '空白', 'CP']] = octADCRBSuc[['OGD', 'BPs', '空白', 'CP']].astype('int')

    octADCRBSuc['BPs(%)'] = 100*octADCRBSuc['BPs'] / octADCRBSuc['總數']
    octADCRBSuc['OGD(%)'] = 100*octADCRBSuc['OGD'] / octADCRBSuc['總數']
    octADCRBSuc['空白(%)'] = 100*octADCRBSuc['空白'] / octADCRBSuc['總數']
    octADCRBSuc['CP(%)'] = 100*octADCRBSuc['CP'] / octADCRBSuc['總數']
    octADCRBSuc['NG_RATIO'] = 100*(octADCRBSuc['總數'] - octADCRBSuc['BPs']) / octADCRBSuc['總數']
    octADCRBSuc['NG_RATIO(不含CP)'] = 100*(octADCRBSuc['總數'] - octADCRBSuc['BPs']- octADCRBSuc['CP']) / octADCRBSuc['總數']
    octADCRBSuc['OGD確認'] = 0#octADCRBSuc['OGD']
    octADCRBSuc['OGD確認(%)'] = octADCRBSuc['OGD']
    octADCRBSuc['空白確認'] = 0#octADCRBSuc['空白']
    octADCRBSuc['空白確認(%)'] = octADCRBSuc['空白']
    octADCRBSuc['CP確認'] = 0#octADCRBSuc['CP']
    octADCRBSuc['CP確認(%)'] = octADCRBSuc['CP']
    
    table = 'oct_adcrbsuc'
    db_data = mysql2df(table)

    for item in octADCRBSuc.index:
        
        tool_id = octADCRBSuc.loc[item]['TOOL_ID']
        pc = octADCRBSuc.loc[item]['PRODUCT_CODE']
        tot = octADCRBSuc.loc[item]['總數']
        
        raw_data1 = raw_data0[(raw_data0['TOOL_ID'] == tool_id) & (raw_data0['PRODUCT_CODE'] == pc)]
        db_data1 = db_data[(db_data['TOOL_ID']==tool_id) & (db_data['PRODUCT_CODE']==pc)]
        
        
        for def_col in ['OGD', '空白', 'CP']:
            
            if def_col == 'BPs':
                defect = 'BP'
            elif def_col == 'OGD':
                defect = 'OTHER GLASS DEFECT'
            elif def_col == '空白':
                defect = '   '
            elif def_col == 'CP':
                defect = 'CELL PARTICLE'

            #octADCRBSucRaw = raw_data0[(raw_data0['DEFECT'].str.contains(defect)) & (raw_data0['TOOL_ID'] == tool_id) & (raw_data0['PRODUCT_CODE'] == pc)]
            octADCRBSucRaw = raw_data1[(raw_data1['DEFECT'].str.contains(defect))]
            # 紀錄查詢
            
            #db_data = db_data[(db_data['TOOL_ID']==tool_id) & (db_data['PRODUCT_CODE']==pc) & (db_data['DEFECT'].str.contains(defect))]
            
            for i in octADCRBSucRaw.index:
                chipid = octADCRBSucRaw.loc[i]['CHIP_ID']
                date0 = str(octADCRBSucRaw.loc[i]['TEST_TIME'])
                date_oct = date0[0:4] + date0[5:7] + date0[8:10]
                eqp_oct = octADCRBSucRaw.loc[i]['TOOL_ID']
                oct_def = octADCRBSucRaw.loc[i]['DEFECT']
                
                #pre_test_user = octADCRBSuc.loc[i]['PRE_TEST_USER']
        
                
                #df0 = db_data[(db_data['CHIP_ID']==chipid) & (db_data['TOOL_ID']==eqp_oct) & (db_data['DEFECT']==oct_def)]
                df0 = db_data1[(db_data1['CHIP_ID']==chipid) & (db_data1['DEFECT']==oct_def)]
                if len(df0) > 0:
                    last_n = df0.index[-1]
                    #df0.drop_duplicates(['CHIP_ID', 'OCT_DEFECT'], keep='last', inplace=True)
                    okng = df0.loc[last_n]['Check']
                    #remarks = df0.loc[last_n]['name']+', '+df0.loc[last_n]['Remarks']
                    octADCRBSuc.loc[item, def_col+'確認'] = octADCRBSuc.loc[item][def_col+'確認'] + 1
                    if okng in ['Real', '多顆']:
                        
                        octADCRBSuc.loc[item, def_col+'確認(%)'] = octADCRBSuc.loc[item][def_col+'確認(%)'] - 1
            octADCRBSuc.loc[item, def_col+'確認(%)'] = 100*octADCRBSuc.loc[item][def_col+'確認(%)']/tot
            
            
            
            """
            tmp = 100*octADCRBSuc['OGD確認(%)'] / octADCRBSuc['總數']
            octADCRBSuc['OGD確認(%)'] = tmp
            tmp = 100*octADCRBSuc['空白確認(%)'] / octADCRBSuc['總數']
            octADCRBSuc['空白確認(%)'] = tmp
            tmp = 100*octADCRBSuc['CP確認(%)'] / octADCRBSuc['總數']
            octADCRBSuc['CP確認(%)'] = tmp
            """
       
        octADCRBSuc = octADCRBSuc.round(2)
        
    print(octADCRBSuc)
    #octADCRBSuc = octADCRBSuc.astype('str')
    table = 'octADCRBSuc'

    return render_template('userMain.html', user=str(user),name=name, auth=auth, shift=shift, sectShow=sectShow,
                           date1=date1, date2=date2, octADCRBSuc= octADCRBSuc)
    
    
def octADCRBSucRaw(user,name, auth, shift, date1, date2, tool_id, pc, def_col, btnName):
    
    sectShow = 'octADCRBSucRaw'
    sql = r" select distinct t.tft_chip_id AS CHip_ID, t.mfg_day, t.test_time,t.tool_id,t.product_code,t.pre_grade,"
    sql += r" t.grade,t.defect_code_desc as defect,t.pre_defect_code_desc as pre_defect,b.test_user as PRE_test_user,t.abbr_no,"
    sql += r" case when t.defect_code_desc like '%BP%' THEN 'BP'"
    sql += r"      when t.defect_code_desc like 'OTHER GLASS DEFECT' THEN 'OGD'"
    sql += r"      when t.defect_code_desc like '%CELL PARTICLE%' THEN 'CP'"
    sql += r"      ELSE t.defect_code_desc"
    sql += r"      END AS type_group"
         
    sql += r" from("
    sql += r" select *"
    sql += r" from celods.h_dax_fbk_test_ods"
    #sql += r" where mfg_day > current_date - interval '1' DAY"
    sql += r" where mfg_day between to_date('" + date1 + "','yyyy-mm-dd') and to_date('" + date2 + "','yyyy-mm-dd')"
    
    sql += r" and site_type='BEOL'"
    sql += r" and site_id='L11'"
    sql += r" and op_id='ADC2'"
    sql += r" and pre_grade in ('X','W')"
    sql += r" and abbr_no not like '%RK%'"
    sql += r" and pre_defect_code_desc like '%BP%'"
    sql += r" )t"
    sql += r" left join celods.h_dax_fbk_test_ods b on"
    sql += r" t.tft_chip_id=b.tft_chip_id"
    sql += r" and t.product_code=b.product_code"
    sql += r" and b.judge_cnt < t.judge_cnt"
    sql += r" and b.op_id='CGL'"
    sql += r" and b.mfg_day > (to_date('" + date1 + "','yyyy-mm-dd') - interval '60' day)"
    raw_data0 = ora2df(sql)
    raw_data0.fillna({'DEFECT':'   '}, inplace=True)
    
    if def_col == 'BPs':
        defect = 'BP'
    elif def_col == 'OGD':
        defect = 'OTHER GLASS DEFECT'
    elif def_col == '空白':
        defect = '   '
    elif def_col == 'CP':
        defect = 'CELL PARTICLE'
    
    octADCRBSucRaw = raw_data0[(raw_data0['DEFECT'].str.contains(defect)) & (raw_data0['TOOL_ID'] == tool_id) & (raw_data0['PRODUCT_CODE'] == pc)].copy()
    octADCRBSucRaw.reset_index(drop=True, inplace=True)
    #octADCRBSucRaw['IMG'] = 'NA'
    octADCRBSucRaw['確認'] = 'NA'
    octADCRBSucRaw['說明'] = 'NA'
    # 紀錄查詢
    table = 'oct_adcrbsuc'
    db_data = mysql2df(table)
    
    df_aoi = octADCRBSucRaw[['CHIP_ID']]
    df_adc = octADCRBSucRaw[['CHIP_ID','DEFECT', '確認', '說明']]
    for i in octADCRBSucRaw.index:
        chipid = octADCRBSucRaw.loc[i]['CHIP_ID']
        date0 = str(octADCRBSucRaw.loc[i]['TEST_TIME'])
        date_oct = date0[0:4] + date0[5:7] + date0[8:10]
        eqp_oct = octADCRBSucRaw.loc[i]['TOOL_ID']
        oct_def = octADCRBSucRaw.loc[i]['DEFECT']
        
        #pre_test_user = octADCRBSuc.loc[i]['PRE_TEST_USER']

        
        df0 = db_data[(db_data['CHIP_ID']==chipid) & (db_data['TOOL_ID']==eqp_oct) & (db_data['DEFECT']==oct_def)].copy()
        if len(df0) > 0:
            last_n = df0.index[-1]
            #df0.drop_duplicates(['CHIP_ID', 'OCT_DEFECT'], keep='last', inplace=True)
            okng = df0.loc[last_n]['Check']
            remarks = df0.loc[last_n]['name']+', '+str(df0.loc[last_n]['Remarks'])
            octADCRBSucRaw.loc[i, '確認'] = str(okng)
            octADCRBSucRaw.loc[i, '說明'] = str(remarks)
        df_adc.loc[i, '確認'] = octADCRBSucRaw.loc[i]['確認']
        df_adc.loc[i, '說明'] = octADCRBSucRaw.loc[i]['說明']
            
        octimgs = octDefectImg(chipid, date_oct, eqp_oct, oct_def)
        aoi_img = octimgs[0]
        adc_img = octimgs[1]
        img_html = ""
        # 合併原表格版本
        for img in adc_img:
            1
            #img_html += r"<a href='"+img+"'><img align='center' width='160' height='120' src='"+img+"'  ></a>"
        #octADCRBSucRaw.loc[i, 'IMG'] = img_html
        # ADC影像過濾
        skip_n = 0
        df_record = pd.DataFrame(columns=['ptc', 'cx', 'cy'])
        for num0 in range(len(adc_img)):
            pattern= ""
            img_name = os.path.basename(adc_img[num0])
            spl = img_name.split('_')
            if spl[4] in ['R', 'G', 'B']:
                skip_n += 1
                continue
            ptc0 = spl[4]
            cx0 = spl[6]
            cy0 = spl[8]
            print(ptc0, cx0, cy0)
            df0 = df_record[(df_record['ptc'] == ptc0) & (abs(df_record['cx'] - 10) > 0) & (abs(df_record['cy'] - 5) > 0 )]
            if len(df0) > 0:
                skip_n += 1
                continue
            df_record.loc[num0, 'ptc'] = ptc0
            df_record.loc[num0, 'cx'] = int(cx0)
            df_record.loc[num0, 'cy'] = int(cy0)
            
            pattern = spl[3][1:]+'_'+spl[4] + '<br/>'
            df_adc.loc[i, 'IMG_'+str(num0-skip_n)] = pattern + r"<a href='"+adc_img[num0]+"'><img align='center' width='160' height='120' src='"+adc_img[num0]+"'  ></a>"
        
        
        
            #return send_from_directory(path, file, as_attachment=True)
        
        
        #img_html = r"<img src='"+adc_img+"'  >"
        #"<a href='"+img_path+"'><img width='240' height='180' src='"+img_path+"' ></a>"
                        
    #　如果無影像則改為空ＤＦ
    if len(df_adc.columns) == 1:
        1
        #df_adc = pd.DataFrame()
    
    #octaoi_list.append(octaoi_imgs)
    #octadc_list.append(octadc_imgs)
    octADCRBSucRaw.drop(columns=['MFG_DAY'], inplace=True)
    try:
        path000 = r'static/csv'
        if not os.path.exists(path000):
            os.mkdir(path000)
        filepath = r'static/csv/'+btnName+'.csv'
        octADCRBSucRaw.to_csv(filepath, index=False, encoding='utf-8-sig')
    except:
        print('csv儲存失敗')
    #octADCRBSucRaw = octADCRBSucRaw.reset_index(drop=True)
    #print(octADCRBSucRaw)
    return render_template('userMain.html', user=str(user),name=name, auth=auth, shift=shift, sectShow=sectShow,
                           date1=date1, date2=date2, octADCRBSucRaw= octADCRBSucRaw, df_adc=df_adc, tool_id=tool_id, pc=pc, def_col=def_col)
    
def octADCRBSucEQP(user,name, auth, shift, date1, date2, tool_id, pc, def_col):
    
    sectShow = 'octADCRBSucEQP'
    sql = r" select distinct t.tft_chip_id AS CHip_ID, t.mfg_day, t.test_time,t.tool_id,t.product_code,t.pre_grade,"
    sql += r" t.grade,t.defect_code_desc as defect,t.pre_defect_code_desc as pre_defect,b.test_user as PRE_test_user,t.abbr_no,"
    sql += r" case when t.defect_code_desc like '%BP%' THEN 'BP'"
    sql += r"      when t.defect_code_desc like 'OTHER GLASS DEFECT' THEN 'OGD'"
    sql += r"      when t.defect_code_desc like '%CELL PARTICLE%' THEN 'CP'"
    sql += r"      ELSE t.defect_code_desc"
    sql += r"      END AS type_group"
         
    sql += r" from("
    sql += r" select *"
    sql += r" from celods.h_dax_fbk_test_ods"
    #sql += r" where mfg_day > current_date - interval '1' DAY"
    sql += r" where mfg_day between to_date('" + date1 + "','yyyy-mm-dd') and to_date('" + date2 + "','yyyy-mm-dd')"
    
    sql += r" and site_type='BEOL'"
    sql += r" and site_id='L11'"
    sql += r" and op_id='ADC2'"
    sql += r" and pre_grade in ('X','W')"
    sql += r" and abbr_no not like '%RK%'"
    sql += r" and pre_defect_code_desc like '%BP%'"
    sql += r" )t"
    sql += r" left join celods.h_dax_fbk_test_ods b on"
    sql += r" t.tft_chip_id=b.tft_chip_id"
    sql += r" and t.product_code=b.product_code"
    sql += r" and b.judge_cnt < t.judge_cnt"
    sql += r" and b.op_id='CGL'"
    
    raw_data0 = ora2df(sql)
    raw_data0.fillna({'DEFECT':'   '}, inplace=True)
    
    if def_col == 'BPs':
        defect = 'BP'
    elif def_col == 'OGD':
        defect = 'OTHER GLASS DEFECT'
    elif def_col == '空白':
        defect = '   '
    elif def_col == 'CP':
        defect = 'CELL PARTICLE'
     #& (raw_data0['DEFECT'] == defect)
    raw_data1 = raw_data0[(raw_data0['TOOL_ID'] == tool_id) & (raw_data0['PRODUCT_CODE'] == pc)]
    raw_data1 = raw_data1.reset_index(drop=True)
    tot = len(raw_data1)
    raw_data2 = raw_data1.groupby(['DEFECT','PRE_TEST_USER'])
    raw_data2 = raw_data2.size().to_frame(name=tool_id)
    eqp_list = ['CCCGL1082','CCCGL1083','CCCGL2082','CCCGL2083','CCCGL3082',
                   'CCCGL3083','CCCGL4082','CCCGL4083','CCCGL5082','CCCGL5083',
                   'CCCGL6082','CCCGL6083','CCCGL7082','CCCGL7083','CCCGL8082',
                   'CCCGL8083','CCCGL9072','CCCGL9073']
    #full_index = pd.MultiIndex.from_product([['2021/12/22', '2021/12/23', '2021/12/24', '2021/12/25', '2021/12/26'], eqp_list])
    raw_data2.reset_index(drop=False, inplace=True)
    #octADCRBSucEQP.set_index( ['PRE_TEST_USER', 'DEFECT'], inplace=True)
    #octADCRBSucEQP = octADCRBSucEQP.reindex(eqp_list).fillna(0).T
    #octADCRBSucEQP.reset_index(drop=True, inplace=True)
    defect_ind = ['BPs', 'OTHER GLASS DEFECT', 'CELL PARTICLE', '   ']
    octADCRBSucEQP = pd.DataFrame(index =defect_ind, columns=eqp_list)
    
    for i in raw_data2.index:
        defect = raw_data2.loc[i]['DEFECT']
        eqp_ct1 = raw_data2.loc[i]['PRE_TEST_USER']
        num0 = raw_data2.loc[i][tool_id]
        if ('BP' in defect) or (defect in ['   ', 'OTHER GLASS DEFECT', 'CELL PARTICLE']):
            octADCRBSucEQP.loc[defect, eqp_ct1] = num0
            

    
    octADCRBSucEQP.fillna(0, inplace=True)
    octADCRBSucEQP.loc['BPs'] = 0
    
    for col in octADCRBSucEQP.columns:   
        tot0 = 0
        for defect in octADCRBSucEQP.index:
            if 'BP' in defect:
                num0 = octADCRBSucEQP.loc[defect][col]
                tot0 += num0
                #print(num0)
        
        octADCRBSucEQP.loc['BPs', col] = tot0
        #break
    
        #octADCRBSucEQP = octADCRBSucEQP.reindex(eqp_list).fillna(0).T
    octADCRBSucEQP = octADCRBSucEQP.loc[defect_ind] 
    sum_df = octADCRBSucEQP.sum()
    octADCRBSucEQP.loc['總計(%)'] = sum_df
    #octADCRBSucEQP = 100*octADCRBSucEQP/sum_df
    octADCRBSucEQP.fillna(0, inplace=True)
    octADCRBSucEQP.astype(int)
    octADCRBSucEQP.reset_index(drop=False, inplace=True)
    octADCRBSucEQP.rename(columns={'index':'單位(%)'}, inplace=True)
    #octADCRBSucEQP = octADCRBSucEQP.round(2)
    
    return render_template('userMain.html', user=str(user),name=name, auth=auth, shift=shift, sectShow=sectShow,
                           date1=date1, date2=date2, octADCRBSucEQP= octADCRBSucEQP,
                           tool_id=tool_id, pc=pc)
    
    
    
    
    
def octADCRBSuc_Upload(user,name, auth, shift, req_list):
    
    #返回第一層
    sectShow = 'octADCRBSuc'
    #sectShow = 'uploadOK'
    
    #df_dp2bp = pd.DataFrame(columns=['user', 'name', 'shift', 'auth'])
    table = 'oct_adcrbsuc'
    db_data = mysql2df(table)
    db_ADCRBSuc = pd.DataFrame(columns=db_data.columns)
    newIdx = len(db_ADCRBSuc)
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
        if col in db_ADCRBSuc.columns:
            db_ADCRBSuc.loc[newIdx+num, col] = req
        #　imgCheck'為每一個Ｉｄ的最後一項
        1
    # 個別補上個人資訊
    user_list = ['user', 'name', 'shift', 'auth']
    drop_list = []
    for m in db_ADCRBSuc.index:
        check0 = db_ADCRBSuc.loc[m]['Check']
        if check0 == '---' or check0 is None or pd.isna(check0):
            drop_list.append(m)
        for ii in user_list:
            req = request.form.get(ii)
            db_ADCRBSuc.loc[m, ii] = req
        db_ADCRBSuc.loc[m, 'Checked_Date'] = now_hm
        
        # 新增MFG DATE轉換資訊
        #test_time = df_dp2bp.loc[newIdx+m]['TEST_TIME']
        #df_dp2bp.loc[newIdx+m,'TEST_TIME_MFG'] = testTime2MFG(str(test_time))
        
    db_ADCRBSuc = db_ADCRBSuc.drop(drop_list)
    #db_ADCRBSuc.reset_index(inplace=True, drop=True)
    #db_ADCRBSuc = db_ADCRBSuc.drop(columns=['Check'])
    print(db_ADCRBSuc)
    df2mysql_append(db_ADCRBSuc, table)
    
    today = datetime.date.today().strftime("%Y-%m-%d")
    date1 = request.form.get('date1')
    date2 = request.form.get('date2')
    
    return octADCRBSuc(user,name, auth, shift, date1, date2)

def adcRBRej(date1, date2):
    sql = r"select t.mfg_day,t.test_time,t.tool_id,t.product_code,t.tft_chip_id as chip_id,t.pre_grade,"
    sql += r"t.grade,t.defect_code_desc as defect,t.pre_defect_code_desc as pre_defect,t.abbr_no,"
    sql += r"case when t.pre_defect_code_desc like '%BP%' THEN 'BP'"
    sql += r"     when t.pre_defect_code_desc like '%POINT-CLUSTER%' THEN 'BP'"
    sql += r"     when t.pre_defect_code_desc like '%CELL PARTICLE%' THEN 'CP'"
    sql += r"     ELSE t.pre_defect_code_desc"
    sql += r"     END AS type_group"
    sql += r" from celods.h_dax_fbk_test_ods t"
    sql += r" where mfg_day between to_date('" + date1 + "','yyyy-mm-dd') and to_date('" + date2 + "','yyyy-mm-dd')"
    sql += r" and t.site_type='BEOL'"
    sql += r" and t.site_id='L11'"
    sql += r" and t.op_id='OCT2'"
    sql += r" and t.pre_grade in ('RB','RC')"
    sql += r" and t.test_user like 'CC%'"
    sql += r" and t.tool_id not in ('CCCTS300','CCCTSA00','CCOCT300','CCOCT400')"

    raw_data0 = ora2df(sql)
    return raw_data0

def octADCRBRej(user,name, auth, shift, date1,date2):
    
    sectShow = 'octADCRBRej'
    # 建立各defect的數量
    raw_data0 = adcRBRej(date1, date2)
    #print(raw_data0)
    if len(raw_data0) == 0:
        octADCRBRej = pd.DataFrame(columns =["該日期無資料"])
    else:
        #raw_data0.fillna({'DEFECT':'   '}, inplace=True)
        raw_data1 = raw_data0.groupby(['PRODUCT_CODE', 'TOOL_ID', 'GRADE'])
        raw_data2 = raw_data1.size().to_frame(name='COUNT')
        raw_data2 = raw_data2.reset_index()
        
        #加總指定ｄｅｆｅｃｔ
        zp_raw = raw_data2[(raw_data2['GRADE'].isin(['Z', 'P']))]
        df_zp = zp_raw.groupby(['PRODUCT_CODE', 'TOOL_ID'])['COUNT'].agg('sum').to_frame(name='ZP')
        
        x_raw = raw_data2[(raw_data2['GRADE'].isin(['X']))]
        df_x = x_raw.groupby(['PRODUCT_CODE', 'TOOL_ID'])['COUNT'].agg('sum').to_frame(name='X')
        
        
    
        df_tot = raw_data2.groupby(['PRODUCT_CODE', 'TOOL_ID'])['COUNT'].agg('sum').to_frame(name='總數')
          
        
        # 合併表格
        octADCRBRej = pd.concat([df_zp, df_x, df_tot], verify_integrity = True, axis=1)
        octADCRBRej = octADCRBRej.fillna(0)
        
        octADCRBRej = octADCRBRej.reset_index()
        
        #octADCRBRej[['OGD', 'BPs', '空白', 'CP']] = octADCRBSuc[['OGD', 'BPs', '空白', 'CP']].astype('int')
    
        octADCRBRej['ZP(%)'] = 100*octADCRBRej['ZP'] / octADCRBRej['總數']
        octADCRBRej['X(%)'] = 100*octADCRBRej['X'] / octADCRBRej['總數']
        octADCRBRej['總(%)'] = octADCRBRej['ZP(%)'] + octADCRBRej['X(%)']
        octADCRBRej['REAL'] = 0
        octADCRBRej['Particle誤判'] = 0
        octADCRBRej['機台異常'] = 0
        octADCRBRej['邊緣誤判'] = 0
        octADCRBRej['其他請說明'] = 0
        octADCRBRej['待確認'] = octADCRBRej['X']
        
        
        
        
        
        table = 'oct_adcrbrej'
        db_data = mysql2df(table)
        
        for item in octADCRBRej.index:
            
            tool_id = octADCRBRej.loc[item]['TOOL_ID']
            pc = octADCRBRej.loc[item]['PRODUCT_CODE']
            tot = octADCRBRej.loc[item]['總數']
            
            raw_data1 = raw_data0[(raw_data0['TOOL_ID'] == tool_id) & (raw_data0['PRODUCT_CODE'] == pc)]
            db_data1 = db_data[(db_data['TOOL_ID']==tool_id) & (db_data['PRODUCT_CODE']==pc)]
            grades = ['X']
            octADCRBRejRaw = raw_data1[(raw_data0['GRADE'].isin(grades))].copy()
            
            
    
            
            # 紀錄查詢
            
            
            
            for i in octADCRBRejRaw.index:
                chipid = octADCRBRejRaw.loc[i]['CHIP_ID']
                date0 = str(octADCRBRejRaw.loc[i]['TEST_TIME'])
                date_oct = date0[0:4] + date0[5:7] + date0[8:10]
                eqp_oct = octADCRBRejRaw.loc[i]['TOOL_ID']
                oct_def = octADCRBRejRaw.loc[i]['DEFECT']
                
                #pre_test_user = octADCRBSuc.loc[i]['PRE_TEST_USER']
        
                
                #df0 = db_data[(db_data['CHIP_ID']==chipid) & (db_data['TOOL_ID']==eqp_oct) & (db_data['DEFECT']==oct_def)]
                df0 = db_data1[(db_data1['CHIP_ID']==chipid) & (db_data1['DEFECT']==oct_def)]
                if len(df0) > 0:
                    last_n = df0.index[-1]
                    #df0.drop_duplicates(['CHIP_ID', 'OCT_DEFECT'], keep='last', inplace=True)
                    okng = df0.loc[last_n]['Check']
                    #remarks = df0.loc[last_n]['name']+', '+df0.loc[last_n]['Remarks']
                    octADCRBRej.loc[item, '待確認'] = octADCRBRej.loc[item]['待確認'] - 1
                    if okng in ['REAL', 'Particle誤判', '機台異常', '邊緣誤判', '其他請說明']:
                        octADCRBRej.loc[item, okng] = octADCRBRej.loc[item][okng] + 1
                        #octADCRBSuc.loc[item, def_col+'確認(%)'] = octADCRBSuc.loc[item][def_col+'確認(%)'] - 1
            #octADCRBRej.loc[item, def_col+'確認(%)'] = 100*octADCRBSuc.loc[item][def_col+'確認(%)']/tot
            
            
       
        octADCRBRej = octADCRBRej.round(2)
        
    print(octADCRBRej)
    #octADCRBSuc = octADCRBSuc.astype('str')
    table = 'octADCRBRej'

    return render_template('userMain.html', user=str(user),name=name, auth=auth, shift=shift, sectShow=sectShow,
                           date1=date1, date2=date2, octADCRBRej= octADCRBRej)
    


def octADCRBRejRaw0(user, name, auth, shift, date1, date2, tool_id, pc, grade_col):
    
    sectShow = 'octADCRBRejRaw0'
    
    if grade_col == 'ZP':
        grades = ['Z', 'P']
    elif grade_col == 'X':
        grades = ['X']
    
    
    raw_data0 = adcRBRej(date1, date2)
    raw_data0 = raw_data0[(raw_data0['TOOL_ID'] == tool_id) & (raw_data0['PRODUCT_CODE'] == pc) & (raw_data0['GRADE'].isin(grades))]
    #print(raw_data0)
    if len(raw_data0) == 0:
        octADCRBRej = pd.DataFrame(columns =["該日期無資料"])
    else:
        #raw_data0.fillna({'DEFECT':'   '}, inplace=True)
        
        raw_data1 = raw_data0.groupby(['PRODUCT_CODE', 'TOOL_ID', 'GRADE', 'DEFECT'])
        raw_data2 = raw_data1.size().to_frame(name='片數')
        raw_data2.reset_index(inplace=True)
        
        """
        zp_raw = raw_data2[(raw_data2['GRADE'].isin(['Z', 'P']))]
        df_zp = zp_raw.groupby(['PRODUCT_CODE', 'TOOL_ID'])['COUNT'].agg('sum').to_frame(name='ZP')
        
        x_raw = raw_data2[(raw_data2['GRADE'].isin(['X']))]
        df_x = x_raw.groupby(['PRODUCT_CODE', 'TOOL_ID'])['COUNT'].agg('sum').to_frame(name='X')
        
        
    
        df_tot = raw_data2.groupby(['PRODUCT_CODE', 'TOOL_ID'])['COUNT'].agg('sum').to_frame(name='總數')
        
        
        # 合併表格
        octADCRBRej = pd.concat([df_zp, df_x, df_tot], verify_integrity = True, axis=1)
        """
        octADCRBRej = raw_data2.fillna(0)
        
        octADCRBRej.reset_index(drop=True, inplace=True)
        
        #octADCRBRej[['OGD', 'BPs', '空白', 'CP']] = octADCRBSuc[['OGD', 'BPs', '空白', 'CP']].astype('int')
    
        #octADCRBRej['ZP(%)'] = 100*octADCRBRej['ZP'] / octADCRBRej['總數']
        #octADCRBRej['X(%)'] = 100*octADCRBRej['X'] / octADCRBRej['總數']
        #octADCRBRej['總(%)'] = octADCRBRej['ZP(%)'] + octADCRBRej['X(%)']
        octADCRBRej['REAL'] = 0
        octADCRBRej['Particle誤判'] = 0
        octADCRBRej['機台異常'] = 0
        octADCRBRej['邊緣誤判'] = 0
        octADCRBRej['其他請說明'] = 0
        octADCRBRej['待確認'] = octADCRBRej['片數']
        
        
        table = 'oct_adcrbrej'
        db_data = mysql2df(table)
        db_data1 = db_data[(db_data['TOOL_ID'] == tool_id) & (db_data['PRODUCT_CODE'] == pc) & (db_data['GRADE'].isin(grades))]
  
        print(octADCRBRej)
        for item in octADCRBRej.index:
            defect0 = octADCRBRej.loc[item]['DEFECT']
            tool_id = octADCRBRej.loc[item]['TOOL_ID']
            pc = octADCRBRej.loc[item]['PRODUCT_CODE']
            #tot = octADCRBRej.loc[item]['總數']
            
            octADCRBRejRaw = raw_data0[(raw_data0['DEFECT'] == defect0)]
            

            # 紀錄查詢
            
            
            
            for i in octADCRBRejRaw.index:
                chipid = octADCRBRejRaw.loc[i]['CHIP_ID']
                date0 = str(octADCRBRejRaw.loc[i]['TEST_TIME'])
                date_oct = date0[0:4] + date0[5:7] + date0[8:10]
                eqp_oct = octADCRBRejRaw.loc[i]['TOOL_ID']
                oct_def = octADCRBRejRaw.loc[i]['DEFECT']
                
                #pre_test_user = octADCRBSuc.loc[i]['PRE_TEST_USER']
        
                
                #df0 = db_data[(db_data['CHIP_ID']==chipid) & (db_data['TOOL_ID']==eqp_oct) & (db_data['DEFECT']==oct_def)]
                df0 = db_data1[(db_data1['CHIP_ID']==chipid) & (db_data1['DEFECT']==oct_def)]
                if len(df0) > 0:
                    last_n = df0.index[-1]
                    #df0.drop_duplicates(['CHIP_ID', 'OCT_DEFECT'], keep='last', inplace=True)
                    okng = df0.loc[last_n]['Check']
                    #remarks = df0.loc[last_n]['name']+', '+df0.loc[last_n]['Remarks']
                    octADCRBRej.loc[item, '待確認'] = octADCRBRej.loc[item]['待確認'] - 1
                    if okng in ['REAL', 'Particle誤判', '機台異常', '邊緣誤判', '其他請說明']:
                        octADCRBRej.loc[item, okng] = octADCRBRej.loc[item][okng] + 1
                        #octADCRBSuc.loc[item, def_col+'確認(%)'] = octADCRBSuc.loc[item][def_col+'確認(%)'] - 1
            #octADCRBRej.loc[item, def_col+'確認(%)'] = 100*octADCRBSuc.loc[item][def_col+'確認(%)']/tot
            
            
        
    octADCRBRej = octADCRBRej.round(2)
    return render_template('userMain.html', user=str(user),name=name, auth=auth, shift=shift, sectShow=sectShow,
                       date1=date1, date2=date2, octADCRBRej= octADCRBRej)
    




def octADCRBRejRaw(user, name, auth, shift, date1, date2, tool_id, pc, grade_col, defect):
    print("octADCRBRejRaw第三層進入")
    sectShow = 'octADCRBRejRaw'
    
    raw_data0 = adcRBRej(date1, date2)
    if grade_col == 'ZP':
        grades = ['Z', 'P']
    elif grade_col == 'X':
        grades = ['X']
    
    filter0 = (raw_data0['GRADE'].isin(grades)) & (raw_data0['TOOL_ID'] == tool_id) & (raw_data0['PRODUCT_CODE'] == pc) & (raw_data0['DEFECT'] == defect)
    octADCRBRejRaw = raw_data0[filter0].copy()
    octADCRBRejRaw.reset_index(drop=True, inplace=True)
    #octADCRBRejRaw['IMG'] = 'NA'
    octADCRBRejRaw['確認'] = 'NA'
    octADCRBRejRaw['說明'] = 'NA'
    
    #df_aoi = pd.DataFrame()
    #df_adc = pd.DataFrame()
    df_aoi = octADCRBRejRaw[['CHIP_ID']]
    df_adc = octADCRBRejRaw[['CHIP_ID','DEFECT', '確認', '說明']]
    
    
    # 紀錄查詢
    table = 'oct_adcrbrej'
    db_data = mysql2df(table)
    
    
    for i in octADCRBRejRaw.index:
        chipid = octADCRBRejRaw.loc[i]['CHIP_ID']
        date0 = str(octADCRBRejRaw.loc[i]['TEST_TIME'])
        date_oct = date0[0:4] + date0[5:7] + date0[8:10]
        eqp_oct = octADCRBRejRaw.loc[i]['TOOL_ID']
        oct_def = octADCRBRejRaw.loc[i]['DEFECT']
        grade0 = octADCRBRejRaw.loc[i]['GRADE']
        #pre_test_user = octADCRBRej.loc[i]['PRE_TEST_USER']

        
        df0 = db_data[(db_data['CHIP_ID']==chipid) & (db_data['TOOL_ID']==eqp_oct) & (db_data['GRADE']==grade0)]
        if len(df0) > 0:
            last_n = df0.index[-1]
            #df0.drop_duplicates(['CHIP_ID', 'OCT_DEFECT'], keep='last', inplace=True)
            okng = df0.loc[last_n]['Check']
            remarks = df0.loc[last_n]['name']+', '+ str(df0.loc[last_n]['Remarks'])
            octADCRBRejRaw.loc[i, '確認'] = str(okng)
            octADCRBRejRaw.loc[i, '說明'] = str(remarks)
        df_adc.loc[i, '確認'] = octADCRBRejRaw.loc[i]['確認']
        df_adc.loc[i, '說明'] = octADCRBRejRaw.loc[i]['說明']
            
        octimgs = octDefectImg(chipid, date_oct, eqp_oct, oct_def)
        aoi_img = octimgs[0]
        adc_img = octimgs[1]
        img_html = ""
        # 合併原表格版本
        for img in adc_img:
            1
            #img_html += r"<a href='"+img+"'><img align='center' width='160' height='120' src='"+img+"'  ></a>"
        #octADCRBRejRaw.loc[i, 'IMG'] = img_html
        skip_n = 0
        df_record = pd.DataFrame(columns=['ptc', 'cx', 'cy'])
        for num0 in range(len(adc_img)):
            pattern= ""
            img_name = os.path.basename(adc_img[num0])
            spl = img_name.split('_')
            if spl[4] in ['R', 'G', 'B']:
                skip_n += 1
                continue
            ptc0 = spl[4]
            cx0 = spl[6]
            cy0 = spl[8]
            print(ptc0, cx0, cy0)
            df0 = df_record[(df_record['ptc'] == ptc0) & (abs(df_record['cx'] - 10) > 0) & (abs(df_record['cy'] - 5) > 0 )]
            if len(df0) > 0:
                skip_n += 1
                continue
            df_record.loc[num0, 'ptc'] = ptc0
            df_record.loc[num0, 'cx'] = int(cx0)
            df_record.loc[num0, 'cy'] = int(cy0)
            
            pattern = spl[3][1:]+'_'+spl[4] + '<br/>'
            df_adc.loc[i, 'IMG_'+str(num0-skip_n)] = pattern + r"<a href='"+adc_img[num0]+"'><img align='center' width='160' height='120' src='"+adc_img[num0]+"'  ></a>"
        
        
        
        
        #img_html = r"<img src='"+adc_img+"'  >"
        #"<a href='"+img_path+"'><img width='240' height='180' src='"+img_path+"' ></a>"
    
    #　如果無影像則改為空ＤＦ
    if len(df_adc.columns) == 1:
        1
        #df_adc = pd.DataFrame()
    #octaoi_list.append(octaoi_imgs)
    #octadc_list.append(octadc_imgs)
    octADCRBRejRaw.drop(columns=['MFG_DAY'], inplace=True)
    
    try:
        path000 = r'static/csv'
        if not os.path.exists(path000):
            os.mkdir(path000)
       
        btnName = list(request.form)[-1]
        filepath = r'static/csv/'+btnName+'.csv'
        octADCRBRejRaw.to_csv(filepath, index=False, encoding='utf-8-sig')
    except:
        print('csv儲存失敗:',filepath)
    
    
    #octADCRBRejRaw = octADCRBRejRaw.reset_index(drop=True)
    #print(octADCRBRejRaw)
    return render_template('userMain.html', user=str(user),name=name, auth=auth, shift=shift, sectShow=sectShow,
                           date1=date1, date2=date2, octADCRBRejRaw= octADCRBRejRaw, df_adc=df_adc)


def octADCRBRej_Upload(user,name, auth, shift, req_list):
    #返回第一層
    sectShow = 'octADCRBRej'
    #sectShow = 'uploadOK'
    
    #df_dp2bp = pd.DataFrame(columns=['user', 'name', 'shift', 'auth'])
    table = 'oct_adcrbrej'
    db_data = mysql2df(table)
    db_ADCRBRej = pd.DataFrame(columns=db_data.columns)
    #db_ADCRBRej = pd.DataFrame()
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
        if col in db_ADCRBRej.columns:
            db_ADCRBRej.loc[num, col] = req
        #　imgCheck'為每一個Ｉｄ的最後一項
    
    
    # 送出後回到第二層之參數
    pc = db_ADCRBRej.loc[db_ADCRBRej.index[-1]]['PRODUCT_CODE']
    grade_col = db_ADCRBRej.loc[db_ADCRBRej.index[-1]]['GRADE']
    tool_id = db_ADCRBRej.loc[db_ADCRBRej.index[-1]]['TOOL_ID']
    
    # 個別補上個人資訊
    user_list = ['user', 'name', 'shift', 'auth']
    drop_list = []
    for m in db_ADCRBRej.index:
        check0 = db_ADCRBRej.loc[m]['Check']
        if check0 == '---' or check0 is None or pd.isna(check0):
            drop_list.append(m)
        for ii in user_list:
            req = request.form.get(ii)
            db_ADCRBRej.loc[m, ii] = req
        db_ADCRBRej.loc[m, 'Checked_Date'] = now_hm
        
        # 新增MFG DATE轉換資訊
        #test_time = df_dp2bp.loc[newIdx+m]['TEST_TIME']
        #df_dp2bp.loc[newIdx+m,'TEST_TIME_MFG'] = testTime2MFG(str(test_time))
        
    db_ADCRBRej = db_ADCRBRej.drop(drop_list)
    db_ADCRBRej.reset_index(inplace=True, drop=True)
    #db_ADCRBSuc = db_ADCRBSuc.drop(columns=['Check'])
    #print(db_ADCRBRej)
    df2mysql_append(db_ADCRBRej, table)
    
    
    date1 = request.form.get('date1')
    date2 = request.form.get('date2')
    
    
    return octADCRBRejRaw0(user, name, auth, shift, date1, date2, tool_id, pc, grade_col)
    #return octADCRBRej(user,name, auth, shift, date1, date2)




def adcRBSamp(date1, date2):
    

    sql = r"select t.mfg_day,t.tool_id,t.test_time,t.product_code,t.tft_chip_id as chip_id, "
    sql += r" t.pre_Grade AS ADCRB_GRADE,t.pre_defect_code_desc AS ADCRB_DEFECT,t.grade as OCT_ADC_GRADE,"
    sql += r" t.defect_code_desc as OCT_ADC_DEFECT, t.test_user as OCT_ADC_TEST_USER, t.abbr_no as OCT_ADC_ABBR,"
    sql += r" b.grade as OP_GRADE, b.test_user as OP_USER, b.defect_value as OP_VALUE,b.defect_code_desc as OP_DEFECT"
    sql += r" from("
    sql += r" select *"
    sql += r" from celods.h_dax_fbk_test_ods"
    sql += r" where mfg_day between to_date('" + date1 + "','yyyy-mm-dd') and to_date('" + date2 + "','yyyy-mm-dd')"
    sql += r" and site_type='BEOL'"
    sql += r" and site_id='L11'"
    sql += r" and op_id='OCT2'"
    sql += r" and pre_grade in ('RB','RC')"
    sql += r" AND GRADE='Z'"
    sql += r" and test_user like 'CC%'"
    sql += r" and tool_id not in ('CCCTS300','CCCTSA00','CCOT300','CCOCT400')"
    sql += r" and tool_id not like 'DMYG2Z'"
    sql += r" )t"
    sql += r" left join celods.h_dax_fbk_test_ods b"
    sql += r" on t.tft_chip_id=b.tft_chip_id"
    sql += r" where b.test_user not like 'CC%'"
    sql += r" and b.mfg_day > (to_date('" + date1 + "','yyyy-mm-dd') - interval '60' day)"
    sql += r" and b.site_type='BEOL'"
    sql += r" and b.site_id='L11'"
    sql += r" and b.judge_cnt > t.judge_cnt"
    sql += r" and b.judge_cnt - t.judge_cnt =1"
    raw_data0 = ora2df(sql)
    return raw_data0

    
    
    
def octADCRBSamp(user,name, auth, shift, date1,date2):
    
    sectShow = 'octADCRBSamp'
    # Udefectq
    raw_data0 = adcRBSamp(date1, date2)
    #print(raw_data0)
    if len(raw_data0) == 0:
        octADCRBSamp = pd.DataFrame(columns =["該日期無資料"])
    else:
        #raw_data0.fillna({'DEFECT':'   '}, inplace=True)
        raw_data1 = raw_data0.groupby(['PRODUCT_CODE', 'TOOL_ID', 'OP_GRADE'])
        raw_data2 = raw_data1.size().to_frame(name='COUNT')
        raw_data2 = raw_data2.reset_index()
        
            
        #[`w
        zp_raw = raw_data2[(raw_data2['OP_GRADE'].isin(['Z', 'P']))]
        df_zp = zp_raw.groupby(['PRODUCT_CODE', 'TOOL_ID'])['COUNT'].agg('sum').to_frame(name='ZP')
        
        samp_raw = raw_data2[(~raw_data2['OP_GRADE'].isin(['Z', 'P']))]
        df_samp = samp_raw.groupby(['PRODUCT_CODE', 'TOOL_ID'])['COUNT'].agg('sum').to_frame(name='Sampling')
        
        
    
        df_tot = raw_data2.groupby(['PRODUCT_CODE', 'TOOL_ID'])['COUNT'].agg('sum').to_frame(name='總數')
          
        
        # X
        octADCRBSamp = pd.concat([df_samp, df_zp, df_tot], verify_integrity = True, axis=1)
        octADCRBSamp = octADCRBSamp.fillna(0)
        
        octADCRBSamp = octADCRBSamp.reset_index()
        
        #octADCRBSamp[['OGD', 'BPs', '', 'CP']] = octADCRBSuc[['OGD', 'BPs', '', 'CP']].astype('int')
        octADCRBSamp['Sampling(%)'] = 100*octADCRBSamp['Sampling'] / octADCRBSamp['總數']
        octADCRBSamp['ZP(%)'] = 100*octADCRBSamp['ZP'] / octADCRBSamp['總數']
        octADCRBSamp['總(%)'] = octADCRBSamp['ZP(%)'] + octADCRBSamp['Sampling(%)']
        octADCRBSamp['同點不可見'] = 0
        octADCRBSamp['新增點'] = 0
        octADCRBSamp['漏檢'] = 0
        octADCRBSamp['非相關位置Defect'] = 0
        octADCRBSamp['其他'] = 0
        octADCRBSamp['待確認'] = octADCRBSamp['Sampling']
        
        
        
        
        table = 'oct_adcrb_samp'
        db_data = mysql2df(table)
        
        for item in octADCRBSamp.index:
            
            tool_id = octADCRBSamp.loc[item]['TOOL_ID']
            pc = octADCRBSamp.loc[item]['PRODUCT_CODE']
            tot = octADCRBSamp.loc[item]['總數']
            
            raw_data1 = raw_data0[(raw_data0['TOOL_ID'] == tool_id) & (raw_data0['PRODUCT_CODE'] == pc)]
            db_data1 = db_data[(db_data['TOOL_ID']==tool_id) & (db_data['PRODUCT_CODE']==pc)]
            grades = ['Z', 'P']
            octADCRBSampRaw = raw_data1[(~raw_data0['OP_GRADE'].isin(grades))].copy()
            
            
    
            
            # d
            
            
            
            for i in octADCRBSampRaw.index:
                chipid = octADCRBSampRaw.loc[i]['CHIP_ID']
                date0 = str(octADCRBSampRaw.loc[i]['TEST_TIME'])
                date_oct = date0[0:4] + date0[5:7] + date0[8:10]
                eqp_oct = octADCRBSampRaw.loc[i]['TOOL_ID']
                oct_def = octADCRBSampRaw.loc[i]['OP_DEFECT']
                
                #pre_test_user = octADCRBSuc.loc[i]['PRE_TEST_USER']
        
                
                #df0 = db_data[(db_data['CHIP_ID']==chipid) & (db_data['TOOL_ID']==eqp_oct) & (db_data['DEFECT']==oct_def)]
                df0 = db_data1[(db_data1['CHIP_ID']==chipid) & (db_data1['OP_DEFECT']==oct_def)]
                if len(df0) > 0:
                    last_n = df0.index[-1]
                    #df0.drop_duplicates(['CHIP_ID', 'OCT_DEFECT'], keep='last', inplace=True)
                    okng = df0.loc[last_n]['Check']
                    #remarks = df0.loc[last_n]['name']+', '+df0.loc[last_n]['Remarks']
                    octADCRBSamp.loc[item, '待確認'] = octADCRBSamp.loc[item]['待確認'] - 1
                    if okng in ['同點不可見', '新增點', '漏檢', '非相關位置Defect', '其他']:
                        octADCRBSamp.loc[item, okng] = octADCRBSamp.loc[item][okng] + 1
                        #octADCRBSuc.loc[item, def_col+'T{(%)'] = octADCRBSuc.loc[item][def_col+'T{(%)'] - 1
            #octADCRBSamp.loc[item, def_col+'T{(%)'] = 100*octADCRBSuc.loc[item][def_col+'T{(%)']/tot
            
            
    
        octADCRBSamp = octADCRBSamp.round(2)
         
    
    #octADCRBSuc = octADCRBSuc.astype('str')
    table = 'octADCRBSamp'
    
    return render_template('userMain.html', user=str(user),name=name, auth=auth, shift=shift, sectShow=sectShow,
                           date1=date1, date2=date2, octADCRBSamp= octADCRBSamp)
    

def octADCRBSampRaw(user,name, auth, shift, date1, date2, tool_id, pc, grade_col):
    
    sectShow = 'octADCRBSampRaw'
    
    raw_data0 = adcRBSamp(date1, date2)
    if grade_col == 'Sampling':
        grades = ['Z', 'P']
    elif grade_col == 'X':
        grades = ['X']
    
    
    octADCRBSampRaw = raw_data0[(~raw_data0['OP_GRADE'].isin(grades)) & (raw_data0['TOOL_ID'] == tool_id) & (raw_data0['PRODUCT_CODE'] == pc)].copy()
    octADCRBSampRaw.reset_index(drop=True, inplace=True)
    #octADCRBSampRaw['IMG'] = 'NA'
    octADCRBSampRaw['確認'] = 'NA'
    octADCRBSampRaw['說明'] = 'NA'
    
    #df_aoi = pd.DataFrame()
    #df_adc = pd.DataFrame()
    df_aoi = octADCRBSampRaw[['CHIP_ID']]
    df_adc = octADCRBSampRaw[['CHIP_ID','OCT_ADC_DEFECT', '確認', '說明']]
    
    
    # d
    table = 'oct_adcrb_samp'
    
    db_data = mysql2df(table)
    
    
    for i in octADCRBSampRaw.index:
        chipid = octADCRBSampRaw.loc[i]['CHIP_ID']
        date0 = str(octADCRBSampRaw.loc[i]['TEST_TIME'])
        date_oct = date0[0:4] + date0[5:7] + date0[8:10]
        eqp_oct = octADCRBSampRaw.loc[i]['TOOL_ID']
        oct_def = octADCRBSampRaw.loc[i]['OP_DEFECT']
        grade0 = octADCRBSampRaw.loc[i]['OP_GRADE']
        #pre_test_user = octADCRBSamp.loc[i]['PRE_TEST_USER']

        
        df0 = db_data[(db_data['CHIP_ID']==chipid) & (db_data['TOOL_ID']==eqp_oct) & (db_data['OP_GRADE']==grade0)]
        if len(df0) > 0:
            last_n = df0.index[-1]
            #df0.drop_duplicates(['CHIP_ID', 'OCT_DEFECT'], keep='last', inplace=True)
            okng = df0.loc[last_n]['Check']
            remarks = df0.loc[last_n]['name']+', '+ str(df0.loc[last_n]['Remarks'])
            octADCRBSampRaw.loc[i, '確認'] = str(okng)
            octADCRBSampRaw.loc[i, '說明'] = str(remarks)
        df_adc.loc[i, '確認'] = octADCRBSampRaw.loc[i]['確認']
        df_adc.loc[i, '說明'] = octADCRBSampRaw.loc[i]['說明']

        
        octimgs = octDefectImg(chipid, date_oct, eqp_oct, oct_def)
        aoi_img = octimgs[0]
        adc_img = octimgs[1]
        img_html = ""
        # X
        for img in adc_img:
            1
            #img_html += r"<a href='"+img+"'><img align='center' width='160' height='120' src='"+img+"'  ></a>"
        #octADCRBSampRaw.loc[i, 'IMG'] = img_html
        
        skip_n = 0
        df_record = pd.DataFrame(columns=['ptc', 'cx', 'cy'])
        for num0 in range(len(adc_img)):
            pattern= ""
            img_name = os.path.basename(adc_img[num0])
            spl = img_name.split('_')
            if spl[4] in ['R', 'G', 'B']:
                skip_n += 1
                continue
            ptc0 = spl[4]
            cx0 = spl[6]
            cy0 = spl[8]
            print(ptc0, cx0, cy0)
            df0 = df_record[(df_record['ptc'] == ptc0) & (abs(df_record['cx'] - 10) > 0) & (abs(df_record['cy'] - 10) > 0 )]
            if len(df0) > 0:
                skip_n += 1
                continue
            df_record.loc[num0, 'ptc'] = ptc0
            df_record.loc[num0, 'cx'] = int(cx0)
            df_record.loc[num0, 'cy'] = int(cy0)
            
            pattern = spl[3][1:]+'_'+spl[4] + '<br/>'
            df_adc.loc[i, 'IMG_'+str(num0-skip_n)] = pattern + r"<a href='"+adc_img[num0]+"'><img align='center' width='160' height='120' src='"+adc_img[num0]+"'  ></a>"
        
        
        
        
        #img_html = r"<img src='"+adc_img+"'  >"
        #"<a href='"+img_path+"'><img width='240' height='180' src='"+img_path+"' ></a>"
    
    #@pGLvh
    if len(df_adc.columns) == 1:
        1
        #df_adc = pd.DataFrame()
    #octaoi_list.append(octaoi_imgs)
    #octadc_list.append(octadc_imgs)
    octADCRBSampRaw.drop(columns=['MFG_DAY'], inplace=True)
    
    try:
        path000 = r'static/csv'
        if not os.path.exists(path000):
            os.mkdir(path000)
        btnName = list(request.form)[-1]
        filepath = r'static/csv/'+btnName+'.csv'
        octADCRBSampRaw.to_csv(filepath, index=False, encoding='utf-8-sig')
    except:
        print('csv儲存失敗:',filepath)

    
    
    
    #octADCRBSampRaw = octADCRBSampRaw.reset_index(drop=True)
    #print(octADCRBSampRaw)
    return render_template('userMain.html', user=str(user),name=name, auth=auth, shift=shift, sectShow=sectShow,
                           date1=date1, date2=date2, octADCRBSampRaw= octADCRBSampRaw, df_adc=df_adc)


def octADCRBSamp_Upload(user,name, auth, shift, req_list):
    #^@h
    sectShow = 'octADCRBSamp'
    #sectShow = 'uploadOK'
    
    #df_dp2bp = pd.DataFrame(columns=['user', 'name', 'shift', 'auth'])
    table = 'oct_adcrb_samp'
    db_data = mysql2df(table)
    db_ADCRBSamp = pd.DataFrame(columns=db_data.columns)
    #db_ADCRBSamp = pd.DataFrame()
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
        if col in db_ADCRBSamp.columns:
            db_ADCRBSamp.loc[num, col] = req
            print(num, col,req )
        #@imgCheck'C@@
        1
    # OWHT
    user_list = ['user', 'name', 'shift', 'auth']
    drop_list = []
    for m in db_ADCRBSamp.index:
        check0 = db_ADCRBSamp.loc[m]['Check']
        if check0 == '---' or check0 is None or pd.isna(check0):
            drop_list.append(m)
            continue
        for ii in user_list:
            req = request.form.get(ii)
            db_ADCRBSamp.loc[m, ii] = req
        db_ADCRBSamp.loc[m, 'Checked_Date'] = now_hm
        
        # sWMFG DATET
        #test_time = df_dp2bp.loc[newIdx+m]['TEST_TIME']
        #df_dp2bp.loc[newIdx+m,'TEST_TIME_MFG'] = testTime2MFG(str(test_time))
        
    db_ADCRBSamp = db_ADCRBSamp.drop(drop_list)
    #db_ADCRBSamp.reset_index(inplace=True, drop=True)
    #db_ADCRBSuc = db_ADCRBSuc.drop(columns=['Check'])
    #print(db_ADCRBRej)
    df2mysql_append(db_ADCRBSamp, table)
    
    
    date1 = request.form.get('date1')
    date2 = request.form.get('date2')
    
    return octADCRBSamp(user,name, auth, shift, date1, date2)




def aoiGO(date1, date2):
    sql = r"select to_char(t.mfg_day,'yyyy-MM-dd') as mfg_day, to_char(t.test_time,'yyyy-MM-dd hh24:mi:ss') as test_time, t.tool_id, t.product_code, t.tft_chip_id as chip_id, t.pre_grade, t.grade,"
    sql += r" t.defect_code_desc as defect, t.test_user, t.pre_defect_code_desc as pre_defect, t.abbr_no, b.test_user as PRE_TEST_USER, t.judge_cnt,"
    
    
    
    sql += r" case "
    sql += r"  when (t.pre_grade like 'A') then 'RA'"
    sql += r"  when (t.pre_grade like 'B') then 'RB'"
    sql += r"  when (t.pre_grade like 'Q') then 'RQ'"
    sql += r"  when (t.pre_grade like 'M') then 'RM'"  
    sql += r"  when (t.pre_grade like 'C') then 'RC'"    
    sql += r"  when (t.pre_grade like 'K') then 'RK'"    
    sql += r"  when (t.pre_grade like 'G') and (t.abbr_no not like '%CNG%') and (t.abbr_no not like '%XXXX%') and  (t.abbr_no not like '%XCXX%') and (t.abbr_no not like '%XXRX%') and (t.abbr_no not like '%XCRX%') then 'RA(G)'"
    sql += r"  when (t.pre_grade like '3') and (t.abbr_no not like '%K%') and (t.abbr_no not like '%XXXX%') and  (t.abbr_no not like '%XCXX%') and (t.abbr_no not like '%XXRX%') and (t.abbr_no not like '%XCRX%') then 'ARK'"
    sql += r"  when (t.pre_grade in ('3','G','X','W')) and t.abbr_no like '%CNG%' or t.abbr_no like '%XXXX%' or t.abbr_no like '%XCXX%'or t.abbr_no like '%XXRX%' or t.abbr_no like '%XCRX%' then 'CNG'"
    sql += r"  when (t.pre_grade in ('X','W')) and (t.abbr_no not like '%CNG%') and (t.abbr_no not like '%XXXX%') and  (t.abbr_no not like '%XCXX%') and (t.abbr_no not like '%XXRX%') and (t.abbr_no not like '%XCRX%') then 'ADC X' "

    
    
    
    """
    sql += r" case when (t.pre_grade like 'G') and (t.abbr_no not like '%CNG%') and (t.abbr_no not like '%AOI%')and (t.abbr_no not like '%A') then 'CT1_G'"
    sql += r"      when (t.pre_grade like 'RA') and (t.abbr_no not like '%AOI%') then 'RA'"
    sql += r"      when (t.pre_grade like 'X') and (t.abbr_no not like '%CNG%') and (t.abbr_no not like '%A') then 'ADC X'"
    sql += r"      when  t.pre_grade like 'RQ'then 'RQ'"
    sql += r"      when  t.pre_grade like 'RM'then 'RM'"
    sql += r"      when  t.pre_grade like 'RB'then 'RB'"
    sql += r"      when  t.pre_grade like 'RC'then 'RC'"
    sql += r"      when  t.pre_grade like '3'then 'ARK'"
    sql += r"      when (t.pre_grade like 'RK') or (t.abbr_no not like '%K') then 'RK'"
    sql += r"      when (t.pre_grade like 'W') and (t.abbr_no not like '%CNG%') then 'CT1_W'"
    sql += r"      when (t.pre_grade in ('3','G','X','W') and t.abbr_no like '%CNG%') then 'CNG'"
    sql += r"      when ((t.pre_grade like 'G') and ((t.abbr_no like '%AOI%') or (t.abbr_no like '%A'))) then 'RA(G)'"
    """     
         
    sql += r"      else t.pre_grade"
    sql += r"      end as type_group"
    sql += r" from("
    sql += r" select *"
    sql += r" from celods.h_dax_fbk_test_ods"
    sql += r" where mfg_day between to_date('" + date1 + "','yyyy-mm-dd') and to_date('" + date2 + "','yyyy-mm-dd')"
    
    sql += r" and site_type='BEOL'"
    sql += r" and site_id='L11'"
    sql += r" and op_id='OCT2'"
    sql += r" and pre_grade in ('RB','RC','G','RA','X','RK','W','RQ','RM','3','RA')"
    sql += r" and test_user like 'CC%'"
    sql += r" and tool_id in ('CCCTS300','CCCTSA00','CCOT300','CCOCT400')"     
    sql += r" and tool_id not like 'DMYG2Z'"
    sql += r" )t"
    sql += r" left join celods.h_dax_fbk_test_ods b on t.tft_chip_id=b.tft_chip_id"
    sql += r" and b.judge_cnt < t.judge_cnt"
    sql += r" and t.judge_cnt - b.judge_cnt =1"
    sql += r" and b.op_id in ('OCT1', 'OCT2')"
    sql += r" and b.mfg_day > (to_date('" + date1 + "','yyyy-mm-dd') - interval '90' day)"
    raw_data0 = ora2df(sql)
    if len(raw_data0) > 0:
        raw_data0.drop_duplicates(['CHIP_ID'], keep='last', inplace=True)
    return raw_data0



def rightKill(date1, date2):
    sql = r"select to_char(t.mfg_day,'yyyy-MM-dd') as mfg_day, t.tool_id, t.test_time,"
    sql += r" t.product_code, t.tft_chip_id as chip_id, t.grade as AOI_GRADE,"
    sql += r" t.defect_code_desc as AOI_DEFECT, "
    sql += r" t.test_user as AOI_TEST_USER, t.pre_Grade AS CT1_GRADE,"
    sql += r" t.pre_defect_code_desc AS CT1_DEFECT, t.abbr_no,"
    sql += r" b.grade as OP_GRADE, b.test_user as OP_USER,"
    sql += r" b.defect_value as OP_VALUE, b.defect_code_desc as OP_DEFECT,"
    
    
    
    # 新case調整
    sql += r" case "
    sql += r"  when (t.pre_grade like 'A') then 'RA'"
    sql += r"  when (t.pre_grade like 'B') then 'RB'"
    sql += r"  when (t.pre_grade like 'Q') then 'RQ'"
    sql += r"  when (t.pre_grade like 'M') then 'RM'"  
    sql += r"  when (t.pre_grade like 'C') then 'RC'"    
    sql += r"  when (t.pre_grade like 'K') then 'RK'"    
    sql += r"  when (t.pre_grade like 'G') and (t.abbr_no not like '%CNG%') and (t.abbr_no not like '%XXXX%') and  (t.abbr_no not like '%XCXX%') and (t.abbr_no not like '%XXRX%') and (t.abbr_no not like '%XCRX%') then 'RA(G)'"
    sql += r"  when (t.pre_grade like '3') and (t.abbr_no not like '%K%') and (t.abbr_no not like '%XXXX%') and  (t.abbr_no not like '%XCXX%') and (t.abbr_no not like '%XXRX%') and (t.abbr_no not like '%XCRX%') then 'ARK'"
    sql += r"  when (t.pre_grade in ('3','G','X','W')) and t.abbr_no like '%CNG%' or t.abbr_no like '%XXXX%' or t.abbr_no like '%XCXX%'or t.abbr_no like '%XXRX%' or t.abbr_no like '%XCRX%' then 'CNG'"
    sql += r"  when (t.pre_grade in ('X','W')) and (t.abbr_no not like '%CNG%') and (t.abbr_no not like '%XXXX%') and  (t.abbr_no not like '%XCXX%') and (t.abbr_no not like '%XXRX%') and (t.abbr_no not like '%XCRX%') then 'ADC X' "

    
    
    
    """
    sql += r" case when (t.pre_grade like 'G') and (t.abbr_no not like '%CNG%') and (t.abbr_no not like '%AOI%')and (t.abbr_no not like '%A') then 'CT1_G'"
    sql += r"      when (t.pre_grade like 'RA') and (t.abbr_no not like '%AOI%') then 'RA'"
    sql += r"      when (t.pre_grade like 'X') and (t.abbr_no not like '%CNG%') and (t.abbr_no not like '%A') then 'ADC X'"
    sql += r"      when  t.pre_grade like 'RQ'then 'RQ'"
    sql += r"      when  t.pre_grade like 'RM'then 'RM'"
    sql += r"      when  t.pre_grade like 'RB'then 'RB'"
    sql += r"      when  t.pre_grade like 'RC'then 'RC'"
    sql += r"      when  t.pre_grade like '3'then 'ARK'"
    sql += r"      when (t.pre_grade like 'RK') or (t.abbr_no not like '%K') then 'RK'"
    sql += r"      when (t.pre_grade like 'W') and (t.abbr_no not like '%CNG%') then 'CT1_W'"
    sql += r"      when (t.pre_grade in ('3','G','X','W') and t.abbr_no like '%CNG%') then 'CNG'"
    sql += r"      when ((t.pre_grade like 'G') and ((t.abbr_no like '%AOI%') or (t.abbr_no like '%A'))) then 'RA(G)'"
    """
     
    
    
    sql += r"      else t.pre_grade"
    sql += r"      end as type_group"
    sql += r" from("
    sql += r" select *"
    sql += r" from celods.h_dax_fbk_test_ods"
    sql += r" where mfg_day between to_date('" + date1 + "','yyyy-mm-dd') and to_date('" + date2 + "','yyyy-mm-dd')"
    sql += r" and site_type='BEOL'"
    sql += r" and site_id='L11'"
    sql += r" and op_id='OCT2'"
    sql += r" and pre_grade in ('RB','RC','G','RA','X','RK','W','RQ','RM','3','RA')"
    sql += r" and grade not in ('G','Z','P')"
    sql += r" and test_user like 'CC%'"
    sql += r" and tool_id in ('CCCTS300','CCCTSA00','CCOT300','CCOCT400')"
    sql += r" and tool_id not like 'DMYG2Z'"
    sql += r" )t"
    sql += r" left join celods.h_dax_fbk_test_ods b on t.tft_chip_id=b.tft_chip_id"
    sql += r" where b.test_user not like 'CC%'"
    sql += r" and b.site_type='BEOL'"
    sql += r" and b.site_id='L11'"
    sql += r" and b.judge_cnt > t.judge_cnt"
    sql += r" and b.judge_cnt - t.judge_cnt =1"
    #sql += r" and b.mfg_day > (to_date('" + date1 + "','yyyy-mm-dd') - interval '90' day)"
    raw_data0 = ora2df(sql)
    if len(raw_data0) > 0:
        raw_data0.drop_duplicates(['CHIP_ID'], keep='last', inplace=True)
    return raw_data0

    
    

def octAOIGO(user,name, auth, shift, date1,date2):
    
    sectShow = 'octAOIGO'
    
    
    
    raw_data0 = aoiGO(date1, date2)
    
    if len(raw_data0) == 0:
        table = 'octAOIGO'
        return render_template('userMain.html', user=str(user),name=name, auth=auth, shift=shift, sectShow=sectShow,
                               date1=date1, date2=date2, octAOIGO= raw_data0)
        
    #raw_data0.fillna({'DEFECT':'   '}, inplace=True)
    raw_data0['isG'] = 'N'
    raw_data0.loc[raw_data0['GRADE'].isin(['Z', 'P']), 'isG'] = 'Y'
    raw_data1 = raw_data0.groupby(['TYPE_GROUP', 'MFG_DAY', 'TOOL_ID','isG'])
    raw_data2 = raw_data1.size().to_frame(name='COUNT')
    raw_data2 = raw_data2.astype(int)
    raw_data2 = raw_data2.reset_index()
    
    
    
    # Right kill data  AOI判X => 人檢Z, P
    rk_data0 = rightKill(date1, date2)
    rk_data1 = rk_data0.groupby(['TYPE_GROUP', 'MFG_DAY', 'TOOL_ID', 'OP_GRADE']).size().to_frame(name='COUNT')
    rk_data1.reset_index(inplace=True)
    print(rk_data1)
    
    #加總指定ｄｅｆｅｃｔ
    g_raw = raw_data2[(raw_data2['isG']=='Y')]
    df_g = g_raw.groupby(['TYPE_GROUP', 'MFG_DAY', 'TOOL_ID'])['COUNT'].agg('sum').to_frame(name='GO')
   
    ng_raw = raw_data2[(raw_data2['isG']=='N')]
    df_ng = ng_raw.groupby(['TYPE_GROUP', 'MFG_DAY', 'TOOL_ID'])['COUNT'].agg('sum').to_frame(name='NO_GO')
    
      
    df_tot = raw_data2.groupby(['TYPE_GROUP', 'MFG_DAY', 'TOOL_ID'])['COUNT'].agg('sum').to_frame(name='總數')
    
    nonzp_rkraw = rk_data1[~(rk_data1['OP_GRADE'].isin(['Z', 'P', 'G']))]
    df_rknonzp = nonzp_rkraw.groupby(['TYPE_GROUP', 'MFG_DAY', 'TOOL_ID'])['COUNT'].agg('sum').to_frame(name='Right_Kill')


    df_rktot = rk_data1.groupby(['TYPE_GROUP', 'MFG_DAY', 'TOOL_ID'])['COUNT'].agg('sum').to_frame(name='RK總數')
    # 合併表格
    octAOIGO = pd.concat([df_g, df_ng, df_tot, df_rknonzp, df_rktot], verify_integrity = True, axis=1)
    
    octAOIGO = octAOIGO.fillna(0)
    octAOIGO = octAOIGO.reset_index()
    
    octAOIGO['GOLD_RATIO(%)'] = 100*octAOIGO['GO'] / octAOIGO['總數']
    octAOIGO['Right_Kill(%)'] = 100*octAOIGO['Right_Kill'] / octAOIGO['RK總數']
    
    #octAOIGO.loc[octAOIGO['Right_Kill'] == 0 , 'Right_Kill(%)'] = 'N/A'
    """
    table = 'oct_adcrbsuc'
    db_data = mysql2df(table)

    for item in octAOIGO.index:
        
        tool_id = octAOIGO.loc[item]['TOOL_ID']
        pc = octAOIGO.loc[item]['PRODUCT_CODE']
        tot = octAOIGO.loc[item]['總數']
        
        raw_data1 = raw_data0[(raw_data0['TOOL_ID'] == tool_id) & (raw_data0['PRODUCT_CODE'] == pc)]
        db_data1 = db_data[(db_data['TOOL_ID']==tool_id) & (db_data['PRODUCT_CODE']==pc)]
        
        
        for def_col in ['OGD', '空白', 'CP']:
            
            if def_col == 'BPs':
                defect = 'BP'
            elif def_col == 'OGD':
                defect = 'OTHER GLASS DEFECT'
            elif def_col == '空白':
                defect = '   '
            elif def_col == 'CP':
                defect = 'CELL PARTICLE'

            #octAOIGORaw = raw_data0[(raw_data0['DEFECT'].str.contains(defect)) & (raw_data0['TOOL_ID'] == tool_id) & (raw_data0['PRODUCT_CODE'] == pc)]
            octAOIGORaw = raw_data1[(raw_data1['DEFECT'].str.contains(defect))]
            # 紀錄查詢
            
            #db_data = db_data[(db_data['TOOL_ID']==tool_id) & (db_data['PRODUCT_CODE']==pc) & (db_data['DEFECT'].str.contains(defect))]
            
            for i in octAOIGORaw.index:
                chipid = octAOIGORaw.loc[i]['CHIP_ID']
                date0 = str(octAOIGORaw.loc[i]['TEST_TIME'])
                date_oct = date0[0:4] + date0[5:7] + date0[8:10]
                eqp_oct = octAOIGORaw.loc[i]['TOOL_ID']
                oct_def = octAOIGORaw.loc[i]['DEFECT']
                
                #pre_test_user = octAOIGO.loc[i]['PRE_TEST_USER']
        
                
                #df0 = db_data[(db_data['CHIP_ID']==chipid) & (db_data['TOOL_ID']==eqp_oct) & (db_data['DEFECT']==oct_def)]
                df0 = db_data1[(db_data1['CHIP_ID']==chipid) & (db_data1['DEFECT']==oct_def)]
                if len(df0) > 0:
                    last_n = df0.index[-1]
                    #df0.drop_duplicates(['CHIP_ID', 'OCT_DEFECT'], keep='last', inplace=True)
                    okng = df0.loc[last_n]['Check']
                    #remarks = df0.loc[last_n]['name']+', '+df0.loc[last_n]['Remarks']
                    octAOIGO.loc[item, def_col+'確認'] = octAOIGO.loc[item][def_col+'確認'] + 1
                    if okng in ['Real', '多顆']:
                        
                        octAOIGO.loc[item, def_col+'確認(%)'] = octAOIGO.loc[item][def_col+'確認(%)'] - 1
            octAOIGO.loc[item, def_col+'確認(%)'] = 100*octAOIGO.loc[item][def_col+'確認(%)']/tot
    """
            
            
     
       
    octAOIGO = octAOIGO.round(2)
    octAOIGO[['GO', 'NO_GO', 'Right_Kill']] = octAOIGO[['GO', 'NO_GO', 'Right_Kill']].astype(int)
        
    print(octAOIGO)
    #octAOIGO = octAOIGO.astype('str')
    table = 'octAOIGO'

    return render_template('userMain.html', user=str(user),name=name, auth=auth, shift=shift, sectShow=sectShow,
                           date1=date1, date2=date2, octAOIGO= octAOIGO)
    
def octAOIRKRaw1(user,name, auth, shift, g_type, mfg_day, tool_id):

    sectShow = 'octAOIRKRaw1'
    raw_data0 = rightKill(mfg_day, mfg_day)
    
    
    filter0 = (raw_data0['TYPE_GROUP'] == g_type) & (raw_data0['TOOL_ID'] == tool_id) 
    #filter0 = filter0 & (raw_data0['TOOL_ID'] == tool_id) & (True) 
   # filter0 = filter0 & (raw_data0['DEFECT'] == defect)

    octAOIRKRaw1 = raw_data0[filter0]
    

    df_aoi = pd.DataFrame()
    
    #octAOIGORaw2['確認'] = 'N/A'
    #octAOIGORaw2['說明'] = 'N/A'
    #octAOIGORaw2 = octAOIGORaw2.assign(確認="NA",說明='NA')
    return render_template('userMain.html', user=str(user),name=name, auth=auth, shift=shift, sectShow=sectShow,
                           octAOIRKRaw1= octAOIRKRaw1)



def octAOIGORaw1(user,name, auth, shift, g_type, mfg_day, tool_id):
    
    sectShow = 'octAOIGORaw1'
    raw_data0 = aoiGO(mfg_day, mfg_day)
    raw_data0 = raw_data0[ (raw_data0['TYPE_GROUP'] == g_type) & (raw_data0['TOOL_ID'] == tool_id)]
    #raw_data0.fillna({'DEFECT':'   '}, inplace=True)
    raw_data0['isG'] = 'NO_GO'
    raw_data0.loc[raw_data0['GRADE'].isin(['Z', 'P']), 'isG'] = 'GO'
    raw_data1 = raw_data0.groupby(['TYPE_GROUP', 'MFG_DAY', 'TOOL_ID','isG', 'DEFECT'])
    raw_data2 = raw_data1.size().to_frame(name='片數')
    raw_data2 = raw_data2.astype(int)
    raw_data2.sort_values(["isG","片數"],ascending= False, inplace=True)
    raw_data2 = raw_data2.reset_index()
    
    octAOIGORaw1 = raw_data2.copy()
    tot0 = len(raw_data0)
    octAOIGORaw1["RATIO"] = 100*octAOIGORaw1['片數'] / tot0
    octAOIGORaw1['Real(CT1相關)'] = 0
    octAOIGORaw1 = octAOIGORaw1.assign(Real=0, 髒汙汙判=0, 機台異常=0, 其他請說明=0)
    octAOIGORaw1['未確認'] = octAOIGORaw1['片數'].copy()
    
    
    octAOIGORaw1['ROW_CNT'] = 1
    if len(octAOIGORaw1) > 0:
        start_idx = 0
        gold0 = octAOIGORaw1.loc[0]['isG']
    for idx in octAOIGORaw1.index[1:]:
        next_gold0 = octAOIGORaw1.loc[idx]['isG']
        if gold0 == next_gold0:
            octAOIGORaw1.loc[start_idx, 'ROW_CNT'] = octAOIGORaw1.loc[start_idx]['ROW_CNT'] + 1
            octAOIGORaw1.loc[idx, 'ROW_CNT'] = -1
        else:
            start_idx = idx
            gold0 = next_gold0
    
   
    table = 'oct_aoigo'
    db_data = mysql2df(table)
    db_data1 = db_data[(db_data['TYPE_GROUP']==g_type) & (db_data['TOOL_ID']==tool_id)]
    for item in octAOIGORaw1.index:
        defect0 = octAOIGORaw1.loc[item]['DEFECT']
        isG0 = octAOIGORaw1.loc[item]['isG']
        
        raw_data1 = raw_data0[(raw_data0['DEFECT'] == defect0) & (raw_data0['isG']==isG0)]
        
        
        
        
        
        
        if isG0 == 'GO':
            df0 = db_data1[(db_data1['DEFECT'] == defect0) & (db_data1['GRADE'].isin(['Z', 'P']))]
        elif isG0 == 'NO_GO':
            df0 = db_data1[(db_data1['DEFECT']==defect0) & (~raw_data0['GRADE'].isin(['Z', 'P']))]
        else:
            continue
        
        df0.drop_duplicates(['CHIP_ID', 'PRE_TEST_USER'], inplace=True)
        if len(df0) > 0:
            for idx0 in df0.index:  
                okng = df0.loc[idx0]['Check']
                if okng in ['Real', 'Real(CT1相關)', '髒汙汙判', '機台異常', '其他請說明']:
                    octAOIGORaw1.loc[item, okng] = octAOIGORaw1.loc[item][okng] + 1
                    octAOIGORaw1.loc[item, '未確認'] = octAOIGORaw1.loc[item]['未確認'] - 1
            
        #系統自動帶入
        if 1:
            for idx0 in raw_data1.index:
                jug_cnt0 = raw_data1.loc[idx0]['JUDGE_CNT']
                chipid = raw_data1.loc[idx0]['CHIP_ID']
                oct_def = defect0
                sql = r"select t.tft_chip_id, t.test_signal_no as x, t.test_gate_no as y, t.major_defect_flag, t.test_tool_id, "
                sql += r" t.test_op_id, t.test_time, t.test_user, t.test_judge_cnt, t.defect_code_desc as defect  "
                sql += r" from celods.h_dax_fbk_defect_ods t "
                sql += r" where t.tft_chip_id = '"+ chipid +"'"
                sql += r"and t.test_op_id in ('CGL') "
                #sql += r" and t.test_op_id='CGL' or "
                #sql += r" ( t.test_judge_cnt in ('" + str(jug_cnt0) + "') and t.major_defect_flag = 'Y' and t.defect_code_desc='" + oct_def + "') "
                sql += r" order by t.test_time "
                df0_ct1 = ora2df(sql)
                
                
                sql = r"select t.tft_chip_id, t.test_signal_no as x, t.test_gate_no as y, t.major_defect_flag, t.test_tool_id, "
                sql += r" t.test_op_id, t.test_time, t.test_user, t.test_judge_cnt, t.defect_code_desc as defect "
                sql += r" from celods.h_dax_fbk_defect_ods t "
                sql += r" where t.test_op_id in ( 'OCT1', 'OCT2') "
                sql += r" and t.tft_chip_id = '"+ chipid +"'"
                sql += r" and t.major_defect_flag = 'Y'"
                sql += r" and t.test_judge_cnt in ('" + str(jug_cnt0) + "')" 
                sql += r" and t.defect_code_desc='" + oct_def + "' "
                sql += r" order by t.test_time "
                df0_oct = ora2df(sql)
                #df0_oct = df_ct1XY[~filter0]
                #df0_ct1 = df_ct1XY[filter0]
                
                for idx0 in df0_oct.index:
                    x0 = df0_oct.loc[idx0]['X']
                    y0 = df0_oct.loc[idx0]['Y']
                    #print('CT1找相近座標')
                    # CT1 座標相近則自動帶入 (可能沒進CT1  卡控IF)
                    if len(df0_ct1) > 0:
                        df0 = df0_ct1[(abs(df0_ct1['X'] - x0) < 30) & (abs(df0_ct1['Y'] - y0) < 30)]
                        if 'BP' in oct_def:
                            df1 = df0[df0['DEFECT'].str.contains('BP')]
                        elif 'DP' in oct_def:
                            df1 = df0[df0['DEFECT'].str.contains('DP')]
                        else:
                            df1 = df0[df0['DEFECT'].str.contains(oct_def)]
                        if len(df1) > 0:
                            okng = 'Real(CT1相關)'
                            print(oct_def, '系統帶入')
                            octAOIGORaw1.loc[item, okng] = octAOIGORaw1.loc[item][okng] + 1
                            octAOIGORaw1.loc[item, '未確認'] = octAOIGORaw1.loc[item]['未確認'] - 1
        
        
        
    octAOIGORaw1 = octAOIGORaw1.round(2)
    #octAOIGORaw1[['COUNT']] = octAOIGORaw1[['COUNT']].astype(int)
    return render_template('userMain.html', user=str(user),name=name, auth=auth, shift=shift, sectShow=sectShow,
                           octAOIGORaw1= octAOIGORaw1)
def octAOIGORaw2(user,name, auth, shift, g_type, mfg_day, tool_id, isG, defect):
    sectShow = 'octAOIGORaw2'
    raw_data0 = aoiGO(mfg_day, mfg_day)
    grades = ['Z', 'P']
    if isG:
        filter0 = (raw_data0['TYPE_GROUP'] == g_type) & (raw_data0['TOOL_ID'] == tool_id) 
        filter0 = filter0 & (raw_data0['TOOL_ID'] == tool_id) & (raw_data0['GRADE'].isin(grades)) 
        filter0 = filter0 & (raw_data0['DEFECT'] == defect)
    else:
        filter0 = (raw_data0['TYPE_GROUP'] == g_type) & (raw_data0['TOOL_ID'] == tool_id) 
        filter0 = filter0 & (raw_data0['TOOL_ID'] == tool_id) & (~raw_data0['GRADE'].isin(grades)) 
        filter0 = filter0 & (raw_data0['DEFECT'] == defect)
        
    octAOIGORaw2 = raw_data0[filter0]
    

    df_aoi = pd.DataFrame()
    
    #octAOIGORaw2['確認'] = 'N/A'
    #octAOIGORaw2['說明'] = 'N/A'
    octAOIGORaw2 = octAOIGORaw2.assign(確認="NA",說明='NA')
    
    # 紀錄查詢
    table = 'oct_aoigo'
    db_data = mysql2df(table)
    octAOIGORaw2.reset_index(drop=True, inplace=True)
    df_aoi = octAOIGORaw2[['CHIP_ID','DEFECT', '確認', '說明']].copy()
    for i in octAOIGORaw2.index:
        chipid = octAOIGORaw2.loc[i]['CHIP_ID']
        date0 = str(octAOIGORaw2.loc[i]['TEST_TIME'])
        date_oct = date0[0:4] + date0[5:7] + date0[8:10]
        eqp_oct = octAOIGORaw2.loc[i]['TOOL_ID']
        oct_def = octAOIGORaw2.loc[i]['DEFECT']
        jug_cnt0 = octAOIGORaw2.loc[i]['JUDGE_CNT']
        #pre_test_user = octADCRBSuc.loc[i]['PRE_TEST_USER']
        # 若CT1坐標相近 且DEFECT相同  自動帶入"REAL(CT1相關)"
        #系統自動帶入
        sql = r"select t.tft_chip_id, t.test_signal_no as x, t.test_gate_no as y, t.major_defect_flag, t.test_tool_id, "
        sql += r" t.test_op_id, t.test_time, t.test_user, t.test_judge_cnt, t.defect_code_desc as defect  "
        sql += r" from celods.h_dax_fbk_defect_ods t "
        sql += r" where t.tft_chip_id = '"+ chipid +"'"
        sql += r"and t.test_op_id in ('CGL') "
        #sql += r" and t.test_op_id='CGL' or "
        #sql += r" ( t.test_judge_cnt in ('" + str(jug_cnt0) + "') and t.major_defect_flag = 'Y' and t.defect_code_desc='" + oct_def + "') "
        sql += r" order by t.test_time "
        df0_ct1 = ora2df(sql)
        #df_ct1XY = ora2df(sql)
        #filter0 = (df_ct1XY['TEST_OP_ID'] == 'CGL')
        
        
        sql = r"select t.tft_chip_id, t.test_signal_no as x, t.test_gate_no as y, t.major_defect_flag, t.test_tool_id, "
        sql += r" t.test_op_id, t.test_time, t.test_user, t.test_judge_cnt, t.defect_code_desc as defect "
        sql += r" from celods.h_dax_fbk_defect_ods t "
        sql += r" where t.test_op_id in ( 'OCT1', 'OCT2') "
        sql += r" and t.tft_chip_id = '"+ chipid +"'"
        sql += r" and t.major_defect_flag = 'Y'"
        sql += r" and t.test_judge_cnt in ('" + str(jug_cnt0) + "')" 
        sql += r" and t.defect_code_desc='" + oct_def + "' "
        sql += r" order by t.test_time "
        df0_oct = ora2df(sql)
        #df0_oct = df_ct1XY[~filter0]
        #df0_ct1 = df_ct1XY[filter0]
        
            
        isCT1R = False
        for idx0 in df0_oct.index:
            x0 = df0_oct.loc[idx0]['X']
            y0 = df0_oct.loc[idx0]['Y']
            #print('CT1找相近座標')
            # CT1 座標相近則自動帶入 (可能沒進CT1  卡控IF)
            if len(df0_ct1) > 0:
                df0 = df0_ct1[(abs(df0_ct1['X'] - x0) < 30) & (abs(df0_ct1['Y'] - y0) < 30)]
                if 'BP' in oct_def:
                    df1 = df0[df0['DEFECT'].str.contains('BP')]
                elif 'DP' in oct_def:
                    df1 = df0[df0['DEFECT'].str.contains('DP')]
                else:
                    df1 = df0[df0['DEFECT'].str.contains(oct_def)]
                if len(df1) > 0:
                    octAOIGORaw2.loc[i, '確認'] = 'Real(CT1相關)'
                    octAOIGORaw2.loc[i, '說明'] = '系統帶入'
                    isCT1R = True
        #mfg_day
        
        
        df0 = db_data[(db_data['CHIP_ID']==chipid) & (db_data['TOOL_ID']==eqp_oct) & (db_data['DEFECT']==oct_def)].copy()
        if len(df0) > 0:
            last_n = df0.index[-1]
            #df0.drop_duplicates(['CHIP_ID', 'OCT_DEFECT'], keep='last', inplace=True)
            okng = df0.loc[last_n]['Check']
            remarks = df0.loc[last_n]['name']+', '+str(df0.loc[last_n]['Remarks'])
            octAOIGORaw2.loc[i, '確認'] = str(okng)
            octAOIGORaw2.loc[i, '說明'] = str(remarks)
        
        df_aoi.loc[i, '確認'] = octAOIGORaw2.loc[i]['確認']
        df_aoi.loc[i, '說明'] = octAOIGORaw2.loc[i]['說明']
        print('OCT找圖:', chipid, date_oct, eqp_oct, oct_def)
        if not isCT1R:
            octimgs = octDefectImg(chipid, date_oct, eqp_oct, oct_def)
            aoi_img = octimgs[0]
            skip_n = 0
            for num0 in range(len(aoi_img)):
                pattern= "AOI IMG"
                img_name = os.path.basename(aoi_img[num0])
                spl = img_name.split('_')
                try:
                    if spl[3][1:] in ['M', 'F']:
                        pattern = spl[3][1:]+'_'+spl[4] 
                        
                    else:
                        pattern = spl[2][1:]+'_'+spl[3] 
                        #pattern = spl[3][1:]+'_'+spl[4]
                except:
                    1
                if aoi_img[num0][-4:] == '.tif':
                    df_aoi.loc[i, 'IMG_'+str(num0-skip_n)] = "<a href=\""+aoi_img[num0]+"\">"+pattern+"</a>"
                else:
                    # <img align="center" width='160' height='120' src="{{ value[i] }}" ></a>  
                    df_aoi.loc[i, 'IMG_'+str(num0-skip_n)] = "<a href=\"javascript:PopupPic('"+aoi_img[num0]+"')\">"+pattern+"</a>"
                   

    try:
        path000 = r'static/csv'
        if not os.path.exists(path000):
            os.mkdir(path000)
        btnName = list(request.form)[-1]
        btnName_val = request.form.get(btnName)
        filepath = r'static/csv/'+btnName+'__'+btnName_val+'.csv'
        octAOIGORaw2.to_csv(filepath, index=False, encoding='utf-8-sig')
    except:
        print('csv儲存失敗:',filepath)
        
    return render_template('userMain.html', user=str(user),name=name, auth=auth, shift=shift, sectShow=sectShow,
                           octAOIGORaw2= octAOIGORaw2, df_aoi=df_aoi)
    
def octAOIGO_Upload(user,name, auth, shift, req_list):
    #sectShow = 'uploadOK'
    
    #df_dp2bp = pd.DataFrame(columns=['user', 'name', 'shift', 'auth'])
    table = 'oct_aoigo'
    db_data = mysql2df(table)
    db_octAOIGO = pd.DataFrame(columns=db_data.columns)
    #db_octAOIGO = pd.DataFrame()
    
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
        if col in db_octAOIGO.columns or col in ['Check2', 'Remarks2']:
            db_octAOIGO.loc[num, col] = req
        #　imgCheck'為每一個Ｉｄ的最後一項
    
    # 下方選單將覆蓋上方
    cond0 = ~( (db_octAOIGO['Check2'].isin(['---'])) | (db_octAOIGO['Check2'].isnull()) )
    db_octAOIGO.loc[cond0, 'Check'] = db_octAOIGO.loc[cond0]['Check2']
    
    db_octAOIGO.loc[cond0, 'Remarks'] = db_octAOIGO.loc[cond0]['Remarks2']
    
    # 個別補上個人資訊
    user_list = ['user', 'name', 'shift', 'auth']
    drop_list = []
    for m in db_octAOIGO.index:
        check0 = db_octAOIGO.loc[m]['Check']
        if check0 == '---' or check0 is None or pd.isna(check0):
            drop_list.append(m)
        for ii in user_list:
            req = request.form.get(ii)
            db_octAOIGO.loc[m, ii] = req
        db_octAOIGO.loc[m, 'Checked_Date'] = now_hm
        
        # 新增MFG DATE轉換資訊
        #test_time = df_dp2bp.loc[newIdx+m]['TEST_TIME']
        #df_dp2bp.loc[newIdx+m,'TEST_TIME_MFG'] = testTime2MFG(str(test_time))
        
    db_octAOIGO.drop(index=drop_list, columns=['Check2', 'Remarks2'], inplace=True)
    db_octAOIGO.reset_index(inplace=True, drop=True)
    #db_ADCRBSuc = db_ADCRBSuc.drop(columns=['Check'])
    print(db_octAOIGO)
    df2mysql_append(db_octAOIGO, table)
    
    g_type = db_octAOIGO.loc[db_octAOIGO.index[-1]]['TYPE_GROUP']
    tool_id = db_octAOIGO.loc[db_octAOIGO.index[-1]]['TOOL_ID']
    mfg_day = request.form.get('mfg_day')
    print(g_type, tool_id, mfg_day)
    return octAOIGORaw1(user,name, auth, shift, g_type, mfg_day, tool_id)
    #return octAOIGO(user,name, auth, shift, mfg_day, mfg_day)
    

def aoiSamp(date1, date2):
    
    #--AOI Sampling RATIO
    sql = r"select to_char(t.mfg_day,'yyyy-MM-dd') as mfg_day, t.tool_id, to_char(t.test_time,'yyyy-MM-dd hh24:mi:ss') as test_time, "
    sql += r" t.product_code, t.tft_chip_id as chip_id, "
    sql += r" t.grade as PRE_GRADE, t.defect_code_desc as PRE_DEFECT,"
    sql += r" t.test_user as PRE_TEST_USER, t.pre_Grade AS CT1_GRADE,"
    sql += r" t.pre_defect_code_desc AS CT1_DEFECT, t.abbr_no,"
    sql += r" b.grade as OP_GRADE, b.test_user as OP_USER, b.defect_value as OP_VALUE,"
    sql += r" b.defect_code_desc as OP_DEFECT,"
    # 新case調整
    sql += r" case "
    sql += r"  when (t.pre_grade like 'A') then 'RA'"
    sql += r"  when (t.pre_grade like 'B') then 'RB'"
    sql += r"  when (t.pre_grade like 'Q') then 'RQ'"
    sql += r"  when (t.pre_grade like 'M') then 'RM'"  
    sql += r"  when (t.pre_grade like 'C') then 'RC'"    
    sql += r"  when (t.pre_grade like 'K') then 'RK'"    
    sql += r"  when (t.pre_grade like 'G') and (t.abbr_no not like '%CNG%') and (t.abbr_no not like '%XXXX%') and  (t.abbr_no not like '%XCXX%') and (t.abbr_no not like '%XXRX%') and (t.abbr_no not like '%XCRX%') then 'RA(G)'"
    sql += r"  when (t.pre_grade like '3') and (t.abbr_no not like '%K%') and (t.abbr_no not like '%XXXX%') and  (t.abbr_no not like '%XCXX%') and (t.abbr_no not like '%XXRX%') and (t.abbr_no not like '%XCRX%') then 'ARK'"
    sql += r"  when (t.pre_grade in ('3','G','X','W')) and t.abbr_no like '%CNG%' or t.abbr_no like '%XXXX%' or t.abbr_no like '%XCXX%'or t.abbr_no like '%XXRX%' or t.abbr_no like '%XCRX%' then 'CNG'"
    sql += r"  when (t.pre_grade in ('X','W')) and (t.abbr_no not like '%CNG%') and (t.abbr_no not like '%XXXX%') and  (t.abbr_no not like '%XCXX%') and (t.abbr_no not like '%XXRX%') and (t.abbr_no not like '%XCRX%') then 'ADC X' "

    """
    sql += r" case when (t.pre_grade like 'G') and (t.abbr_no not like '%CNG%') and (t.abbr_no not like '%AOI%')and (t.abbr_no not like '%A') then 'CT1_G'"
    sql += r"      when (t.pre_grade like 'RA') and (t.abbr_no not like '%AOI%') then 'RA'"
    sql += r"      when (t.pre_grade like 'X') and (t.abbr_no not like '%CNG%') and (t.abbr_no not like '%A') then 'ADC X'"
    sql += r"      when  t.pre_grade like 'RQ'then 'RQ'"
    sql += r"      when  t.pre_grade like 'RM'then 'RM'"
    sql += r"      when  t.pre_grade like 'RB'then 'RB'"
    sql += r"      when  t.pre_grade like 'RC'then 'RC'"
    sql += r"      when  t.pre_grade like '3'then 'ARK'"
    sql += r"      when (t.pre_grade like 'RK') or (t.abbr_no not like '%K') then 'RK'"
    sql += r"      when (t.pre_grade like 'W') and (t.abbr_no not like '%CNG%') then 'CT1_W'"
    sql += r"      when (t.pre_grade in ('3','G','X','W') and t.abbr_no like '%CNG%') then 'CNG'"
    sql += r"      when ((t.pre_grade like 'G') and ((t.abbr_no like '%AOI%') or (t.abbr_no like '%A'))) then 'RA(G)'"
    """
    
    sql += r"          "
    sql += r"      else t.pre_grade"
    sql += r"      end as type_group"
    sql += r" from("
    sql += r" select *"
    sql += r" from celods.h_dax_fbk_test_ods"
    sql += r" where mfg_day between to_date('" + date1 + "','yyyy-mm-dd') and to_date('" + date2 + "','yyyy-mm-dd')"
    sql += r" and site_type='BEOL'"
    sql += r" and site_id='L11'"
    sql += r" and op_id='OCT2'"
    sql += r" and grade in ('G','Z','P')"
    sql += r" and test_user like 'CC%'"
    sql += r" and tool_id in ('CCCTS300','CCCTSA00','CCOT300','CCOCT400')     "
    sql += r" and tool_id not like 'DMYG2Z'"
    sql += r" )t"
    sql += r" left join celods.h_dax_fbk_test_ods b on t.tft_chip_id=b.tft_chip_id"
    sql += r" where b.test_user not like 'CC%'"
    sql += r" and b.site_type='BEOL'"
    sql += r" and b.site_id='L11'"
    sql += r" and b.judge_cnt > t.judge_cnt"
    sql += r" and b.judge_cnt - t.judge_cnt =1"
    sql += r" and b.mfg_day > (to_date('" + date1 + "','yyyy-mm-dd') - interval '90' day)"
    
    
    raw_data0 = ora2df(sql)
    if len(raw_data0) > 0:
        raw_data0.drop_duplicates(['CHIP_ID'], keep='last', inplace=True)
    return raw_data0

    
    
    
def octAOISamp(user,name, auth, shift, date1,date2):
    
    sectShow = 'octAOISamp'
    # Udefectq
    raw_data0 = aoiSamp(date1, date2)
    #print(raw_data0)

    if len(raw_data0) == 0:
        octAOISamp = pd.DataFrame(columns =["該日期無資料"])
    else:
        #raw_data0.fillna({'DEFECT':'   '}, inplace=True)
        raw_data1 = raw_data0.groupby(['PRODUCT_CODE', 'TOOL_ID', 'OP_GRADE'])
        raw_data2 = raw_data1.size().to_frame(name='COUNT')
        raw_data2 = raw_data2.reset_index()
        
            
        #[`w
        zp_raw = raw_data2[(raw_data2['OP_GRADE'].isin(['Z', 'P']))]
        df_zp = zp_raw.groupby(['PRODUCT_CODE', 'TOOL_ID'])['COUNT'].agg('sum').to_frame(name='ZP')
        
        samp_raw = raw_data2[(~raw_data2['OP_GRADE'].isin(['Z', 'P']))]
        df_samp = samp_raw.groupby(['PRODUCT_CODE', 'TOOL_ID'])['COUNT'].agg('sum').to_frame(name='Sampling')
        
        
    
        df_tot = raw_data2.groupby(['PRODUCT_CODE', 'TOOL_ID'])['COUNT'].agg('sum').to_frame(name='總數')
          
        
        # X
        octAOISamp = pd.concat([df_samp, df_zp, df_tot], verify_integrity = True, axis=1)
        octAOISamp = octAOISamp.fillna(0)
        
        octAOISamp = octAOISamp.reset_index()
        
        #octAOISamp[['OGD', 'BPs', '', 'CP']] = octADCRBSuc[['OGD', 'BPs', '', 'CP']].astype('int')
        octAOISamp['Sampling(%)'] = 100*octAOISamp['Sampling'] / octAOISamp['總數']
        octAOISamp['ZP(%)'] = 100*octAOISamp['ZP'] / octAOISamp['總數']
        octAOISamp['總(%)'] = octAOISamp['ZP(%)'] + octAOISamp['Sampling(%)']
        octAOISamp['同點不可見'] = 0
        octAOISamp['新增點'] = 0
        octAOISamp['漏檢'] = 0
        octAOISamp['非相關位置Defect'] = 0
        octAOISamp['其他'] = 0
        octAOISamp['待確認'] = octAOISamp['Sampling']
        
        
        
        
        table = 'oct_aoi_samp'
        db_data = mysql2df(table)
        
        for item in octAOISamp.index:
            
            tool_id = octAOISamp.loc[item]['TOOL_ID']
            pc = octAOISamp.loc[item]['PRODUCT_CODE']
            tot = octAOISamp.loc[item]['總數']
            
            # group後的raw data
            raw_data1 = raw_data0[(raw_data0['TOOL_ID'] == tool_id) & (raw_data0['PRODUCT_CODE'] == pc)]
            # group後的db data
            db_data1 = db_data[(db_data['TOOL_ID']==tool_id) & (db_data['PRODUCT_CODE']==pc)]
            grades = ['Z', 'P']
            octAOISampRaw = raw_data1[(~raw_data0['OP_GRADE'].isin(grades))].copy()
            
            
            for i in octAOISampRaw.index:
                chipid = octAOISampRaw.loc[i]['CHIP_ID']
                #date0 = str(octAOISampRaw.loc[i]['TEST_TIME'])
                #date_oct = date0[0:4] + date0[5:7] + date0[8:10]
                #eqp_oct = octAOISampRaw.loc[i]['TOOL_ID']
                oct_def = octAOISampRaw.loc[i]['OP_DEFECT']
                
                #pre_test_user = octADCRBSuc.loc[i]['PRE_TEST_USER']
        
                
                #df0 = db_data[(db_data['CHIP_ID']==chipid) & (db_data['TOOL_ID']==eqp_oct) & (db_data['DEFECT']==oct_def)]
                df0 = db_data1[(db_data1['CHIP_ID']==chipid) & (db_data1['OP_DEFECT']==oct_def)]
                if len(df0) > 0:
                    last_n = df0.index[-1]
                    #df0.drop_duplicates(['CHIP_ID', 'OCT_DEFECT'], keep='last', inplace=True)
                    okng = df0.loc[last_n]['Check']
                    #remarks = df0.loc[last_n]['name']+', '+df0.loc[last_n]['Remarks']
                    octAOISamp.loc[item, '待確認'] = octAOISamp.loc[item]['待確認'] - 1
                    if okng in ['同點不可見', '新增點', '漏檢', '非相關位置Defect', '其他']:
                        octAOISamp.loc[item, okng] = octAOISamp.loc[item][okng] + 1
                        #octADCRBSuc.loc[item, def_col+'T{(%)'] = octADCRBSuc.loc[item][def_col+'T{(%)'] - 1
            #octAOISamp.loc[item, def_col+'T{(%)'] = 100*octADCRBSuc.loc[item][def_col+'T{(%)']/tot
            
            
        
        octAOISamp = octAOISamp.round(2)
         
    
    #octADCRBSuc = octADCRBSuc.astype('str')
    
    return render_template('userMain.html', user=str(user),name=name, auth=auth, shift=shift, sectShow=sectShow,
                           date1=date1, date2=date2, octAOISamp= octAOISamp)
    

def octAOISampRaw(user,name, auth, shift, date1, date2, tool_id, pc, grade_col):
    
    sectShow = 'octAOISampRaw'
    
    raw_data0 = aoiSamp(date1, date2)
    if grade_col == 'Sampling':
        grades = ['Z', 'P']
    elif grade_col == 'X':
        grades = ['X']
    
    
    octAOISampRaw = raw_data0[(~raw_data0['OP_GRADE'].isin(grades)) & (raw_data0['TOOL_ID'] == tool_id) & (raw_data0['PRODUCT_CODE'] == pc)].copy()
    octAOISampRaw.reset_index(drop=True, inplace=True)
    #octAOISampRaw['IMG'] = 'NA'
    octAOISampRaw['確認'] = 'NA'
    octAOISampRaw['說明'] = 'NA'
    
    #df_aoi = pd.DataFrame()
    #df_adc = pd.DataFrame()
    df_aoi = octAOISampRaw[['CHIP_ID','PRE_DEFECT', '確認', '說明']]
    #df_adc = octAOISampRaw[['CHIP_ID','OCT_ADC_DEFECT', '確認', '說明']]
    
    
    # d
    table = 'oct_aoi_samp'
    
    db_data = mysql2df(table)
    
    
    for i in octAOISampRaw.index:
        chipid = octAOISampRaw.loc[i]['CHIP_ID']
        date0 = str(octAOISampRaw.loc[i]['TEST_TIME'])
        date_oct = date0[0:4] + date0[5:7] + date0[8:10]
        eqp_oct = octAOISampRaw.loc[i]['TOOL_ID']
        oct_def = octAOISampRaw.loc[i]['OP_DEFECT']
        grade0 = octAOISampRaw.loc[i]['OP_GRADE']
        #pre_test_user = octAOISamp.loc[i]['PRE_TEST_USER']
        
        
        
        df0 = db_data[(db_data['CHIP_ID']==chipid) & (db_data['TOOL_ID']==eqp_oct)].copy()
        if len(df0) > 0:
            last_n = df0.index[-1]
            #df0.drop_duplicates(['CHIP_ID', 'OCT_DEFECT'], keep='last', inplace=True)
            okng = df0.loc[last_n]['Check']
            remarks = df0.loc[last_n]['name']+', '+str(df0.loc[last_n]['Remarks'])
            octAOISampRaw.loc[i, '確認'] = str(okng)
            octAOISampRaw.loc[i, '說明'] = str(remarks)
        
        df_aoi.loc[i, '確認'] = octAOISampRaw.loc[i]['確認']
        df_aoi.loc[i, '說明'] = octAOISampRaw.loc[i]['說明']
        print('OCT找圖:', chipid, date_oct, eqp_oct, oct_def)
        
                   
        
        
        
        
      
        
        if 1:
            octimgs = octDefectImg(chipid, date_oct, eqp_oct, oct_def)
            aoi_img = octimgs[0]
            skip_n = 0
            for num0 in range(len(aoi_img)):
                pattern= "AOI IMG"
                img_name = os.path.basename(aoi_img[num0])
                spl = img_name.split('_')
                try:
                    if spl[3][1:] in ['M', 'F']:
                        pattern = spl[3][1:]+'_'+spl[4] 
                        
                    else:
                        pattern = spl[2][1:]+'_'+spl[3] 
                        #pattern = spl[3][1:]+'_'+spl[4]
                except:
                    1
                if aoi_img[num0][-4:] == '.tif':
                    df_aoi.loc[i, 'IMG_'+str(num0-skip_n)] = "<a href=\""+aoi_img[num0]+"\">"+pattern+"</a>"
                else:
                    # <img align="center" width='160' height='120' src="{{ value[i] }}" ></a>  
                    df_aoi.loc[i, 'IMG_'+str(num0-skip_n)] = "<a href=\"javascript:PopupPic('"+aoi_img[num0]+"')\">"+pattern+"</a>"
    #octaoi_list.append(octaoi_imgs)
    #octadc_list.append(octadc_imgs)
    #octAOISampRaw.drop(columns=['MFG_DAY'], inplace=True)
    
    try:
        btnName = list(request.form)[-1]
        filepath = r'static/csv/'+btnName+'.csv'
        octAOISampRaw.to_csv(filepath, index=False, encoding='utf-8-sig')
    except:
        print('csv儲存失敗:',filepath)

    
    
    
    #octAOISampRaw = octAOISampRaw.reset_index(drop=True)
    #print(octAOISampRaw)
    return render_template('userMain.html', user=str(user),name=name, auth=auth, shift=shift, sectShow=sectShow,
                           date1=date1, date2=date2, octAOISampRaw= octAOISampRaw, df_aoi=df_aoi)


def octAOISamp_Upload(user,name, auth, shift, req_list):
    #^@h
    sectShow = 'octAOISamp'
    #sectShow = 'uploadOK'
    
    #df_dp2bp = pd.DataFrame(columns=['user', 'name', 'shift', 'auth'])
    table = 'oct_aoi_samp'
    db_data = mysql2df(table)
    db_octAOISamp = pd.DataFrame(columns=db_data.columns)
    #db_octAOISamp = pd.DataFrame()
    
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
        
        if col in db_octAOISamp.columns or col in ['Check2', 'Remarks2']:
            db_octAOISamp.loc[num, col] = req
        #　imgCheck'為每一個Ｉｄ的最後一項
    print(db_octAOISamp)
    # 下方選單將覆蓋上方
    cond0 = ~( (db_octAOISamp['Check2'].isin(['---'])) | (db_octAOISamp['Check2'].isnull()) )
    db_octAOISamp.loc[cond0, 'Check'] = db_octAOISamp.loc[cond0]['Check2']
    
    db_octAOISamp.loc[cond0, 'Remarks'] = db_octAOISamp.loc[cond0]['Remarks2']
    
    # 個別補上個人資訊
    user_list = ['user', 'name', 'shift', 'auth']
    drop_list = []
    for m in db_octAOISamp.index:
        check0 = db_octAOISamp.loc[m]['Check']
        if check0 == '---' or check0 is None or pd.isna(check0):
            drop_list.append(m)
        for ii in user_list:
            req = request.form.get(ii)
            db_octAOISamp.loc[m, ii] = req
        db_octAOISamp.loc[m, 'Checked_Date'] = now_hm
        
        # 新增MFG DATE轉換資訊
        #test_time = df_dp2bp.loc[newIdx+m]['TEST_TIME']
        #df_dp2bp.loc[newIdx+m,'TEST_TIME_MFG'] = testTime2MFG(str(test_time))
        
    db_octAOISamp.drop(index=drop_list, columns=['Check2', 'Remarks2'], inplace=True)
    db_octAOISamp.reset_index(inplace=True, drop=True)
    #db_ADCRBSuc = db_ADCRBSuc.drop(columns=['Check'])
    print(db_octAOISamp)
    df2mysql_append(db_octAOISamp, table)
    
    #g_type = db_octAOIGO.loc[db_octAOIGO.index[-1]]['TYPE_GROUP']
    #tool_id = db_octAOIGO.loc[db_octAOIGO.index[-1]]['TOOL_ID']
    
    
    date1 = request.form.get('date1')
    date2 = request.form.get('date2')
   
    return octAOISamp(user,name, auth, shift, date1,date2)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    