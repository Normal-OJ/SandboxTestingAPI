from http.server import BaseHTTPRequestHandler, HTTPServer
from http.client import parse_headers
from urllib.parse import urlparse
from os import listdir,system,chdir
import json
import threading
import time
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
    print('successfully create the server')

def readConfig():
    testCases = {}
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

        test_result.update({int(probSetting["problemId"]):{
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

def compareResult(filename):
    ts = time.strftime('%Y%m%d%H%M%S', time.localtime())
    fp = open("{0}{1}.report".format(filename , ts) , "w")
    fp.write('[')
    commma_enable = False
    for i in list(test_result.keys()):
        report = {}
        if test_result[i]['expectedResult'] != test_result[i]['RealResult'] :
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
if __name__ == '__main__':
    
    readConfig()
    
    server_thread = threading.Thread(target = run)
    server_thread.start()
    while(not checkIfFinished()):
        print(test_result)
        time.sleep(1)
    server_thread._delete()

    


    
    
    