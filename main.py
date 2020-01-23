# Execution argument example: ./main.py name@email.com username password email@trello.com

import sys
import re
sys.path.append("./scripts")

import scriptHandler

emailRegex = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")

if __name__ == "__main__":
        if (emailRegex.match(sys.argv[1]) != None and 
        type(sys.argv[2]) == str and 
        type(sys.argv[3]) == str and 
        emailRegex.match(sys.argv[4]) != None):
                scriptHandler.boot()
                scriptHandler.main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
        else:
                input("Useage: main.py name@email.com username password email@trello.com\n\nPress any key to continue. . .")
                quit("Useage: main.py name@email.com username password email@trello.com")
