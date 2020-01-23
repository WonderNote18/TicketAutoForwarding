@echo off

mode con:cols=75 lines=80
title POS.TicketingAutoForward

:: [Variables]
::	VAR_1 = outlook exchange email
::	VAR_2 = outlook exchange username
::	VAR_3 = outlook exchange password
::	VAR_4 = trello ticketing email

set VAR_1=""
set VAR_2=""
set VAR_3=""
set VAR_4=""

C:\Python34\python.exe "C:\SAS Program Files\POS.TicketingAutoForward\main.py" %1 %VAR_1% %VAR_2% %VAR_3% %VAR_4%