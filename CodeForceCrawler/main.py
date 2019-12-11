import requests
import bs4
import json
def exportHtml(name,content):
    with open(name,"w") as fp:
        fp.write(content)

verdictNameList=[
    "anyVerdict",
    "OK",
    "WRONG_ANSWER",
    "RUNTIME_ERROR",
    "TIME_LIMIT_EXCEEDED",
    "MEMORY_LIMIT_EXCEEDED",
    "COMPILATION_ERROR"
]
verdict2status={
    "OK":"AC",
    "WRONG_ANSWER":"WA",
    "RUNTIME_ERROR":"RE",
    "TIME_LIMIT_EXCEEDED":"TLE",
    "MEMORY_LIMIT_EXCEEDED":"MLE",
    "COMPILATION_ERROR":"CE"
}
programTypeForInvokerList=[
    "anyProgramTypeForInvoker"
    "c.gcc11",
    "cpp.g++11",
    "python.3"
]
programTypeForInvoker2programType={
    "c.gcc11":"C",
    "cpp.g++11":"C++",
    "python.3":"Python3"
}
def findSpecifySubmissionIds(CONTEST_ID,verdictName,programTypeForInvoker)->list:
    """
        query all the match sample during a specify contest

        Parameter:

        CONTEST_ID: the contest id

        verdictName: the submission status of a problem, ex:AC,WA...

        programTypeForInvoker: the language of program

        Return Value:

        a list of ids (list[int]) 
    """
    ses=requests.session()
    res=ses.get("https://codeforces.com/contest/{0}/status".format(str(CONTEST_ID)))
    soup=bs4.BeautifulSoup(res.text,"html.parser")
    csrfToken=soup.find("meta",{"name":"X-Csrf-Token"})
    redirectPostData={
        "csrf_token":str(csrfToken['content']),
        "action":"setupSubmissionFilter",
        "frameProblemIndex":"anyProblem",
        "verdictName":verdictName,
        "programTypeForInvoker":programTypeForInvoker,
        "comparisonType":"NOT_USED"
    }
    res=ses.post("https://codeforces.com/contest/{0}/status".format(str(CONTEST_ID)),data=redirectPostData,allow_redirects=True)
    ses.close()
    if res.status_code != 200:
        print("Error Occur")
        print("Query Return Code {0}".format(str(res.status_code)))
        return None
    soup=bs4.BeautifulSoup(res.text,"html.parser")
    ret=[]
    for i in soup.find_all("a",{"class":"view-source"}):
        ret.append(i["submissionid"])
    return ret

def getSubmittion(CONTEST_ID,SUBMISSION_ID):
    """
        get the specify submittion by CONTEST_ID and SUBMISSION_ID

        Parameter:

        CONTEST_ID: the contest id

        SUBMISSION_ID: the submission id

        Return Values:

        sourceCode: source code (str)

        compilationError: wheather it's a CE case (boolean)

        testCases: a list of dictory with testcases (list[dict])
    """
    ses=requests.session()
    res=ses.get("https://codeforces.com/contest/{0}/submission/{1}".format(str(CONTEST_ID),str(SUBMISSION_ID)))
    soup=bs4.BeautifulSoup(res.text,"html.parser")
    csrfToken=soup.find("span",{"class":"csrf-token"})
    PostData={
        "csrf_token":str(csrfToken['data-csrf']),
        "submissionId":str(SUBMISSION_ID)
    }
    res=ses.post("https://codeforces.com/data/submitSource",data=PostData)
    if res.status_code != 200:
        print("Error Occur!!")
        print("Receive Return Code {0}".format(str(res.status_code)))
        return None
    ses.close()
    data=dict(json.loads(res.text))
    
    sourceCode=data["source"]
    testCaseNum=data["testCount"]
    
    testCases=[]
    # extracting data
    for i in range(1,testCaseNum+1):
        if str(data["input#"+str(i)]).find("...")!=-1 or str(data["answer#"+str(1)]).find("...")!=-1:
            continue
        testCases.append({
            "input":data["input#"+str(i)],
            "output":data["answer#"+str(1)],
            "verdict":data["verdict#"+str(i)]
        })
    
    return sourceCode , data["compilationError"] , testCases
    
if __name__ == "__main__":
    #print(findSpecifySubmissionIds(1265,"OK","c.gcc11"))
    getSubmittion(132,61898597)
