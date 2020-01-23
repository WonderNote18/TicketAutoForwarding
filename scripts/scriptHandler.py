import threading
import os
import sys
import time
import datetime
import startup
from scriptClasses import SystemData, SystemLogger
from emailParser import EmailParser
from emailer import EmailData
from composer import EmailComposer

sysData = SystemData()
sysLog = SystemLogger()
eData = EmailData()
eParser = EmailParser()
eComposer = EmailComposer()

def cls():
        input("\n\nPress any key to continue")
        os.system('cls' if os.name == 'nt' else 'clear')

def clsW():
        os.system('cls' if os.name == 'nt' else 'clear')

def boot():
        sysLog.logger.info("Starting program.")
        startup.confirmConfigFiles()
        startup.parseUsersFile()
        startup.parseKeywordsFile()
        startup.parseExceptionsFile()
        startup.parseTemplateFile()

def main(email, username, password, trelloEmail):
        eData.initData(email, username, password, trelloEmail)

        # TODO: check against sql to run for new emails

        threadEmailQuery = threading.Thread(name='EmailQuery', target=mainEmailQuery)
        #threadInputQuery = threading.Thread(name='InputQuery', target=mainInputQuery)
        threadEmailQuery.start()
        print("AutoForward has booted successfully. Enter \"H\" for a list of commands.\n\n")
        #threadInputQuery.start()
        while True:
                if not threadEmailQuery.isAlive():
                        #threadInputQuery.exit()
                        eData.composeEndProgramEmail()
                        sysLog.logger.warning("System shutting down.")
                        sys.exit()
                time.sleep(0.35)

def mainEmailQuery():
        from random import randrange

        if sysData.running:
                (flagNewEmailFound, emailList) = eData.checkEmail()
                if flagNewEmailFound:
                        sysData.ticketSleeping = False
                        for email in emailList:
                                if email.subject == None:
                                        subjectWords = email.text_body.split()
                                        emailSubject = " ".join(subjectWords[0:5])
                                else:
                                        emailSubject = email.subject
                                
                                print("\t[LOG] Parsing email [" + emailSubject + "] sent from [" + email.sender.name + "]\n\n>",end='')
                                sysLog.logger.info("Parsing email [" + emailSubject + "] sent from [" + email.sender.name + "]")

                                email.text_body = email.text_body.replace(u"\u2018", "'").replace(u"\u2019", "'").replace(u"\u2014", "-").replace("\u2013", "-").replace("\u201c", "\"").replace("\u201d", "\"").replace(u"\u2022", "*").replace(u"\u2024", ".").replace(u"\u2025", "..").replace(u"\u2026", "...").replace(u"\u2639", ":(").replace(u"\u263a", ":)")
                                
                                eParser.initData(email.sender, emailSubject, email.text_body)

                                (subject, body, assignedUsers, assignedLabels) = eParser.main()
                                eData.composeEmailToTicketing(email.sender, email.to_recipients, email.cc_recipients, body, subject, assignedLabels, assignedUsers, attachments=email.attachments)

                                (responseBody, responseSubject) = eComposer.main(subject, assignedUsers)
                                eData.composeEmailToSender(email.sender, responseBody, responseSubject, assignedUsers)
                                
                                for user in assignedUsers:
                                        sysData.userData[user]['ticketCounter'] += 1
                                sysData.emailsHandled += 1
                        mainEmailQuery()
                else:
                        sysData.ticketSleeping = True
                        if datetime.datetime.now().hour >= 23:
                                print("\t[LOG] End of Day. Stopping AutoForward. . ." + sleepTime.strftime("%m/%d/%Y") + "\n\n>",end='')
                                sysLog.logger.info("End of Day.")
                                sys.exit()
                        else:
                                sleepTime = randrange(30, 150, 30)
                                print("\t[LOG] Sleeping for " + str(sleepTime) + " secs / " + str(sleepTime / 60) + " mins.\n\n>",end='')
                                time.sleep(sleepTime)
                        mainEmailQuery()
        else:
                # TODO: Save system info to sql in config
                return

def mainInputQuery():
        inputText = input("\t\t====AutoForward====\n\n>").upper()
        inputChoices = ['Q', 'H', 'S', 'L']
        inputChoicesLong = ['QUIT', 'HELP', 'SYSTEM', 'LOG']

        if sysData.running:
                if inputText == 'Q' or inputText == "QUIT":
                        sysLog.logger.warning("User command: QUIT")
                        if sysData.ticketSleeping == True:
                                print("\n\n\n\nUser has ended program.")
                                sysData.running = False
                                sys.exit()
                        else:
                                print("\n\n\n\nUser has ended program.\n\nDo not close the console window until all background processes have been completed.")
                                sysData.running = False
                                return
                elif inputText == 'H' or inputText == "HELP":
                        MIQ_Help()
                elif inputText == 'S' or inputText == "SYSTEM":
                        sysLog.logger.info("User command: SYSTEM")
                        print(sysData)
                        cls()
                        mainInputQuery()
                elif inputText == 'L' or inputText == "LOG":
                        MIQ_RecentLog()
                else:
                        print("\n\n\tInvalid selection. Type 'HELP' for commands . . .")
                        cls()
                        mainInputQuery()
        else:
                sysLog.logger.warning("Input query ended by EOD.")
                sys.exit()

def MIQ_RecentLog():
        sysLog.logger.info("User command: LOG")
        with open("./logs/" + sysLog.fileDate + ".log", 'r') as sysLogFile:
                output = ""
                fileLines = sysLogFile.readlines()
                fileSize = len(fileLines)

                if fileSize >= 30:
                        for x in range(fileSize-30, fileSize):
                                print(fileLines[x])
                else:
                        for x in range(0,fileSize):
                                print(fileLines[x])
        cls()
        mainInputQuery()

def MIQ_Help():
        sysLog.logger.info("User command: HELP")
        print("""
        [Q] - QUIT
                Exits the program.

        [H] - HELP
                Provides a list of commands to enter.
                Shortname and Longname are provided.

        [S] - SYSTEM
                Prints relevant system information.
                Provides runtime, total emails, etc.
        
        [L] - LOG
                Reads up to the last 45 entries in the current log."""
                )
        cls()
        mainInputQuery()
