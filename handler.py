from forwardNew import forward
from deleteMails import delete
from Invite import sendInvites
from random import shuffle
from pathlib import Path

hostName=""
hostMail=""
hostPassword=""
gameSubject=""
playerList = {}
playerMapping = {}

statusNumber={
    "OFF\n":-1,
    "Creds given\n":0,
    "Players inputted\n":1,
    "Santees invited\n":2,
    "Players mapped\n":3,
    "Santas invited\n":4,
    "Letters sent\n":5,
}
#takes a dictionary of player objects and returns an assignment

def endGame():
    print("Hope the game went well!")
    open("data.txt","w").write("OFF\n")

def changeStatus(status):
    data = open('data.txt',"r").readlines()
    data[0] = status
    open('data.txt',"w").writelines(data)

def sendLetters():
    global playerList,playerMapping,hostMail,hostPassword
    forward(hostName,hostMail,hostPassword,gameSubject+"-letter",playerList,playerMapping)
    changeStatus("Letters sent\n")

def sendGifts():
    global playerList,playerMapping,hostMail,hostPassword
    reverseMapping={}
    for player in playerMapping:
        reverseMapping[playerMapping[player]] = player
    forward(hostName,hostMail,hostPassword,gameSubject+"-gift",playerList,reverseMapping,GIFT=True)
    

def mapPlayers():
    global playerList,playerMapping
    playerNames = []
    for player in playerList:
        playerNames.append(player)
    shuffle(playerNames)
    for i in range(len(playerNames)):
        playerMapping[playerNames[i]] = playerNames[(i+1)%(len(playerNames))]
    saveMapping(playerMapping)
    changeStatus("Players mapped\n")

def saveMapping(playerMapping):
    f = open("data.txt","a")
    for player in playerMapping:
        f.write(player+":"+playerMapping[player]+"\n")

def inputPlayers():
    print("#####################################")
    print("Hello "+hostName)
    print("Please now enter player credentials(including your own if you are participating)")
    players = {}
    name=""
    email=""
    while True :
        name = input("Player name: ")
        if name=="quit":
            break
        email = input("Player email: ")
        players[name] = email
    savePlayers(players)
    global playerList
    playerList = players
    changeStatus("Players nputted\n") 

def savePlayers(playerList):
    f = open("data.txt","a")
    f.write("Players:"+str(len(playerList))+"\n")
    for player in playerList:
        f.write(player+":"+playerList[player]+"\n")

def inputCredentials():
    name = input("Please enter your name: ")
    email = input("Please enter your email ID: ")
    password = input("Please enter your email password: ")
    gameSubject = input("Enter a uniqe email subject for your game: ")
    return name,email,password,gameSubject

def saveCredentials(hostName,hostMail,hostPassword,subject):
    f = open("data.txt","w")
    f.write("Creds given\n")
    f.write("Name:"+hostName+"\n")
    f.write("Username:"+hostMail+"\n")
    f.write("Password:"+hostPassword+"\n")
    f.write("Subject:"+subject+"\n")
    f.close()

def startNewGame():
    print("Hi there host. Let's start a new game!")
    name,email,password,subject =  inputCredentials()
    saveCredentials(name,email,password,subject)
    return name,email,password,subject

def getCredentials():
    global hostName,hostMail,hostPassword,gameSubject
    f = open('data.txt')
    f.readline()
    hostName = f.readline().split(':')[1].replace("\n","")
    hostMail = f.readline().split(':')[1].replace("\n","")
    hostPassword = f.readline().split(':')[1].replace("\n","")
    gameSubject = f.readline().split(':')[1].replace("\n","")

def getPlayers():
    global playerList
    playerList = {}
    f = open("data.txt","r")
    for i in range(5):
        f.readline()
    
    numOfPlayers = int(f.readline().split(':')[1].replace("\n",""))
    for i in range(numOfPlayers):
        playerInfo = f.readline().split(':')
        playerList[playerInfo[0]] = playerInfo[1].replace("\n","")
    return playerList

def getMapping():
    global playerMapping
    playerMapping={}
    f = open("data.txt","r")
    for i in range(5):
        f.readline()
    numOfPlayers = int(f.readline().split(':')[1].replace("\n",""))
    for i in range(numOfPlayers):
        f.readline()
    for i in range(numOfPlayers):
        playerInfo = f.readline().split(':')
        playerMapping[playerInfo[0]] = playerInfo[1].replace("\n","")
    return playerMapping

def sendSanteeInvites():
    global hostName,hostMail,hostPassword,gameSubject,playerList,playerMapping
    inviteText = Path('invite.txt').read_text()
    inviteWithSubject = inviteText.replace("##Subject##",gameSubject)
    sendInvites(sender=hostMail,password=hostPassword,playerList=playerList,inviteText=inviteWithSubject,subject="Ho Ho Ho...")
    changeStatus("Santees invited\n")

def sendSantaInvites():
    global hostName,hostMail,hostPassword,gameSubject,playerList,playerMapping
    inviteText = Path('santaInvite.txt').read_text()
    inviteWithSubject = inviteText.replace("##Subject##",gameSubject)
    sendInvites(sender=hostMail,password=hostPassword,playerList=playerList,inviteText=inviteWithSubject,subject="Invites!",recipientList=playerMapping)
    changeStatus("Santas invited\n")

def cleanup(subject,FROM=False):
    global hostMail,hostPassword,playerList
    if not FROM:
        delete("Santa",hostMail,hostPassword,subject,mailType='"[Gmail]/Sent Mail"')
        delete("Santa",hostMail,hostPassword,subject,mailType="INBOX")
    else:
        for player in playerList:
            delete("Santa",hostMail,hostPassword,subject+" from "+player,mailType='"[Gmail]/Sent Mail"')
            delete("Santa",hostMail,hostPassword,subject+" from "+player,mailType="INBOX")
def main():
    global hostName,hostMail,hostPassword,gameSubject,playerList,playerMapping
    f = open("data.txt","r")
    counter = 0
    while not f and counter<10:
        open("data.txt","w").write("OFF\n")
        f = open("data.txt","r")
    
    if counter==10:
        raiseException("unable to open data.txt")

    status = statusNumber[f.readline()]    

    if status==-1:
        hostName,hostMail,hostPassword,gameSubject = startNewGame()
    else:
        if status>=0:
            getCredentials()
        if status>=1:
            getPlayers()
        if status>=3:
            getMapping()
    
    ### WE HAVE REQUIRED DATA NOW

    next = int(input("Continue? "))
    while next==1 and status<=5:
        if status==0:
            inputPlayers()
            status=1
        elif status==1:
            print("Inviting Santees")
            sendSanteeInvites()
            status=2
            cleanup("Ho Ho Ho...")
        elif status==2:
            print("Mapping Players")
            mapPlayers()
            status=3
        elif status==3:
            print("Inviting Santas")
            sendSantaInvites()
            status=4
            cleanup("Invites!")
        elif status==4:
            print("Sending Letters")
            sendLetters()
            status=5
            cleanup(gameSubject+"-letter")
        elif status==5:
            print("Sending Gifts")
            sendGifts()
            cleanup(gameSubject+"-gift")
            endGame()
            status=6
        next = int(input("Continue? ")) 


main()
