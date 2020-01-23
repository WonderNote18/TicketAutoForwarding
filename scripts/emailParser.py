import re
import scriptHandler as sHandler


class EmailParser:
    def __init__(self):
        self.senderName = None
        self.senderEmail = None
        self.subject = None
        self.body = None
        self.labelData = {}
        self.assignedUsers = {}
        self.assignedLabels = []

    def initData(self, emailSender, emailSubject, emailBody):
        if len(emailSubject) <= 1:
                bodySplit = emailBody.split()
                bodyString = " ".join(bodySplit[0:5])
                self.subject = bodyString + "..."
        else:
                self.subject = emailSubject
        
        self.body = emailBody
        self.labelData = {}
        self.senderName = emailSender.name
        self.senderEmail = emailSender.email_address
        self.assignedUsers = {}
        self.assignedLabels = []
        
    def main(self):
        self.scrape_main()
        self.init_main()
        self.assign_main()
        sHandler.sysLog.logger.debug("Scraped and assigned users and labels from email: " + self.subject)
        return (self.subject, self.body, self.assignedUsers, self.assignedLabels)
                
    def scrape_main(self):
        self.scrapeEmail(text=self.subject, textType="subject")
        self.scrapeEmail(text=self.body, textType="body")
    
    def init_main(self):
        self.ticketInitLabels(self.labelData, self.assignedLabels)    
        self.ticketInitUsers(self.assignedLabels, sHandler.sysData.userData, self.assignedUsers)
    
    def assign_main(self):
        (usersWithoutMax, labelsWithoutMax) = self.ticketAssignLabels(self.assignedLabels, self.assignedUsers)

        if labelsWithoutMax == self.assignedLabels:
            self.ticketAssignUsers(usersWithoutMax, self.assignedLabels)
        else:
            self.ticketAssignUsers(self.assignedUsers, self.assignedLabels)
            
        finalUsers = []
        sHandler.sysLog.logger.debug("User Dict before turning into list: " + str(self.assignedUsers))
        for user in self.assignedUsers.keys():
            finalUsers.append(user)
        self.assignedUsers = finalUsers.copy()
        sHandler.sysLog.logger.debug("User Dict after turning into list: " + str(self.assignedUsers))

    def scrapeEmail(self, text="", textType=""):

        if textType == "body":
            oecExclude = "\r\n\r\n\r\n\r\n---\r\n\r\nNew Outlook Express and Windows Live Mail replacement - get it here:\r\n\r\nhttp://www.oeclassic.com/\r\n\r\n\r\n\r\n"
            oecExclude2 = "\r\n\r\n---\r\nNew Outlook Express and Windows Live Mail replacement - get it here:\r\nhttp://www.oeclassic.com/\r\n\r\n"
            if oecExclude in self.body:
                self.body = self.body.replace(oecExclude, " ")
            if oecExclude2 in self.body:
                self.body = self.body.replace(oecExclude2, " ")
                
        singleWords = text.lower().split()
            
        for label, keywords in sHandler.sysData.keywordData.items():
            for keyword in keywords:
                if len(keyword.split()) == 1:
                    self.keywordCountChecker(keyword, label, singleWords)
                else:
                    self.keywordCountChecker(keyword, label, text.lower())
    
    def keywordCountChecker(self, keyword, label, text):
        if keyword in text:
            if label not in self.labelData.keys():
                self.labelData[label] = 0
            self.labelData[label] += text.count(keyword)
    
    def ticketInitLabels(self, labelData, assignedLabels):
        try:
            maxLabel = max(labelData, key=labelData.get)
            maxLabelAmt = labelData[maxLabel]
            assignedLabels.append(maxLabel)
        except ValueError:
            maxLabel = None
            maxLabelAmt = 0

        if maxLabelAmt > 3:
            for label, counter in labelData.items():
                if label != maxLabel:
                    if counter in range (maxLabelAmt - 4, maxLabelAmt):
                        if label not in assignedLabels:
                            assignedLabels.append(label)
            labelsString = " ".join(assignedLabels)
            sHandler.sysLog.logger.debug("Found keywords in email for labels: {" + labelsString + "}")
        elif maxLabelAmt == 0:
            assignedLabels.append("Miscellaneous")
            sHandler.sysLog.logger.debug("No keywords found in email. Assigning label {Miscellaneous}")
        else:
            labelsString = " ".join(assignedLabels)
            sHandler.sysLog.logger.debug("Found keyword in email for label: {" + labelsString + "}")
    
    def ticketInitUsers(self, assignedLabels, userData, assignedUsers):
        for ticketLabel in assignedLabels:
            for user, data in userData.items():
                if ticketLabel in data['labels']:
                    if user in assignedUsers.keys():
                        assignedUsers[user].append(ticketLabel)
                    else:
                        assignedUsers[user] = [ticketLabel]
        usersString = "["
        for user in assignedUsers.keys():
            if user in userData.keys():
                assignedUsers[user].append(userData[user]['ticketCounter'])
                usersString += user + " "
        sHandler.sysLog.logger.debug("Users associated with labels: " + usersString)

    def ticketAssignLabels(self, assignedLabels, assignedUsers):
        sHandler.sysLog.logger.debug("User Dict at start of AssignLabels: " + str(self.assignedUsers))
        maxUserTicketAmt = max([int(value[-1]) for value in assignedUsers.values()])
        for user, value in assignedUsers.items():
            if maxUserTicketAmt in value:
                maxUser = str(user)
        sHandler.sysLog.logger.debug("User [" + maxUser + "] in selection with most assigned tickets: (" + str(maxUserTicketAmt) + ")")
        usersWithoutMax = assignedUsers.copy()
        labelsWithoutMax = []
        del usersWithoutMax[maxUser]

        for ticketLabel in assignedLabels:
            for user, value in assignedUsers.items():
                if ticketLabel in value:
                    if ticketLabel not in labelsWithoutMax:
                        labelsWithoutMax.append(ticketLabel)

        return (usersWithoutMax, labelsWithoutMax)
    
    def ticketAssignUsers(self, assignedUsers, assignedLabels, flagFinalAttempt=False):
        sHandler.sysLog.logger.debug("User Dict entered for AssignUsers: " + str(self.assignedUsers))
        if len(assignedUsers) == 0:
            sHandler.sysLog.logger.warning("Final attempt reached. Attempting to assign users from original composed list")
            self.ticketAssignUsers(self.assignedUsers, self.assignedLabels, flagFinalAttempt=True)
            return
            
        tempUserCopy = assignedUsers.copy()
        tempLabelsCopy = assignedLabels.copy()
        currentUserLabels = []

        for user, value in tempUserCopy.items():
            currentUserLabels = value[0:-1]
            if currentUserLabels in tempLabelsCopy:
                labelDifference = [label for label in assignedLabels if label not in currentUserLabels]
                tempLabelsCopy = labelDifference.copy()
                if len(labelDifference) == 0:
                    break
            else:
                del assignedUsers[user]
        
        self.assignedUsers = tempUserCopy.copy()
        
        if tempLabelsCopy == assignedLabels and flagFinalAttempt == False:
            sHandler.sysLog.logger.debug("Assigned " + str(self.assignedUsers.keys()) + " to ticket")
        elif flagFinalAttempt == True:
            sHandler.sysLog.logger.warning("Max attempts reached on user assignment.")
        else:
            sHandler.sysLog.logger.warning("Final attempt reached. Attempting to assign users from original composed list: " + str(tempUserCopy))
            self.ticketAssignUsers(self.assignedUsers, self.assignedLabels, flagFinalAttempt=True)

