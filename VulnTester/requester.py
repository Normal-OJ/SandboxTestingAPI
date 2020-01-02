#!/usr/bin/env python
#--coding:utf-8--
import json
from os import listdir,system,chdir,environ
import requests
import zipfile
import threading
import StartTest
import sys  

def zipFolder(src , filename):
    chdir(src)
    #print("zip command:{0}".format(f"zip -qr {filename}.zip . -i *") , file = sys.stderr)
    system(f"zip -qr {filename}.zip *")
    chdir("..")
    system(f"mv {src}/{filename}.zip {filename}.zip")

def LoadTestCases()->dict:
    testcases = {}
    cur_path="./TestCases"
    chdir("TestCases")
    for i in listdir():
        print("try to zip {0}".format(i))
        chdir(i)
        zipFolder("src","source")
        zipFolder("testcase","testcase")
        
        fp=open("settings.json", "r")
        probSetting = ""
        while(True):
            r=fp.readline()
            if(r == ""):
                break
            probSetting+=r
        probSetting=json.loads(s=probSetting)

        testcases.update({i:{
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
    return testcases
def SendRequest(ip,content):
    header={
        "content-type":"multipart/form-data"
    }
    body={
        "checker":content["checker"],
        "languageId":content["languageId"],
        "token": content["token"]
    }
    file={
        "code": ('dmkaspdmaspd', open(content["source"],"rb")),
        "testcase": ('sadas', open(content["testcase"],"rb"))
    }
    resp = requests.post(f'{ip}/submit/{content["submissionId"]}',data=body,files=file)
    if(resp.status_code != 200):
        print("Error Occur!!",file=sys.stderr)
        print(f'Get response: {resp.text}')
        return False
    return True
def requestingJob(sh_dict):
    print("start sending requests",file=sys.stderr)
    StartTest.Lock.acquire()
    dst_base = environ.get("SANDBOX_BASEURL","127.0.0.1")
    dst_port = environ.get("SANDBOX_PORT",8080)
    dst="http://{0}:{1}".format(str(dst_base) ,str(dst_port))
    testcases=dict(LoadTestCases())
    for i in list(testcases.keys()):
        print("sending request:{0}".format(i))
        if SendRequest(dst,testcases[i]) == False:
            sh_dict[i] = {"isPending":False}
    print("end of requester")
    StartTest.Lock.release()
