import os
import server
import requester
import subprocess
import time
import threading
from os import system
from multiprocessing import Manager

Lock=threading.Lock()
time_Limit = 60
if __name__ == "__main__":
    # cat=subprocess.Popen("./nyancat")
    with Manager() as mg:
        sh_dict=mg.dict()
        w1=threading.Thread(target=server.receiverJob , args=(sh_dict,))
        w2=threading.Thread(target=requester.requestingJob , args=(sh_dict,))
        w1.start()
        w2.start()
        w2.join()
        w1.join()
    # cat.kill()
