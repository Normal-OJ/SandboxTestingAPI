from http.server import BaseHTTPRequestHandler, HTTPServer
from http.client import parse_headers
from urllib.parse import urlparse
from os import listdir,system,chdir,system
import json
import threading
import time
import sys
import StartTest
probSetting = {}
test_result = {}

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
            test_result[p_id]["isPending"] = False
            self.send_response(200)
            self.send_header('Content-type','application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(b"success")

def readConfig():
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

        test_result.update({probSetting["problemId"]:{
            "isPending":True,
            "title":i,
            "expectedResult":probSetting["expectedResult"],
            "RealResult":""
        }})
        chdir("..")
    chdir("..")

def checkIfFinished():
    for i in list(test_result.keys()):
        if test_result[i]['isPending'] == True:
            return False
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
        fp.write(str(report))

    fp.write(']')
    fp.close()

def run():
    # Server settings
    port = 8080
    server_address = ('normal-oj_sandboxtesting', port)
    print('starting server, port', port ,file=sys.stderr)
    httpd = HTTPServer(server_address, HTTPRequestHandler)
    print('running server...' , file=sys.stderr)
    # witing for receiving
    while(not checkIfFinished()):
        httpd.handle_request()
    httpd.server_close()

def displayTestResult():
    while(not checkIfFinished()):
        for i in list(test_result.keys()):
            print(i," is Pending:",test_result[i]['isPending'] ,file=sys.stderr)
        time.sleep(3)
    
def receiverJob():
    StartTest.Lock.acquire()
    readConfig()
    print("done of reading config" , file=sys.stderr)
    StartTest.Lock.release()
    works = []
    works.append(threading.Thread(target=run))
    works.append(threading.Thread(target=displayTestResult))

    for i in works:
        i.start()
    for i in works:
        i.join()


    print("done of receiving result , exporting Testing Profile",file=sys.stderr)
    exportResult("Test")
    print("Successfully export the Testing Result,End of Testing",file=sys.stderr)
    
