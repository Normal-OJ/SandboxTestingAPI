#!/usr/bin/env python
#--coding:utf-8--
import json
from os import listdir,system,chdir
import requests
import zipfile
import threading
import StartTest
import sys
def zipFolder(src , filename):
    chdir(src)
    system(f"zip -qr {filename}.zip *")
    chdir("..")
    system(f"mv {src}/{filename}.zip {filename}.zip")

def LoadTestCases()->dict:
    testCases = {}
    cur_path="./TestCases"
    chdir("TestCases")
    for i in listdir():
        chdir(i)
        zipFolder("src","source")
        zipFolder("testCases","testcase")
        
        fp=open("settings.json", "r")
        probSetting = ""
        while(True):
            r=fp.readline()
            if(r == ""):
                break
            probSetting+=r
        probSetting=json.loads(s=probSetting)

        testCases.update({i:{
            "source"  : f"{cur_path}/{i}/source.zip",
            "testcase": f"{cur_path}/{i}/testcase.zip" ,
            "checker" : "",
            "languageId": probSetting["languageId"],
            "token":"wry!!!",
            "submissionId":probSetting["problemId"]         #problemId == submissionId
        }})
        chdir("..")
    chdir("..")
    print("end of Loading test cases",file=sys.stderr)
    return testCases
def SendRequest(ip,content):
    header={
        "content-type":"fuckyou"
    }
    body={
        "checker":content["checker"],
        "languageId":content["languageId"],
        "token":content["token"],
        "submissionId":content["submissionId"]
    }
    file={
        "source":open(content["source"],"rb"),
        "testcase":open(content["testcase"],"rb")
    }
    resp = requests.post(ip,headers=header,data=body,files=file)
    if(resp.status_code != 200):
        print("Error Occur!!",file=sys.stderr)
        return False
    return True
def requestingJob():
    print("start sending requests",file=sys.stderr)
    StartTest.Lock.acquire()
    dst="http://127.0.0.1"
    testCases=dict(LoadTestCases())
    for i in list(testCases.keys()):
        SendRequest(dst,testCases[i])
    StartTest.Lock.release()