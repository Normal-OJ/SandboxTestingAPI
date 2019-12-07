import os
import threading
import server
import requester

if __name__ == "__main__":
    w1 = threading.Thread(target=server.receiverJob)
    w1.run()
    requester.requestingJob()
    w1.join()
