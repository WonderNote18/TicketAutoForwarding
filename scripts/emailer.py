import os
import datetime
import exchangelib
import scriptHandler as sHandler

class EmailData:
	def __init__(self):
		self.credentials = None
		self.account = None
		self.ticketingEmail = None
		self.recentEmail = None
	
	def initData(self, email, username, password, trelloEmail):
		self.credentials = exchangelib.Credentials(
			username=username,
			password=password
		)
		self.account = exchangelib.Account(
			email,
			credentials=self.credentials,
			autodiscover=True
		)
		self.ticketingEmail = trelloEmail
		self.recentEmail = self.account.inbox.all().order_by('-datetime_received')[0].id

	def checkEmail(self):
		import random

		foundRecentEmail = False
		searchStartRange = 0
		searchEndRange = random.randint(3,6)
		emailList = []
		tempEmailList = []

		while not foundRecentEmail:
			if searchEndRange > 15:
				sHandler.sysLog.logger.debug("Last sent email not found in last " + str(searchEndRange) + " emails. Setting recent email as marker. . .")
				emailList = []
				self.recentEmail = self.account.inbox.all().order_by('-datetime_received')[0].id
				break
			
			(foundRecentEmail, tempEmailList) = self.checkEmailInbox(searchStartRange, searchEndRange)

			searchStartRange = searchEndRange
			searchEndRange += random.randint(3,5)
			emailList += tempEmailList
			tempEmailList = []
		
		if len(tempEmailList) > 0:
			emailList += tempEmailList
		
		if len(emailList) == 0:
			return (False, [])
		else:
			self.recentEmail = emailList[0].id
			sHandler.sysLog.logger.info(str(len(emailList)) + " new emails found.")
			return (True, emailList)
	
	def checkEmailInbox(self, start, end):
		import time
		import random

		emailList = []
		for emailCounter in range(start,end):
			flagSubjectException = False
			flagTextException = False
			
			try:
				selectedEmail = (self.account.inbox.all().order_by('-datetime_received')[emailCounter])
			except:
				time.sleep(random.randint(3,5))
				selectedEmail = (self.account.inbox.all().order_by('-datetime_received')[emailCounter])
			if selectedEmail.subject == None:
			    selectedEmail.subject = " ".join(selectedEmail.text_body.split()[0:5]) + ". . ."

			try:
				print(selectedEmail.text_body)
			except:
				flagTextException = True

			try:
				print(selectedEmail.subject)
			except:
				flagTextException = True

			if selectedEmail.subject == None:
				emailSubject = ""
			else:
				emailSubject = selectedEmail.subject
			subjectWords = emailSubject.lower().split()
			
			for word in sHandler.sysData.exceptionsSubject:
				if word in selectedEmail.subject.lower() or word in subjectWords:
					flagSubjectException=True

			if self.recentEmail == selectedEmail.id:
				return (True, emailList)
			elif selectedEmail.sender.email_address.lower() in sHandler.sysData.exceptionsEmail:
				sHandler.sysLog.logger.info("Email skipped due to exception in email address {}".format(selectedEmail.sender.email_address))
			elif flagSubjectException:
				sHandler.sysLog.logger.info("Email skipped due to exception in subject {}".format(selectedEmail.subject))
			elif flagTextException:
				sHandler.sysLog.logger.info("Email skipped due to unicode characters in subject or body from {}".format(selectedEmail.sender.email_address))
			else:
				emailList.append(selectedEmail)
		return (False, emailList)
	
	def composeEmailToSender(self, sender, body, subject, users):
		msgTemplate=body

		sendToEmails = []
		for user in users:
			if user in sHandler.sysData.userData.keys():
				sendToEmails.append(exchangelib.Mailbox(email_address=sHandler.sysData.userData[user]['email']))
		
		m = exchangelib.Message(
			account=self.account,
			subject=subject,
			body=exchangelib.HTMLBody(msgTemplate),
			to_recipients=sendToEmails
		)

		logoName = "SAS_Logo.jpg"
		with open(logoName, 'rb') as f:
			logoimg = exchangelib.FileAttachment(name=logoName, content=f.read())
			m.attach(logoimg)
		
		m.send()
		sHandler.sysLog.logger.info("Sent ticket confirmation to: " + sender.name + " (" + sender.email_address + ") " + str(users))
		print("\t[LOG] Sent ticket confirmation to: " + sender.name + " (" + sender.email_address + ") " + str(users) + "\n\n>",end='')

	def composeEmailToTicketing(self, sender, to_recipients, cc_recipients, body, subject, labels, users, attachments=[]):
		fromUser = sender.name + " [" + sender.email_address + "]"

		toUsers = "N/A"
		if to_recipients != None:
			toUsers = to_recipients[0].name + " [" + to_recipients[0].email_address + "]"
			if len(to_recipients) > 1:
				for x in range(1, len(to_recipients)):
					toUsers += ", " + to_recipients[x].name + " [" + to_recipients[x].email_address + "]"
		
		ccUsers = "N/A"
		if cc_recipients != None:
			ccUsers = cc_recipients[0].name + " [" + cc_recipients[0].email_address + "]"
			if len(cc_recipients) > 1:
				for x in range(1, len(cc_recipients)):
					ccUsers += ", " + cc_recipients[x].name + " [" + cc_recipients[x].email_address + "]"

		bodyAdd = "###From: {}\n\n###To: {}\n\n###Cc: {}\n\n###Subject: {}\n**════════════════════════════════**\n\n".format(fromUser,
		toUsers,
		ccUsers,
		subject)

		subjectAddSender = sender.name
		subjectAddLabel = ''
		subjectAddUser = ''
		sendToEmails = [exchangelib.Mailbox(email_address=self.ticketingEmail)]

		attList = []
		for file in attachments:
			if isinstance(file, exchangelib.FileAttachment):
				localPath = os.path.join(os.getcwd() + r"\temp", file.name)
				with open(localPath, 'wb') as f:
					f.write(file.content)
				attList.append((file.name, file.content))
		
		for label in labels:
			subjectAddLabel += '#' + label + ' '
		for user in users:
			subjectAddUser += sHandler.sysData.userData[user]['username'] + ' '

		body = bodyAdd + body
		subject = subjectAddSender + " - " + subject + ' ' + subjectAddLabel + subjectAddUser
		m = exchangelib.Message(
			account=self.account,
			subject=subject,
			body=body,
			to_recipients=sendToEmails
		)

		for file in attList:
			localPath = os.path.join(os.getcwd() + r"\temp", file[0])
			m.attach(exchangelib.FileAttachment(name=file[0], content=file[1]))
			os.remove(localPath)
		
		m.send()
		sHandler.sysLog.logger.info("Sent ticket to Trello: " + subject)
		print("\t[LOG] Sent ticket to Trello: " + subject + "\n\n>",end='')

	def composeEndProgramEmail(self):
		endTime = datetime.datetime.now().strftime("%m/%d/%Y at %I:%M:%S %p")
		emailRecipients = [exchangelib.Mailbox(email_address="hector.almanza@sas-shoes.net"),
				   exchangelib.Mailbox(email_address="belinda@sas-shoes.net")]
		emailBody = """POS.TicketingAutoForward Alert
	The script to send tickets to Trello has ended on {}.
	If this has ended prior to 11PM, please look into the logs or most recent emails to determine the cause of the application to end at this time.""".format(endTime)
		m = exchangelib.Message(
			account=self.account,
			subject="POS.TAF ended {}".format(endTime),
			body=emailBody,
			to_recipients=emailRecipients)
		m.send()
