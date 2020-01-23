import scriptHandler as sHandler


def parseUsersFile():
        userDict = {}

        with open('./config/users.txt', 'r') as userFile:
                x = 0
                for line in userFile:
                        dictEntry = {
                                "username": "",
                                "email": "",
                                "labels": [],
                                "ticketCounter": 0
                        }
                        lineArray = (line.strip().split())
                        fullName = (lineArray[0] + " " + lineArray[1])
                        dictEntry["username"] = lineArray[2]
                        dictEntry["email"] = lineArray[3]

                        if len(lineArray) > 4:
                                for label in range(4, len(lineArray)):
                                        dictEntry["labels"].append(lineArray[label])

                        userDict[fullName] = dictEntry
                        x += 1
                sHandler.sysData.assignData(dataType="users", data=userDict)
        sHandler.sysLog.logger.debug("Read config/users.txt")


def parseExceptionsFile():
        import re

        emailArray = []
        subjectArray = []
        emailRe = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")

        with open('./config/exceptions.txt', 'r') as exceptionsFile:
                for line in exceptionsFile:
                        if emailRe.match(line) == None:
                                subjectArray.append(line.strip())
                        else:
                                emailArray.append(line.strip())
        sHandler.sysData.assignData(dataType="exceptionsEmail", data=emailArray)
        sHandler.sysData.assignData(dataType="exceptionsSubject", data=subjectArray)
        sHandler.sysLog.logger.debug("Read config/exceptions.txt")


def parseTemplateFile():
        with open('./config/template.txt', 'r') as templateFile:
                templateString = templateFile.read()
        sHandler.eComposer.template = templateString
        sHandler.sysLog.logger.debug("Read config/template.txt")


def parseKeywordsFile():
        keywordDict = {}
        with open('./config/keywords.txt', 'r') as keywordFile:
                x = 0
                for line in keywordFile:
                        dictEntry = []
                        lineArray = (line.strip().split())

                        dictKey = lineArray[0]
                        for keyword in lineArray[1:]:
                                if "_" in keyword:
                                        multiWord = keyword.replace("_", " ")
                                        dictEntry.append(multiWord)
                                else:
                                        dictEntry.append(keyword)

                        keywordDict[dictKey] = dictEntry
                        x += 1
        sHandler.sysData.assignData(dataType="keywords", data=keywordDict)
        sHandler.sysLog.logger.debug("Read config/keywords.txt")


def confirmConfigFiles():
        import os

        fileList = ["exceptions.txt", "keywords.txt", "template.txt", "users.txt"]
        finalList = fileList.copy()

        for filename in fileList:
                if filename in os.listdir("./config"):
                        finalList.remove(filename)

        if len(finalList) >= 1:
                missingFiles = ", ".join(finalList)
                sHandler.sysLog.logger.error("Files missing from config (" + missingFiles + ")")
                input("ERROR: Files missing from config (" + missingFiles + ")\n\nPress any key to continue. . .")
                quit("ERROR: Files missing from config (" + missingFiles + ")")
        else:
                sHandler.sysLog.logger.info("Config files located")
