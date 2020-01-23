import logging, datetime, os
import scriptHandler as sHandler


class SystemData:
        def __init__(self):
                self.userData = {}
                self.keywordData = {}
                self.exceptionsEmail = []
                self.exceptionsSubject = []
                self.templateData = ""
                
                self.running = True
                self.ticketSleeping = False
                self.emailsHandled = 0
                self.startTime = datetime.datetime.now().replace(microsecond=0)
                self.upTime = None
        
        def __str__(self):
                self.upTime = datetime.datetime.now().replace(microsecond=0) - self.startTime
                
                userInfo = ""
                keywordInfo = ""
                exceptionsEmailInfo = ""
                exceptionsSubjectInfo = ""

                for key in self.userData.keys():
                        userInfo += "\"" + str(key) + "\"\n"
                for key in self.keywordData.keys():
                        keywordInfo += "" + str(key) + "\n"
                for entry in self.exceptionsEmail:
                        exceptionsEmailInfo += "" + str(entry) + "\n"
                for entry in self.exceptionsSubject:
                        exceptionsSubjectInfo += "\"" + str(entry) + "\"\n"

                sHandler.clsW()
                output = "\t\t====AutoForward====\n\tEmails Ticketed: {}\n\tScript Started on {}\n\tCurrent Running Time: {}\n\n\tUser Information:\n{}\n\n\tLabel Keyword Information:\n{}\n\n\tEmail Exception Information:\n{}\n\n\tSubject Exception Information:\n{}\n".format(
                self.emailsHandled,
                self.startTime.strftime("%m/%d/%Y at [%I:%M:%S %p]"),
                self.upTime,
                userInfo, 
                keywordInfo, 
                exceptionsEmailInfo,
                exceptionsSubjectInfo)
                return output
        
        def assignData(self, dataType=None, data=None):
                if dataType == "users":
                        self.userData = data

                elif dataType == "keywords":
                        self.keywordData = data

                elif dataType == "exceptionsEmail":
                        self.exceptionsEmail = data

                elif dataType == "exceptionsSubject":
                        self.exceptionsSubject = data

                elif dataType == "template":
                        self.templateData = data

class SystemLogger():
        def __init__(self):
                self.logger = logging.getLogger("TicketLogging")
                self.logger.setLevel(logging.DEBUG)

                self.formatter = logging.Formatter("%(asctime)s(%(threadName)s)[%(levelname)s]: %(message)s", "[%I:%M:%S %p]")

                self.consoleHandler = logging.StreamHandler()
                self.consoleHandler.setLevel(logging.DEBUG)

                self.fileDate = datetime.datetime.now().strftime("%m-%d-%Y")
                if (self.fileDate + ".log") not in os.listdir("./logs"):
                        newFile = open("./logs/" + self.fileDate + ".log", 'w')
                        newFile.close()
                self.fileHandler = logging.FileHandler("./logs/" + self.fileDate + ".log", 'a')
                self.fileHandler.setLevel(logging.DEBUG)
                self.fileHandler.setFormatter(self.formatter)

                self.logger.addHandler(self.fileHandler)
        
        def updateLoggingFileDaily(self, newTime):
                self.fileDate = newTime.strftime("%m-%d-%Y")

                self.fileHandler.close()
                self.logger.removeHandler(self.fileHandler)

                newFile = open("./logs/" + self.fileDate + ".log", 'w')
                newFile.close()

                self.fileHandler = logging.FileHandler("./logs/" + self.fileDate + ".log", 'a')
                self.fileHandler.setLevel(logging.DEBUG)
                self.fileHandler.setFormatter(self.formatter)

                self.logger.addHandler(self.fileHandler)
