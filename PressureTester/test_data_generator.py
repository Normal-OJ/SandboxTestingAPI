import os
import json
def generate_easy_case(name):
    os.mkdir(name)
    os.chdir(name)

    with open("settings.json" , "w") as fp:
        settings = {
            "languageId":0,
            "problemId":name,
            "expectedResult":[
                {
                    "status": 0
                }
            ]
        }
        fp.write(json.dumps(settings , indent=4))
    os.system("cp ../../easy_source.zip source.zip")
    os.system("cp ../../easy_testcase.zip testcase.zip")
    os.chdir("..")

def generate_case(types , nums , name):
    if types == "easy":
        os.chdir("TestCases")
        for i in range(nums):
            generate_easy_case(name + str(i))
        os.chdir("..")

if __name__ == "__main__":
    generate_case("easy" , 100 ,"Yee")
