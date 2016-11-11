# coding: utf-8

#!/usr/bin/python

import sys, argparse
####################################################################################
##                                  INFORMATION
####################################################################################
##   Developed by: Steven Johnson
##
##   Last Updated: 11/13/2013 4:00AM PST
##
##   Description: Auto-Delete Watched Items In Plex
##
##   Required Configurations:
##      - PC       (Blank = AutoDetect  |  W = Windows  |  L = Linux/Unix/MAC )
##      - Host     (Hostname or IP  | Blank = 127.0.0.1)
##      - Port     (Port  |  Blank = 32400)
##      - Section  (Section aka Library 1 2 3 varies on your system  |  Blank = 1)
##      - Delete   (1 = Delete  |  Blank = 0 (For Testing or Review))
##      - Shows    ( ["Show1","Show2"]; = Kept Shows OR [""]; = DEL ALL SHOWS )
##      - OnDeck   ( 1 = Keep If On Deck  |  Blank = Delete Regardless if onDeck  )
##
####################################################################################
####################################################################################

def main(argv):
    global FileCount
    global DeleteCount
    global DeleteFileList
    global FlaggedCount
    global OnDeckCount
    global ShowsCount
    global ServerToken
    global SlackUrl
    global gPC
        
    FileCount = 0
    DeleteCount = 0
    DeleteFileList = "\n"
    FlaggedCount = 0
    OnDeckCount = 0
    ShowsCount = 0
    
    
    gPC = ""
    Host = ""
    Port = ""
    Section = ""
    Delete = ""
    Shows = ""
    OnDeck = ""
    ServerToken = ""
    SlackUrl = ""
    
    parser = argparse.ArgumentParser(description="arguments")
    
    parser.add_argument('-t', help='W Windows, L Linux', default="", required=False)
    parser.add_argument('-i', help='IP Address', default="", required=False)
    parser.add_argument('-p', help='Port 32400', default="", required=False)
    parser.add_argument('-s', help='Library ID 1,2,3,4', default="1", required=False)
    parser.add_argument('-d', help='1 = Delete, 0 = Test', default="0", required=False)
    parser.add_argument('-k', help='Server Token, will try to read from: ./token', default="", required=False)
    parser.add_argument('-u', help='Slack WebHook Url, will try to read from ./slack', default="", required=False)
    
    args = parser.parse_args()
    
    PC = args.t
    Host = args.i
    Port = args.p
    Section = args.s
    Delete = args.d
    ServerToken = args.k
    SlackUrl = args.u

    procdelete(PC, Host, Port, Section, Delete, Shows, OnDeck)

def procdelete(PC, Host, Port, Section, Delete, Shows, OnDeck):
    global FileCount
    global DeleteCount
    global DeleteFileList
    global FlaggedCount
    global OnDeckCount
    global ShowsCount
    global ServerToken
    global SlackUrl
    global gPC
    ####################################################################################
    ##                        NO NEED TO EDIT BELOW THIS LINE
    ####################################################################################
    import os
    import xml.dom.minidom
    import platform
    import re

    ####################################################################################
    ##  Checking URL
    ####################################################################################
    if ServerToken == "":
        tokenfile = open('token', 'r')
        ServerToken = tokenfile.read()
    if SlackUrl == "":
        slackfile = open('slack', 'r')
        SlackUrl = slackfile.read()
    if Host=="":
        Host="htpc"
    if Port=="":
        Port="32400"
    if Section=="":
        Section = "1"
    URL = ("http://" + Host + ":" + Port + "/library/sections/" + Section + "/recentlyViewed" + "?X-Plex-Token=" + ServerToken)
    OnDeckURL = ("http://" + Host + ":" + Port + "/library/sections/" + Section + "/onDeck" + "?X-Plex-Token=" + ServerToken)
    print("----------------------------------------------------------------------------")
    print("                           Detected Settings")
    print("----------------------------------------------------------------------------")
    print("Host: " + Host)
    print("Port: " + Port)
    print("Section: " + Section)
    print("URL: " + URL)
    print("OnDeck URL: " + OnDeckURL)

    ####################################################################################
    ##  Checking Shows
    ####################################################################################
    NoDelete = " | "
    ShowCount = len(Shows)
    print("Show Count: " + str(ShowCount))

    for Show in Shows:
        Show = re.sub('[^A-Za-z0-9 ]+', '', Show).strip()
        if Show=="":
            NoDelete += "(None Listed) | "
            ShowCount -= 1
        else:
            NoDelete += Show + " | "

    print("Number of Shows Detected For Keeping: " + str(ShowCount))
    print ("Shows to Keep:" + NoDelete)

    ###################################################################################
    ##  Checking Delete
    ####################################################################################
    if Delete=="1":
        print("Delete: ***Enabled***")
    else:
        print("Delete: Disabled - Flagging Only")

    if OnDeck=="1":
        print("Delete OnDeck: No")
    else:
        print("Delete OnDeck: Yes")

    ####################################################################################
    ##  Checking OS
    ####################################################################################
    AD = ""
    gPC = PC
    if PC=="":
        AD = "(Auto Detected)"
        if platform.system()=="Windows":
            PC = "W"
            gPC = PC
        elif platform.system()=="Linux":
            PC = "L"
            gPC = PC
        elif platform.system()=="Darwin":
            PC = "L"
            gPC = PC

    ####################################################################################
    ##  Setting OS Based Variables
    ####################################################################################
    if PC=="L":
        print("Operating System: Linux " + AD)
        import urllib2
        doc = xml.dom.minidom.parse(urllib2.urlopen(URL))
        deck = xml.dom.minidom.parse(urllib2.urlopen(OnDeckURL))
    elif PC=="W":
        print("Operating System: Windows " + AD)
        import urllib.request
        doc = xml.dom.minidom.parse(urllib.request.urlopen(URL))
        deck = xml.dom.minidom.parse(urllib.request.urlopen(OnDeckURL))
    else:
        print("Operating System: ** Not Configured **  (" + platform.system() + ") is not recognized.")
        exit()
    print("----------------------------------------------------------------------------")
    print("----------------------------------------------------------------------------")
    print("")

    FileCount = 0
    DeleteCount = 0
    FlaggedCount = 0
    OnDeckCount = 0
    ShowsCount = 0

    ####################################################################################
    ##  Check On Deck
    ####################################################################################
    def CheckOnDeck( CheckDeckFile ):
        global FileCount
        global DeleteCount
        global DeleteFileList
        global FlaggedCount
        global OnDeckCount
        global ShowsCount
        InTheDeck = 0
        for DeckVideoNode in deck.getElementsByTagName("Video"):
            DeckMediaNode = DeckVideoNode.getElementsByTagName("Media")
            for DeckMedia in DeckMediaNode:
                DeckPartNode = DeckMedia.getElementsByTagName("Part")
                for DeckPart in DeckPartNode:
                    Deckfile = DeckPart.getAttribute("file")
                    if CheckDeckFile==Deckfile:
                        InTheDeck += 1
                    else:
                        InTheDeck += 0
        return InTheDeck

    ####################################################################################
    ##  Check Shows And Delete If Configured
    ####################################################################################
    def CheckShows( CheckFile ):
        global FileCount
        global DeleteCount
        global DeleteFileList
        global FlaggedCount
        global OnDeckCount
        global ShowsCount
        FileCount += 1
        CantDelete = 0
        ShowFound = ""
        
        ##  -- CHECK SHOWS --
        for Show in Shows:
            Show = re.sub('[^A-Za-z0-9 ]+', '', Show).strip()
            if Show=="":
                CantDelete = 0
            else:
                if (' ' in Show) == True:
                    if all(str(Word) in CheckFile for Word in Show.split()):
                        CantDelete += 1
                        ShowFound = "[" + Show + "]"
                        ShowsCount += 1
                    else:
                        CantDelete += 0
                else:
                    if Show in CheckFile:
                        CantDelete += 1
                        ShowFound = "[" + Show + "]"
                        ShowsCount += 1
                    else:
                        CantDelete += 0
        
        ## -- Check OnDeck --
        if OnDeck=="1":
            IsOnDeck = CheckOnDeck(CheckFile);
            if IsOnDeck==0:
                CantDelete += 0
            else:
                CantDelete += 1
                ShowFound = "[OnDeck]" + ShowFound
                OnDeckCount += 1
        
        ## -- DELETE SHOWS --
        if CantDelete == 0:
            if Delete=="1":
                print("**[DELETED] " + CheckFile)
                DeleteFileList = DeleteFileList + "**[DELETED] " + CheckFile + "\n"
                os.remove(file)
                DeleteCount += 1
            else:
                print("**[FLAGGED] " + CheckFile)
                FlaggedCount += 1
        else:
            print("[KEEPING]" + ShowFound + " " + CheckFile)

    ####################################################################################
    ##  Get Files for Watched Shows
    ####################################################################################
    for VideoNode in doc.getElementsByTagName("Video"):
        view = VideoNode.getAttribute("viewCount")
        if view == '': 
            view = 0
        view = int(view)
        MediaNode = VideoNode.getElementsByTagName("Media")
        for Media in MediaNode:
            PartNode = Media.getElementsByTagName("Part")
            for Part in PartNode:
                file = Part.getAttribute("file")
                if view > 0:
                    if os.path.isfile(file):
                        CheckShows(file);
                    else:
                        print("##[NOT FOUND] " + file)

    ####################################################################################
    ##  Check Shows And Delete If Configured
    ####################################################################################
    summaryText = ""
    summaryText = summaryText + "\n\n"
    summaryText = summaryText + "                Summary -- Script Completed Successfully\n"
    summaryText = summaryText + "----------------------------------------------------------------------------\n"
    summaryText = summaryText + "  Total File Count  " + str(FileCount) + "\n"
    summaryText = summaryText + "  Kept Show Files   " + str(ShowsCount) + "\n"
    summaryText = summaryText + "  On Deck Files     " + str(OnDeckCount) + "\n"
    summaryText = summaryText + "  Deleted Files     " + str(DeleteCount) + "\n"
    summaryText = summaryText + "  Flagged Files     " + str(FlaggedCount) + "\n\n"
    summaryText = summaryText + "----------------------------------------------------------------------------\n"
    print(summaryText)
    print("debug:::")
    print(gPC)
    print(PC)
    
    ####################################################################################
    ##  Send Slack Notification
    ####################################################################################
    if not SlackUrl:
        if gPC=="L":
            print("Operating System: Linux ")
            import urllib2
            slackreq = urllib2.Request(SlackUrl)
            slackreq.add_header('Content-Type', 'application/json')
            jsonText = {'text': summaryText  + DeleteFileList}
            slackResponse = urllib2.urlopen(slackreq, json.dumps(jsonText))
        elif gPC=="W":
            print("Operating System: Windows ")
            import urllib.request
            slackreq = urllib.request.urlopen(SlackUrl)
            slackreq.add_header('Content-Type', 'application/json')
            jsonText = {'text': summaryText  + DeleteFileList}
            slackResponse = urllib.request.urlopen(slackreq, json.dumps(jsonText))
        else:
            print("Operating System: ** Not Configured **  (" + platform.system() + ") is not recognized.")

if __name__ == "__main__":
    main(sys.argv[1:])
