#!/usr/bin/env python
#--coding:utf-8--

from http.server import BaseHTTPRequestHandler, HTTPServer
from http.client import parse_headers
import json
from os import listdir
from urllib.parse import urlparse
import requests

test_result={}
class HTTPRequestHandler(BaseHTTPRequestHandler):
    # POST handler
    def do_POST(self):
        sendReply = False
        print("request for",self.path)
        r_header = dict(self.headers)
        
        p_id= str(urlparse(self.path).path).replace('/submission/','')
        if(p_id == "" or not ( int(p_id) in test_result.keys() )):
            self.send_error(404,'Error request')
        else:
            r_contents=self.rfile.read(int(r_header['Content-Length']))
            contents=dict(json.loads(s=r_contents))
            if(contents != None):
                sendReply = True
            if("problemStatusId" in contents.keys()):
                test_result[int(probSetting["problemId"])]["RealResult"] = contents["problemStatusId"]
                sendReply = True
            
            if sendReply == True:
                try:
                    self.send_response(200)
                    self.send_header('Content-type','application/json; charset=utf-8')
                    self.end_headers()
                    self.wfile.write("success")
                except:
                    self.send_error(404,'Error')

def run():
    port = 6666
    print('starting server, port', port)

    # Server settings
    server_address = ('127.0.0.1', port)
    httpd = HTTPServer(server_address, HTTPRequestHandler)
    print('running server...')
    httpd.serve_forever()

def LoadTestCases(cur_path)->dict:
    testCases = {}

    for i in listdir(cur_path):
        fp=open(cur_path + i + "settings.json" , "r")
        probSetting = ""
        while(True):
            r=fp.readline()
            if(r == ""):
                break
            probSetting+=r
        probSetting=json.loads(s=probSetting)

        testCases.update({i:{
            "source"  : cur_path + i + "/main.c" ,
            "testcase": cur_path + i + "/testcase.zip" ,
            "checker" : "",
            "languageid": 0,
            "token":"wry!!!",
            "timeLimit":probSetting["timeLimits"],
            "memoryLimit":probSetting["memoryLimits"],
            "submissionId":int(probSetting["problemId"]),         #problemId == submissionId
        }})

        test_result.update({int(probSetting["problemId"]):{
            "isPending":True,
            "title":i,
            "expectedResult":probSetting["expectedResult"],
            "RealResult":""
        }})
    
    return testCases
def SendRequest(ip,content):
    header={
        "content-type":"fuckyou"
    }
    body={
        "checker":content["checker"],
        "languageId":content["languageId"],
        "token":content["token"],
        "timeLimit":content["timeLimits"],
        "memoryLimit":content["memoryLimits"],
        "submissionId":content["submissionId"]
    }
    file={
        "source":open(content["source"],"rb"),
        "testcase":open(content["testcase"],"rb")
    }
    resp = requests.post(ip,headers=header,data=body,files=file)
    if(resp.status_code != 200):
        print("Error Occur!!")
        return False
    return True

if __name__ == '__main__':
    cur_path = "./TestCases"
    dst="127.0.0.1"
    testCases=dict(LoadTestCases(cur_path))
    for i in list(testCases.keys()):
        SendRequest(dst,testCases[i])
    run()