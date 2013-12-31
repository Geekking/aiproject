#coding:utf-8
'''
Created on Dec 15, 2013

@author: lanny
'''

import MySQLdb
import time
import sys


try:
    conn = MySQLdb.connect(host='localhost',user='root',passwd='627116',db='AIAdvance',charset = "utf8", use_unicode = True,unix_socket="/opt/lampp/var/mysql/mysql.sock")
except MySQLdb.Error, e:
    print "Error %d: %s" % (e.args[0], e.args[1])
    sys.exit(1)
    
try:
    cursor = conn.cursor()
except MySQLdb.Error, e:
    print "Error %d: %s" % (e.args[0], e.args[1])
    sys.exit(1)
    
trainCatDoc = "/home/lanny/workspace/python27/AIProject/trainCatDoc"
trainSetRoot = "/home/lanny/workspace/python27/AIProject/trainSet"

def addPage(pageTitle,Cat):
    
    placename= pageTitle

    sqlString = "select introduction from scenery where name = \'%s\' " %placename
    try:
        cursor.execute(sqlString)
        conn.commit()
        file = cursor.fetchone()
    except MySQLdb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])
        sys.exit(1)
    fPath = trainSetRoot+'/'+Cat+'/'+str(pageTitle)
    if file :
    
        try:
            newPage = open(fPath,'w')
        except:
            print "Cannnot open output file"+fPath
            sys.exit(1)
        try:
            for each in file:
                newPage.write(each)
            newPage.close()
        except:
            print "Cannnot write to file"+fPath
            sys.exit(1)
    else:
        print sqlString
        print cat,pageTitle

try:
    CatDocFile = open(trainCatDoc,'r')
except :
    print "Cannot open file:"+trainCatDoc
    sys.exit(1)
while True:
    cat = CatDocFile.readline()
    if cat == '':
        break
    else:
        cat = cat[0:-1]
        placeString = CatDocFile.readline()
        placeList = placeString.split('、',-1)
        print cat,len(placeList)
        placeString = CatDocFile.readline()
 
        for each_place in placeList:
            if each_place == '\n' or each_place == '':
                continue
            
            addPage(each_place,cat)

CatDocFile.close()
            
        