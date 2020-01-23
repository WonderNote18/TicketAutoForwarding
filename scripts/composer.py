import scriptHandler as sHandler
import re

class EmailComposer:
        def __init__(self):
                self.template = sHandler.sysData.templateData
                self.subjectRegex = re.compile(r"\{insert_subject_here\}")
                self.userRegex = re.compile(r"\{insert_name_here\}")
                self.subject = None
                self.responseBody = None
                self.users = None
        
        def main(self, subject, users):
                self.initComposer(subject=subject, users=users)
                self.editTemplate()
                sHandler.sysLog.logger.debug("Composed return email for [" + self.subject + "]")
                return (self.responseBody, self.subject)
        
        def initComposer(self, subject=None, users=None):
                self.subject = subject
                self.users = users
        
        def editTemplate(self):
                self.responseBody = self.subjectRegex.sub(self.subject, self.template)
                
                userList = []
                for user in self.users:
                        userList.append(user)
                        
                if len(self.users) == 2:
                        self.users = " and ".join(userList)
                elif len(self.users) > 2:
                        self.users = ", ".join(userList[0:-1])
                        self.users += ", and " + userList[-1]
                else:
                        self.users = userList[0]
                
                self.responseBody = self.userRegex.sub(self.users, self.responseBody)
                self.subject = "Ticket Received: " + self.subject
                        
