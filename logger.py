import datetime
import sqlite3


currentDateTime = datetime.datetime.now()

con = sqlite3.connect('log.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
c = con.cursor()
try:
    c.execute("DROP TABLE Users")
    c.execute("DROP TABLE Events")
except:
    pass

createUserDB = "CREATE TABLE IF NOT EXISTS Users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)"
c.execute(createUserDB)

createEventLog = "CREATE TABLE IF NOT EXISTS Events (id INTEGER PRIMARY KEY AUTOINCREMENT, UserID INTEGER NOT NULL, event TEXT, data TEXT, Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (UserID) REFERENCES Users(UserID))"
c.execute(createEventLog)

addUserQuery = "INSERT INTO Users(name) VALUES (?)"
def addUser(name: str):
    c.execute(addUserQuery, (name,))
    con.commit()


addEventQuery = "INSERT INTO Events(UserID, event, data) VALUES (?, ?, ?)"
def logEvent(UserID: int, event: str, data=None):
    c.execute(addEventQuery, (UserID, event, data))
    con.commit()



def getUserID(name: str):
    c.execute("SELECT id FROM Users WHERE name=(?)", (name, ))
    result = c.fetchone()
    return (result if (result == None) else result[0])


if (getUserID("System") == None):
    addUser("System")

def end():
    con.commit()
    con.close()
    
