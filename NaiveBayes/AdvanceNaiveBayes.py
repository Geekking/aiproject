#encoding:utf-8
'''
Created on Dec 11, 2013

@author: lanny
'''

import re
import sys
import time
import jieba
import math
import os
import MySQLdb


jieba.enable_parallel()

trainSetPath = "/home/lanny/workspace/python27/AIProject/trainSet"

cat_lists = []
cat_frequency_dict = dict()
word_cat_frequence_dict = dict()
vacabulary_dict = dict()
totalCount = 0
cat_token = dict()
cat_feature = dict()
word_cat_p = dict()
cat_token_count_dict = dict()
total_token_count=0

stopWordlist = ["的","-","不","在","有","是","为",
                 "以","于","他","而","及","了","这",
                 "与","但","并","已","我","们","把",
                 "，","。","《","》","“","”","！","？",
                 "（","）","……","某","和","【","】",'今',
                 '上','将','年','或','其','则','所以','\t',
                 '就','近','中','从','起','元','至于',
                 '、','：','；','·','[',']','','\n','\n\n',
                 '到','边','至','对','因此','國家','国家',
                 '里','小','只有','[0-9]+','月','同时','•','→',
                 '    ','/',',','.','\"','－','^','а','%',
                 '「','」','一些','等','处','个','最','自','中国'
                 ,"这是",'米','日','以来','也','城','…','列为','世界',
                 ' ','\'','°','显示',' ','之','维基','编辑','简体']
numRe = re.compile("[0-9]+\.?[0-9]*|[a-z|A-Z]+|\n+ +")

trainMultinomialNBLogFolder = "/home/lanny/workspace/python27/AIProject/outFile/Log"

trainMultinomialNBResultFolder = "/home/lanny/workspace/python27/AIProject/outFile/catFile"

applyMultinomialNBFilePathFolder = "/home/lanny/workspace/python27/AIProject/testSet"
applyMultinomialNBFileResultFolder = '/home/lanny/workspace/python27/AIProject/outFile/applyOut'

currentTime = time.strftime("%Y-%m-%d-%X", time.localtime())

trainMultinomialNBLogFolder += '/'+currentTime + "log.out"
trainMultinomialNBResultFolder += '/'+currentTime+"result.out"
applyResultFilePath =  applyMultinomialNBFileResultFolder + '/' + currentTime + 'applyResult.out'
try:
    logFile = open(trainMultinomialNBLogFolder,"w")
    trainResult=open(trainMultinomialNBResultFolder,"w")
    applyResult = open(applyResultFilePath,'w')
except:
    print "can not open file"
    sys.exit()

try:
    conn = MySQLdb.connect(host='localhost',user='root',passwd='627116',db='AIAdvance',charset = "utf8", use_unicode = True,unix_socket="/opt/lampp/var/mysql/mysql.sock")
except MySQLdb.Error, e:
    print "Error %d: %s" % (e.args[0], e.args[1])
    sys.exit(1) 

def extractTokenFromFile(file):
    if os.path.exists(file):
        try:
            pagefile = open(file,'r')
            page = pagefile.read()
    
        except:
            print "cannot open file:"+file
            sys.exit(1)
    else:
        page = file
        
    word_list = jieba.cut(page)   #用结巴分词进行分词
    token_dict = dict()
    for each_word in word_list:
        #去掉停止词和数字
        if each_word in stopWordlist or numRe.match(each_word):
            continue
        else:
            if each_word in token_dict:
                token_dict[each_word]+=1
            else:
                token_dict[each_word] = 1
    return token_dict


def extractTokenFromText(doc):
    '''
    try:
        pagefile = open(doc,'r')
    except:
        print "cannot open file:"+doc
        sys.exit(1)
    page = pagefile.read()
    '''
    page = doc
    word_list = jieba.cut(page)
    token_dict = dict()
    for each_word in word_list:
        if each_word in stopWordlist or numRe.match(each_word):
            continue
        else:
            if each_word in token_dict:
                token_dict[each_word]+=1
            else:
                token_dict[each_word] = 1
    return token_dict

#抽取字典
def extractVacabulary(rootPath):
    global cat_lists,totalCount,cat_token,total_token_count,cat_token_count_dict
    cat_dir_list = os.listdir(rootPath)
    if len(cat_dir_list) > 0:
        cat_lists = cat_dir_list
    else:
        print "no file is empty"+rootPath
        sys.exit(1)
    cat_token_dict = dict()
    for each_cat in cat_lists:
        cat_doc_lists = os.listdir(rootPath + '/'+ each_cat)
        cat_frequency_dict[ each_cat] = len(cat_doc_lists) #记录每一类有多少个景点，为以后记录先验概率
        totalCount += cat_frequency_dict[each_cat]        #记录所有的景点数目，也是为求先验概率做准备
        cat_root = rootPath + '/'+ each_cat
        cat_token_count_dict[each_cat]=0 
        #对训练集的每一个页面进行处理
        for each_doc in cat_doc_lists:
            #从页面提取出词语，返回的事一个以词语为键的字典
            doc_token_dict = extractTokenFromFile(cat_root + '/'+ each_doc) 
            for each_token in doc_token_dict:
                if each_token in cat_token_dict:
                    cat_token_dict[each_token] += doc_token_dict[each_token];
                else:
                    cat_token_count_dict[each_cat]+=1
                    cat_token_dict[each_token] = doc_token_dict[each_token]
                    
                if each_token in vacabulary_dict:
                    vacabulary_dict[each_token] += doc_token_dict[each_token]
                else:
                    vacabulary_dict[each_token] =  doc_token_dict[each_token]
        total_token_count += cat_token_count_dict[each_cat]
        cat_token[each_cat] = cat_token_dict
        cat_token_dict=dict()

def writeCatGoodsToDB(cat_feature):
    try:
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS catGoods")
        cursor.execute("""
        CREATE TABLE catGoods
        (
          cat    VARCHAR(255)  NOT NULL,
          goods  VARCHAR(1000) NOT NULL,
          PRIMARY KEY (cat)
        )DEFAULT CHARACTER SET utf8 collate utf8_bin
        """)
    except MySQLdb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])
        sys.exit (1)
    for each_cat in cat_feature:
        feature_dict = cat_feature[each_cat]
        goodslist = feature_dict.keys() 
        goods = ','.join(goodslist)
        insertSQL = "insert into `catGoods`(`cat`,`goods`) \n values('%s','%s')"%(each_cat,str(goods))
        try:
            cursor.execute(insertSQL)
            conn.commit()
        except MySQLdb.Error, e:
            print "Error %d: %s" % (e.args[0], e.args[1])
            sys.exit (1)


#用开方测试类特性词选取。    
def selectFeature():
    extractVacabulary(trainSetPath)
    global vacabulary_dict,cat_feature,totalCount,total_token_count,cat_token_count_dict
    new_vacabulary_dict = dict()
    for each_cat in cat_token:
        word_docs_count = cat_token[each_cat]
        word_chivalue = dict()
        #算出每个词对应开方检验值
        for each_word in word_docs_count:
            A = word_docs_count[each_word]
            B = cat_token_count_dict[each_cat] - A
            C = vacabulary_dict[each_word] - A
            D = total_token_count - cat_token_count_dict[each_cat]  -  vacabulary_dict[each_word] + word_docs_count[each_word]
            word_chivalue[each_word] = (float)(A+B+C+D)*(A*D-C*B)*(A*D-C*B)/((A+C)*(B+D)*(A+B)*(C+D))
        word_chivalue = sorted(word_chivalue.items(),key = lambda e:e[1],reverse = True)
        count =0
        cat_feature_dict = dict()   #记录每一个词语下的特性词
        for index in range(len(word_chivalue)):
            if count > 35:
                break
            else:
                (word,value) = word_chivalue[index]
                if len(word) >3 : 
                    continue
                if re.match(numRe,word):
                    continue
                else:
                    print word
                count +=1
                cat_feature_dict[word] = word_docs_count[word]
                if word in new_vacabulary_dict:
                    new_vacabulary_dict[word] += cat_feature_dict[word]
                else:
                    new_vacabulary_dict[word] = cat_feature_dict[word]
        cat_feature[each_cat] = cat_feature_dict
    writeCatGoodsToDB(cat_feature)      #存入数据库，一遍后面处理。
    vacabulary_dict = new_vacabulary_dict   #更新词典
    total_token_count = len(vacabulary_dict)    
    for each_cat in cat_lists:
        try:
            cat_feature_str = str(each_cat+'\n')
            for each_f in cat_feature[each_cat]:
                cat_feature_str += str(each_f+' : '+str(cat_feature[each_cat][each_f])+'\n')
            trainResult.write(str(cat_feature_str))
            logFile.write("write selected feature category:"+each_cat)
        except:
                print "can not open result file"
#朴素贝页斯分类法学习过程
def trainMultinomialNB():
    selectFeature()
    for each_cat in cat_frequency_dict:
        cat_frequency_dict[each_cat] = (float)(cat_frequency_dict[each_cat])/totalCount
        for each_word in vacabulary_dict:
            if each_word in cat_feature[each_cat]:
                word_cat_p[each_word+each_cat] =(float)(cat_feature[each_cat][each_word]+1)/(total_token_count + vacabulary_dict[each_word]) #避免
            else:
                word_cat_p[each_word+each_cat] =(float)(1)/(total_token_count + vacabulary_dict[each_word])
#对一个的页面进行分类，返回页面所属类别        
def applyMultinomialNBToDoc(Doc):
    global vacabulary_dict
    doc_token_set = extractTokenFromFile(Doc)
    max_p = -100000
    cat='place_of_interesting'

    for each_cat in cat_lists:
        if cat_frequency_dict[each_cat] !=0 :
            cur_p = math.log(cat_frequency_dict[each_cat])
            for each_token in doc_token_set:
                if each_token in vacabulary_dict:
                    cur_p += math.log(word_cat_p[each_token+each_cat])
        else:
            cur_p = max_p
        if cur_p > max_p:
            max_p = cur_p
            cat = each_cat
    return cat    
   
def applyToLocal(testSetPath):
    trainMultinomialNB()
    file_list = os.listdir(testSetPath)
    file_cat_table  = dict()
    file_count = 0
    file_cat_str = ''
    for each_file in file_list:
        file_cat_table[each_file] =  applyMultinomialNBToDoc(trainSetPath + '/'+each_file)      
        if file_count >200:
            for each_f in file_cat_table:
                file_cat_str += str(each_f) + ' : ' + file_cat_table[each_f]+'\n' 
            try:
                applyResult.write(file_cat_str)
                file_cat_table = dict()
                file_cat_str = ''
                file_count = 0
            except:
                print "cannot write output to file_cat_str"
        else:
            file_count +=1
    if file_count >0:
        for each_f in file_cat_table:
            file_cat_str += str(each_f) + ' : ' + file_cat_table[each_f]+'\n' 
        try:
            applyResult.write(file_cat_str)
            file_cat_table = dict()
        except:
            print "cannot write output to file_cat_str"

def applyToDB():
    count = dict()
    try:
        cursor = conn.cursor()
    except MySQLdb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])
        sys.exit(1)
    
    trainMultinomialNB()
    
    try:
        tableName = "scenery"
        selectAll = "select name,introduction from %s " %tableName
        cursor.execute(str(selectAll))
        t_a = cursor.fetchall()
        title_count = 0
        updateValues = []
        for each_title_abs in t_a:
            title = each_title_abs[0]
            abs = each_title_abs[1]
            cat = applyMultinomialNBToDoc(abs)
            if cat in count:
                count[cat]+=1
            else:
                count[cat]=0
            updateValues.append((cat,title))
            if title_count >=100:
                title_count = 0
                try:
                    cursor.executemany("update `scenery` set category = %s where name =%s",updateValues)
                    conn.commit()
                    updateValues = []
        
                except MySQLdb.Error, e:
                    print "Error %d: %s" % (e.args[0], e.args[1])
                    sys.exit(1)
            else:
                title_count +=1
        if title_count>0:
            title_count = 0
            try:
                cursor.executemany("update scenery set category = %s where name = %s",updateValues)
                conn.commit()
                updateValues = []
        
            except MySQLdb.Error, e:
                print "Error %d: %s" % (e.args[0], e.args[1])
                sys.exit(1)
                
    except MySQLdb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])
        sys.exit(1) 
        conn.close()
    for key in count.keys():
        print key+':'+str(count[key])
applyToDB()
logFile.close()
trainResult.close()
applyResult.close()
