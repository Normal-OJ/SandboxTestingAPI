from http.server import BaseHTTPRequestHandler, HTTPServer
from http.client import parse_headers
from urllib.parse import urlparse
from os import listdir,system,chdir,system
import json
import threading
import time
import sys
import os
import StartTest
probSetting = {}
test_result = {}
req_buffer = []
class HTTPRequestHandler(BaseHTTPRequestHandler):
    # POST handler
    def do_PUT(self):
        print("request for",self.path,file=sys.stderr)
        r_header = dict(self.headers)
        
        p_id= str(urlparse(self.path).path).replace('/submission/','')
        if p_id not in list(test_result.keys()):
            self.send_error(404,'Error request')
        else:
            p_id = p_id
            # getting content of a request
            r_contents=self.rfile.read(int(r_header['Content-Length']))
            contents=dict(json.loads(s=r_contents))
            print("receiving:",file=sys.stderr)
            print(contents,file=sys.stderr)

            test_result[p_id]["RealResult"] = contents
            req_buffer.append(p_id)
            self.send_response(200)
            self.send_header('Content-type','application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(b"success")

def readConfig():
    prob_ids = []
    chdir("TestCases")
    for i in listdir():
        prob_ids.append(i)
        print("loading {0}".format(i))
        chdir(i)
        fp=open("settings.json", "r")
        probSetting = ""
        while(True):
            r=fp.readline()
            if(r == ""):
                break
            probSetting+=r
        probSetting=json.loads(s=probSetting)

        test_result.update({probSetting["problemId"]:{
            "title":i,
            "expectedResult":probSetting["expectedResult"],
            "RealResult":""
        }})
        chdir("..")
    chdir("..")
    return prob_ids

def checkIfFinished( sh_dict ):
    StartTest.Lock.acquire()
    print("i am checking if finished")
    for i in list(sh_dict.keys()):
        if sh_dict[i]['isPending'] == True:
            print("checked if finished ended")
            StartTest.Lock.release()
            return False
    print("check if finished end")
    StartTest.Lock.release()
    return True

'''
    if obj and filter's intersection equals filter , return true
    otherwise , return false
'''
def checkRequire(obj,filter):
    obj = dict(obj)
    filter = dict(filter)

    for i in list(filter.keys()):
        if i not in list(obj.keys()):
            return False
        if obj[i] != filter[i] :
            return False
    return True

'''
    find if there's a match case exsist in expectedResult
'''
def compareResult(problemId):
    for expect in list(test_result[problemId]['expectedResult']):
        if checkRequire(test_result[problemId]['RealResult'] , expect):
            return True
    return False

'''
    export a file of testing
'''
def exportResult(filename):
    ts = time.strftime('%Y%m%d%H%M%S', time.localtime())
    fp = open("{0}{1}.report".format(filename , ts) , "w")
    fp.write('[')
    commma_enable = False
    for i in list(test_result.keys()):
        report = {}
        if compareResult(i)==False:
            report.update({
                "problemId":i,
                "name":test_result[i]['title'],
                "status":"Failed",
                "expectedResult":test_result[i]['expectedResult'],
                "RealResult":test_result[i]['RealResult']
            })
        else:
            report.update({
                "problemId":i,
                "name":test_result[i]['title'],
                "status":"Passed"
            })
        
        if commma_enable:
            fp.write(',')
        else:
            commma_enable = True
        fp.write(json.dumps(report))

    fp.write(']')
    fp.close()

def run(sh_dict):
    # Server settings
    port = int(os.environ.get("API_PORT",8080))
    baseurl= os.environ.get("BASE_URL" , "127.0.0.1")
    server_address = (baseurl, port)
    print('starting server at', server_address ,file=sys.stderr)
    httpd = HTTPServer(server_address, HTTPRequestHandler)
    print('running server...' , file=sys.stderr)
    # waiting for receiving
    while(not checkIfFinished(sh_dict)):
        print("try to handle one request")
        httpd.handle_request()

        StartTest.Lock.acquire()
        for i in req_buffer:
            sh_dict[i] ={"isPending" : False}
        StartTest.Lock.release()

        req_buffer.clear()
        print("handle ended")
    httpd.server_close()

def displayTestResult(sh_dict):
    print("try to display result")
    while(not checkIfFinished(sh_dict)):
        for i in list(sh_dict.keys()):
            print(i," is Pending:",sh_dict[i]['isPending'] ,file=sys.stderr)
        time.sleep(3)
    
def receiverJob(sh_dict):
    StartTest.Lock.acquire()
    prb_ids = readConfig()
    for i in prb_ids:
        sh_dict.update({
            i:{
                "isPending":True
            }
        })
    print("done of reading config" , file=sys.stderr)
    StartTest.Lock.release()
    
    works = []
    works.append(threading.Thread(target=run , args = (sh_dict ,)))
    #works.append(threading.Thread(target=displayTestResult , args = (sh_dict ,) ))

    for i in works:
        i.start()
    for i in works:
        i.join()
    
    print("done of receiving result , exporting Testing Profile",file=sys.stderr)
    exportResult("Test")
    print("Successfully export the Testing Result,End of Testing",file=sys.stderr)
    
