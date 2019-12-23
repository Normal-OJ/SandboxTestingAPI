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
def findSpecifySubmissionIds(CONTEST_ID,verdictName,programTypeForInvoker,problemIndex)->list:
    """
        query all the match sample during a specify contest

        Parameter:

        CONTEST_ID: the contest id

        verdictName: the submission status of a problem, ex:AC,WA...

        programTypeForInvoker: the language of program

        problemIndex: the Index of problem
        
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
        "frameProblemIndex":problemIndex,
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

def getSubmittion(CONTEST_ID,SUBMISSION_ID,getTestCase):
    """
        get the specify submittion by CONTEST_ID and SUBMISSION_ID

        Parameter:

        CONTEST_ID: the contest id

        SUBMISSION_ID: the submission id

        getTestCase: wheather to get testCases

        Return Values:

        sourceCode: source code (str)

        compilationError: wheather it's a CE case (boolean)

        testCases: 
        
        if getTest is True, return a list of dictory with testcases (list[dict])

        otherwise, return the judge status of a problem

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
    testCaseNum=int(data["testCount"])
    testCases=[]

    if getTestCase == True:
        # extracting data
        for i in range(1,testCaseNum+1):
            if str(data["input#"+str(i)]).find("...")!=-1 or str(data["answer#"+str(1)]).find("...")!=-1:
                continue
            testCases.append({
                "input":data["input#"+str(i)],
                "output":data["answer#"+str(1)],
                "verdict":data["verdict#"+str(i)],
                "num":i
            })
    else:
        for i in range(1,testCaseNum+1):
            testCases.append({
                "verdict":data["verdict#"+str(i)],
                "num":i
            })
    
    return sourceCode , data["compilationError"] , testCases
    
def buildProblemList(CONTEST_ID):
    """
        create a avaible problem base

        Parameter:

        CONTEST_ID: the submission id

        Return Values:

        problemDataSet: a json like object dictionary with problem question set
    """
    ses=requests.session()
    res=ses.get("https://codeforces.com/contest/{0}/status".format(str(CONTEST_ID)))
    soup=bs4.BeautifulSoup(res.text,"html.parser").find("select",{"class":"setting-value"} , "html.parser")
    soup=soup.find_all("option")
    
    problemIdList = []
    for i in soup:
        problemIdList.append(i["value"])
    
    problemDataSet={}
    for i in problemIdList:
        if i == "anyProblem":
            continue
        submitIdList = findSpecifySubmissionIds(CONTEST_ID , "OK" , "anyProgramTypeForInvoker" , i)
        _ , _ , testCases = getSubmittion(CONTEST_ID , submitIdList[0],True)
        if len(testCases)!=0:
            problemDataSet.update({i:testCases})
    
    return problemDataSet

def getProcessedCode(CONTEST_ID , verdictName , programTypeForInvoker , frameProblemIndex , problemDB):
    """
        construct specify processed submission base on the condiction it given

        Parameter:

        CONTEST_ID: the submission id

        verdictName: the submission status of a problem, ex:AC,WA...

        programTypeForInvoker: the language of program

        frameProblemIndex: the specify problem id

        problemDB: avaible problem database

        Return Values:

        problemDataSet: a json like object dictionary with problem question set
    """
    targetSubIds = findSpecifySubmissionIds(CONTEST_ID , verdictName , programTypeForInvoker , frameProblemIndex)

    codes=[]
    for id in targetSubIds:
        sourceCode , compilationError , testCases = getSubmittion(CONTEST_ID , id ,False)
        
        if compilationError:
            codes.append({
                "language":programTypeForInvoker,
                "sourceCode":sourceCode,
                "verdict":verdictName,
                "testCaseName:":str(verdictName)+str(id),
                "CodeForceProblemId":frameProblemIndex,
                "targetCaseNums":[]
            })
            continue

        elif verdictName != "OK":
            testCases = [ case for case in testCases if not case["verdict"] == verdictName ]
            if len(testCases) == 0 :
                continue

        targetCaseNums=[]
        for case in testCases:
            findcase=False
            for  probcase in problemDB[frameProblemIndex]:
                if probcase["id"] == case["id"]:
                    findcase=True
                    break
            
            if findcase:
                targetCaseNums.append(case[id])
        
        if len(targetCaseNums) == 0:
            continue
        
        codes.append({
            "language":programTypeForInvoker,
            "sourceCode":sourceCode,
            "verdict":verdictName,
            "testCaseName:":str(verdictName)+str(id),
            "CodeForceProblemId":frameProblemIndex,
            "targetCaseNums":targetCaseNums
        })
    return codes


    



if __name__ == "__main__":
    #print(findSpecifySubmissionIds(1265,"OK","c.gcc11"))
    #getSubmittion(132,61898597)
    #print(buildProblemList(1169))
    problemDB = buildProblemList(1265)
    getProcessedCode(1265 , "OK" ,"c.gcc11" , "E" , problemDB)
    pass