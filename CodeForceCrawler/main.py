import requests
import bs4
import json
import random
import os
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
    "OK":0,
    "WRONG_ANSWER":1,
    "RUNTIME_ERROR":5,
    "TIME_LIMIT_EXCEEDED":3,
    "MEMORY_LIMIT_EXCEEDED":4,
    "COMPILATION_ERROR":2
}
programTypeForInvokerList=[
    "anyProgramTypeForInvoker"
    "c.gcc11",
    "cpp.g++11",
    "python.3"
]
programTypeForInvoker2programType={
    "c.gcc11":0,
    "cpp.g++11":1,
    "python.3":2
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
    print(f"try to accuire submission {SUBMISSION_ID}")
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
        print("returned body:")
        print(res.text)
        return None
    ses.close()
    data=dict(json.loads(res.text))
    print("sucess~~")
    sourceCode=data["source"]
    testCaseNum=int(data["testCount"])
    testCases=[]

    if getTestCase == True:
        # extracting data
        for i in range(1,testCaseNum+1):
            if str(data["input#"+str(i)]).find("...")!=-1 or str(data["answer#"+str(1)]).find("...")!=-1:
                continue
            testCases.append({
                "input":str(data["input#"+str(i)]).replace("\r",""),
                "output":str(data["answer#"+str(1)]).replace("\r",""),
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
    print("building problem list...")
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
    print("done !!!")
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
        
        if compilationError == True:
            codes.append({
                "language":programTypeForInvoker,
                "sourceCode":str(sourceCode).replace("\r" , ""),
                "verdict":verdictName,
                "testCaseName":str(verdictName)+str(id),
                "CodeForceProblemId":frameProblemIndex,
                "targetCaseNums":[]
            })
            continue

        elif verdictName != "OK":
            _testCases =[]
            for case in testCases:
                if case["verdict"] == verdictName:
                    _testCases.append(case)
            
            testCases = _testCases
            if len(testCases) == 0 :
                continue

        targetCaseNums=[]
        for case in testCases:
            findcase=False
            for  probcase in problemDB[frameProblemIndex]:
                if probcase["num"] == case["num"]:
                    findcase=True
                    break
            
            if findcase:
                targetCaseNums.append(case["num"])
        
        if len(targetCaseNums) == 0:
            continue
        
        codes.append({
            "language":programTypeForInvoker,
            "sourceCode":str(sourceCode).replace("\r",""),
            "verdict":verdictName,
            "testCaseName":str(verdictName)+str(id),
            "CodeForceProblemId":frameProblemIndex,
            "targetCaseNums":targetCaseNums
        })
    return codes
def create_file_suffix_by_lang(lang):
    if lang == "c.gcc11":
        return ".c"
    elif lang == "python.3":
        return ".py"
    elif lang == "cpp.g++11":
        return ".cpp"
    return ""
testCaseDict={}
def build_test_case_dict(problemDB):
    for i in list(problemDB.keys()):
        testCaseDict.update({i:{}})
        for u in range(len(problemDB[i])):
            testCaseDict[i].update({problemDB[i][u]["num"]:{
                "input":problemDB[i][u]["input"] , 
                "output":problemDB[i][u]["output"] ,
                "verdict":problemDB[i][u]["verdict"]
            }})

def exportSubmission(submission , metafiles):
    submission = dict(submission)
    os.mkdir(submission["testCaseName"])
    os.chdir(submission["testCaseName"])
    
    with open("settings.json" , "w") as fp:
        fp.write(json.dumps({
            "languageId":programTypeForInvoker2programType[submission["language"]],
            "problemId":submission["testCaseName"],
            "expectedResult":{
                "status": verdict2status[submission["verdict"]]
            }
        }))
    # create src
    os.mkdir("src")
    os.chdir("src")
    with open("main"+create_file_suffix_by_lang(submission["language"]),"w") as fp:
        fp.write(submission["sourceCode"])
    os.chdir("..")
    # create testcase
    os.mkdir("testcase")
    os.chdir("testcase")
    with open("meta.json" , "w") as fp:
        content = {"cases":[]}
        exp = metafiles[submission["CodeForceProblemId"]]
        for _ in range(len(submission["targetCaseNums"])):
            content["cases"].append(exp)
        fp.write(json.dumps(content,indent=4))

    counter=0
    for i in submission["targetCaseNums"]:
        os.mkdir(str(counter))
        os.chdir(str(counter))
        with open("in" , "w") as fp:
            fp.write(testCaseDict[submission["CodeForceProblemId"]][i]["input"])
        with open("out" , "w") as fp:
            fp.write(testCaseDict[submission["CodeForceProblemId"]][i]["output"])
        counter+=1
        os.chdir("..")
    os.chdir("..")
    os.chdir("..")


if __name__ == "__main__":
    #print(findSpecifySubmissionIds(1265,"OK","c.gcc11"))
    #getSubmittion(132,61898597)
    #print(buildProblemList(1169))
    problemDB = buildProblemList(1265)
    build_test_case_dict(problemDB)
    os.mkdir("TestCases")

    for ver in verdictNameList[1:]:
        for p_type in programTypeForInvokerList[1:]:
            for problemId in list(problemDB.keys()):
                print(f"try to build {ver} case written in {p_type} in problem {problemId}")
                submits = getProcessedCode(1265 , ver ,p_type , problemId , problemDB)
                metafile = {}
                with open("meta_conf.json","r") as fp:
                    js_f=""
                    for i in fp.readlines():
                        js_f += i

                    metafile = json.loads(js_f)
                
                # export submissions
                os.chdir("TestCases")
                for sub in submits:
                    exportSubmission(sub,metafile)
                print(f"finish building {ver} case written in {p_type} in problem {problemId}")
                os.chdir("..")