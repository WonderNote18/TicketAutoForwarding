
# Autoforward Ticket Script

## Execution 

**[In Terminal]**
main.py name@email.com username password email@trello.com

## Description

This program is designed to work with Trello to create tickets on a pre-configured board and an email created from Trello to add
new tickets to the Board. This program also uses Outlook Exchange to read emails and create tickets based on differences in the inbox every
X seconds, and sends an automatic reply to the sender of the ticket of the Subject of the email, and the User assigned to the ticket. The user of
the program can also input commands to read system information, recent log information, or to stop executing the program. There is also
a log file created every day to keep track of all activities made inside the program, as well as any user input.

To execute this script, it requires an Outlook Exchange email to read information from, a Username and Password that has access to
the Inbox, and the Trello email that will be sending tickets to your Board. If this is not presented, the program will NOT execute.

The program also utilizes easily configurable .txt files located in the "./config" folder to set Trello User information, an HTML template
to be used for the reply to the sender, a list of exceptions by Email Address and Subject Topic to prevent certain emails from becoming tickets, 
and a list of Trello Labels with their appropriate keywords/most commonly used words in the subject/body of the email. 

**PLEASE MAKE SURE YOU RESTART THE PROGRAM AFTER ANY CHANGES MADE TO THE CONFIG FILES**

The user can input commands in the console that pops up after execution. To find out what commands are available, type "HELP" or "H".

Once the time on the running PC turns past 9PM, the program will stop turning in tickets until 6AM the following day. The program will
also create a new log file for the new day to keep files and logs organized.

## File Information
### users.txt

> firstName lastName trelloUsername email@address.com trelloLabel1 trelloLabel2 ...


### template.txt 


> [insert template to notify sender of email that ticket is being worked on]

> [template will have placeholder text {insert_subject_here} to be replaced with Subject of sender's email]

> [template will have placeholder text {insert_name_here} to be replaced with Full Name of User assigned to ticket]

### exceptions.txt 

>exception1@email.com

>exception.2@email.com

>subject1

>email_subject2

### keywords.txt

>trelloLabel1 keyword1 keyword2 ...

>trelloLabel2 key_word3 key_word_4 ...

[keywords with multiple words will be written with underscores[_] in place of spaces (i.e. "return_voucher", "OMNI_Home")]

[Case sensitivity will not matter - function will check in all lowercase]

### main

Reads command line arguments and passes through to scriptHandler.boot() and main() if arguments are valid.

### startup

Scripts that run on startup that read the files in the "config" folder, and place into class variables to be used in the main program.

>parseUsersFile() reads the text file "users.txt" and creates a dictionary based on the User's name, username, labels that they can work on, and 
number of tickets the user has received.

>parseExceptionsFile() reads the text file "exceptions.txt" and adds each email address into a ordered list

>parseTemplateFile() reads the text file "template.txt" and stores into a str variable

>parseKeywordsFile() reads the text file "keywords.txt" and creates a dictionary based on the type of label and the keywords associated with it. 
Keywords that are composed of multiple words (ex. "Omni Home", "Direct Ship") have spaces replaced with the underscore (_) character, and will 
be treated as a multi-word keyword

>confirmLogFile() checks to see if a log made for the current day was made in the "logs" folder. If not, it will create a MM-DD-YYYY.log file to 
record all script actions.

>confirmConfigFiles() checks to see if all 4 config files (exceptions, keywords, template, users) in the folder. Stops program if not found

### emailParser

Reads the Body and Subject of the sent email to determine what Users will be assigned to the ticket, and what Labels the ticket will be categorized as.

All functions are held inside the "EmailemailParser" Class, with init values to hold the subject, body, related label data, assigned users, and assigned labels.

>initData() is used to initialize class variables to the email's data, and resets labelData, assignedUsers, and assignedLabels to their defaults.

>main() controls the 3 sections of email parsing: scrape_main(), init_main(), and assign_main(). Once completed, it returns the parsed information of
the subject and body of the email, and the Users and Labels assigned to the ticket.

>scrape_main() controls 2 functions of data scraping from the subject and body via scrapeEmail()

>init_main() controls 2 ticketInitLabels() and ticketInitUsers() to init the assignedUsers and assignedLabels variables with info based directly
from the text itself, which can be considered "raw data" from the email.

>assign_main() is the final step for parsing information. It first runs ticketAssignLabels() to determine if the ticket can be assigned to a selected
User who doesn't have the most tickets assigned to them by removing the maxTicket User and using the remaining Users' assignable labels to see if 
the remaining Users can accomplish the ticket without needing the maxTicket User.

>If it can, then it runs ticketAssignUsers() by pulling the remaining User list to assign to the ticket, creating a copy of the list, and checking
once again to see if the users can accomplish the task.
If it cannot, it runs ticketAssignUsers() by pulling the full User list and runs the checks if it can accomplish the task with the Users provided. If it
can't, even though it's using the full User list, it assigns it anyway and makes a log of the error.

### composer

Composes the body and subject of the email to be used in the emailer's composeEmailToTicketing() function.

All functions are held inside the "EmailComposer" Class, with init values to hold the template text, email subject and body, list of users assigned,
and a Regular Expression used to find the placeholder text within the HTML file and edit with values from the Class.

>main() is the main handler for the composer module that runs through 2 parts: initComposer() to set the local variables, and editTemplate() to change
the placeholders in the HTML. Once completed, it returns the composed body and subject.

>initComposer() initializes the composer with the body and subject of the email, and the assigned Users of the ticket.

>editTemplate() uses Regular Expressions to substitute the placeholders in the template with the subject of the email, and the names of the assigned Users
of the ticket.

### emailer.

Script that reads emails coming into inbox and is able to send emails out to Trello and to the Original Sender.
Emails received have data separated and sent to emailParser.py to be calculated. 

All functions are held inside the "EmailData" Class, with init values to hold the credentials and account for Outlook Exchange, the Trello Ticketing
email to be used to submit tickets, and the most recent email ID from the Outlook Inbox.

>initData() is used to initialize the Outlook Inbox at the start of the program as well as setting the ticketingEmail, and finding the Email ID of the
most recent email in the Inbox.

>checkEmail() is the main function used to find a match of the recent email ID saved in the class, and all new emails made after it will be made into
tickets. It first searches through the first 3-6 emails to see if there are new emails by using checkEmailInbox() which will return True/False if the
most recent email was found in that search. If not, the range is increased and searches again until it reads the 15th+ email. If it reaches the limit
AND is unable to find a new email, it sets the first item in the emailList to be the recent email, and returns the emailList to be parsed by the emailParser

>checkEmailInbox() is the secondary function used to find a match of the recent email ID saved in the class. In the range specified, it will look through
the Inbox to see if it can find the recentEmail. If it's not a match AND doesn't have any of the exceptions in the email address/subject, it gets
added to a list of emails to-be-ticketed. If it is a match, the program sends the list to checkEmail() to send out to the emailParser.

>composeEmailToSender() creates and sends an email back to the Original Sender and Assigned Users notifying of the ticket being created. It uses the
HTML template found in "template.txt" to craft the email, and substitutes the placeholders with their appropriate values.

>composeEmailToTicketing() creates and sends an email to the Trello Email to create the ticket. The ticketing email adds Send-To information as well as
the original Subject onto the body of the email, and submits the email out to the Trello Ticketing email.

### scriptHandler


Contains all classes to be used during the program, handles the main functionality of the program, provides organized execution to ensure the process
of creating a ticket is completely fulfilled.

>cls() is used whenever the screen needs to be cleared.

>boot() is used during startup to run through the setup module and assign data to the SystemData Class.

>main() initializes the emailer class via command line arguments, and runs two threads (input, background) to run the program.

>mainEmailQuery() is the main handler for the program. While the program is running, it uses the emailer's checkEmail() function to search for new emails.
If the function returns False, it waits anywhere from 1.5 - 4 minutes to check for a new email.
If the function returns False, AND the current time is past 9PM, the program waits until 6AM to parse any new emails.
Otherwise, for every new email found, the emailParser module executes initData() to take in the email's raw data, and run through its' main() function to 
parse the data into local variables.
The local variables created from the emailParser is used towards the emailer's composeEmailtoTicketing() function to create the ticket,
The composer's main() function is then called to create the email used to create an automatic reply back to the sender via composeEmailToSender()
Once completed, the function adds to each User's ticketCounter variable by 1, as well as the SystemData's emails handled variable.
IF SystemData.running IS FALSE, THE FUNCTION WILL NO LONGER SEARCH FOR EMAILS.
The function is recursive, meaning after all has been checked and completed, it will continually execute itself until no longer running.

>mainInputQuery()is the main input handler for the program. On the console for the program, it waits for the User to input a command from its' list of
commands. 
If "HELP" is selected, MIQ_Help() is called to print a list of commands.
If "SYSTEM" is selected, it prints all System Information found in the SystemData class.
If "LOG" is selected, MIQ_RecentLog() is called to print the past 45 entries in the system log to the most recent entry.
If "QUIT" is selected, it switches the system's Running flag to False and quits the function.
The function is recursive, meaning after all has been checked and completed, it will continually execute itself until no longer running.

## scriptClasses

Contains two classes that handle System Information related to the program, and logging information and actions to the .log file.

All System Info-related functions are held inside the "SystemData" class, initialized to hold information from the "startup" module, and system info such
as start time, runtime, if the program is running and how many emails have been handled.

All Logging-related functions are held inside the "SystemLogger" class, initialized to contain the logging settings, formats, levels of logging,
and filenames.

>assignData() is used during startup to enter in values related to the type of data proposed (dataType "users" inputs user data, etc.).

>updateLoggingFileDaily() closes the logging file for the day and creates a new file for the upcoming day.