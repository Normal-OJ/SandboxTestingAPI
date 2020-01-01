fp=open("/etc/passwd","r")
while(True):
    l=fp.readline()
    if l=="":
        break
    print(l)
fp.close()