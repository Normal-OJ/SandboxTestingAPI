#!/usr/bin/env python
#--coding:utf-8--
import json
from os import listdir,system,chdir,environ
import requests
import zipfile
import threading
import StartTest
import sys  
import time
requesting_status = {}
def LoadTestCases()->dict:
    testcases = {}
    cur_path="./TestCases"
    chdir("TestCases")
    for i in listdir():
        chdir(i)
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

def SendRequest(ip,content,name):
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
    print("sending requests:" , name)
    resp = requests.post(f'{ip}/submit/{content["submissionId"]}',data=body,files=file)
    if(resp.status_code != 200):
        print("Error Occur!!",file=sys.stderr)
        print(f'Get response: {resp.text}')
        requesting_status.update({name:{
            "sucessed":False,
            "timestamp":time.time(),
            "response":{
                "status_code":resp.status_code ,
                "body":resp.text
            } 
        }})
    else:
        requesting_status.update({name:{
            "sucessed":True,
            "timestamp":time.time()
        }})

def requestingJob(sh_dict):
    print("start sending requests",file=sys.stderr)
    StartTest.Lock.acquire()
    dst_base = environ.get("SANDBOX_BASEURL","127.0.0.1")
    dst_port = environ.get("SANDBOX_PORT",8080)
    dst="http://{0}:{1}".format(str(dst_base) ,str(dst_port))
    testcases=dict(LoadTestCases())

    workers = []
    for i in list(testcases.keys()):
        workers.append(threading.Thread(target=SendRequest , args=(dst , testcases[i] , i ,)))
    for i in workers:
        i.start()
    for i in workers:
        i.join()
    print("==================================================")
    print("request status:")
    print(json.dumps(requesting_status , indent=4))
    print("==================================================")
    for i in list(testcases.keys()):
        if requesting_status[i]["sucessed"] == False:
            sh_dict[i] = {
                "isPending": False,
                "ReceiveStatus":requesting_status[i]["response"]
            }
    
    print("end of requester")
    StartTest.Lock.release()
    
    with open(".begin_timestamp.json" , "w") as fp:
        ts = {}
        for i in list(requesting_status.keys()):
            ts.update({i:requesting_status[i]["timestamp"]})
        fp.write(json.dumps(ts,indent=4))
