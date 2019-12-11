import os
import server
import requester
import subprocess
import time
import threading
from os import system
Lock=threading.Lock()
if __name__ == "__main__":
    cat=subprocess.Popen("./nyancat")
    w1=threading.Thread(target=server.receiverJob)
    w2=threading.Thread(target=requester.requestingJob)
    w1.start()
    w2.start()
    w2.join()
    w1.join()
    system("rm ./TestCases/*/*.zip")
    cat.kill()
