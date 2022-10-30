# -*- coding: cp1252 -*-
import tkinter # note that module name has changed from Tkinter in Python 2 to tkinter in Python 3
import os 
from tkinter import *
from tkinter import messagebox
import tkinter.font as tkFont
import argparse
import sys


# dir_path = os.path.dirname(os.path.realpath(__file__))

# ---------------------------------------- Functions ------------------------------------------------------------

def center(toplevel):
    toplevel.update_idletasks()
    w = toplevel.winfo_screenwidth()
    h = toplevel.winfo_screenheight()
    size = tuple(int(_) for _ in toplevel.geometry().split('+')[0].split('x'))
    x = w/2 - size[0]/2
    y = h/2 - size[1]/2
    toplevel.geometry("%dx%d+%d+%d" % (size + (x, y)))

def ReadWorkpath() :
    print ("Settingsfile is : " + os.getcwd() + "/settings.dat")           
    if os.path.exists("settings.dat")==False:        
        print("there is no settings file")    
        file = open('settings.dat', 'w')
        file.write(os.getcwd())
        file.close
        return os.getcwd()
    else :
        file = open('settings.dat', 'r')
        tmp =  file.readline().rstrip()
        file.close
        return tmp
    
def FileGetExt(filename) :
    tmpstr=filename.split('.')
    n=len(tmpstr)
    if (n==1) : 
        return ""            
    return (tmpstr[n-1])

def FileGetNameWoExt(filename) :
    tmpstr=filename.split('.')
    n=len(tmpstr)
    if (n==1) : 
        return ""            
    return (tmpstr[0])

def GetCurFolder(path) :
    tmpstr=path.split(os.sep)
    n=len(tmpstr)
    if (n==1) : 
        return ""            
    return (tmpstr[n-1])
    
def IsVidFile(filename) :       
    if allowedVidFileExt.count(FileGetExt(filename))==0 :            ## super einfach .. wenn der string in der liste vorkommt isses nen vid
        return False
    else :
        return True
    
def ReadPlaylist(path) :
    playlistfilepath = path + os.sep + "playlist.txt"
    if (os.path.exists(playlistfilepath)) :
        file = open(playlistfilepath, 'r')
        ret = file.readline()
        file.close
    else :
        ret = ""
    return ret

def ReadTitlesFile(path, titles_dict):
    titlesFilepath = path + os.sep + titles_file_name
    if (os.path.exists(titlesFilepath)) :
        # read everything
        file = open(titlesFilepath, 'r', encoding="utf-8")
        lines = file.readlines()
        file.close
        for line in lines :
            #prepare line
            curline = line.strip().replace('\n','').replace('\r','')
            if len(curline) > 0 :
                x = line.split(" - ")
                titles_dict[x[0]] = x[1] 
            continue        
    return

def convertStringForYoutube(inputStr) :
    return inputStr.replace('\n',"\\n").replace('\r','')       

def convertStringForYoutubeRmNewLines(inputStr) :
    return inputStr.replace('\n',"").replace('\r','')    

def umlautConverter(inputStr) :
    retVal = inputStr 
    x = 0
    while (x < len(retVal)) :
        if retVal[x].encode("utf-8")   == b'\xc3\xa4' :
            if ( (x+1) <= len(retVal)):
                retVal = retVal[:x] + u"\u00e4" + retVal[x+1:]
            else :
                retVal = retVal[:x] + u"\u00e4"
        elif retVal[x].encode("utf-8") == b'\xc3\xb6' :
            if ( (x+1) <= len(retVal)):
                retVal = retVal[:x] + u"\u00f6" + retVal[x+1:]
            else :
                retVal = retVal[:x] + u"\u00f6"
        elif retVal[x].encode("utf-8") ==  b'\xc3\xbc' :
            if ( (x+1) <= len(retVal)):
                retVal = retVal[:x] + u"\u00fc" + retVal[x+1:]
            else :
                retVal = retVal[:x] + u"\u00fc"
        #print(x , retVal[x], retVal[x].encode("utf8"))
        x += 1
    return retVal

def WriteNyuFile(windowHandle, nyufileName, nyuFilePath, title, titleAddy, description) :
    fullVidTitle = umlautConverter(convertStringForYoutubeRmNewLines(title))
    description = umlautConverter(convertStringForYoutube(description))

    #print ("Type: " + str(type(description)))
    description = description[len("description:\\n"):]

    if (titleAddy == "") : 
        pass # do nothing
    else :
        fullVidTitle += (" - " + titleAddy)   

    
    print ("VideoTitle: " + fullVidTitle)
    print ("Description: " + description)
    print ("Writing File: " + nyuFilePath + os.sep + nyufileName)    

    file = open(nyuFilePath + os.sep + nyufileName, 'w', encoding="utf8")
    file.write(fullVidTitle + "\n" + description)
    file.close()
    windowHandle.withdraw()
    windowHandle.quit()
    windowHandle.destroy()
    return
    
def MyCallbacktest2(windowHandle) :
    print ("callback2")
    windowHandle.withdraw()    
    windowHandle.quit()
    windowHandle.destroy()    
    return

def ShowNewVidFrame(vidpath, vidfile) :    
    ## Setup Vars
    nyuFileName = vidfile + ".nyu"
    ## Setup window
    window = tkinter.Tk()
    window.title("Filename: " + vidfile)
    
    
    ## Title >> BaseTitle #Number - Addy
    ## Lets play DarkSouls #17 - Endboss
    l1 = Label(window, text="Title")
    
    strBaseTitle = GetCurFolder(vidpath)
    strVidNumber = " #" + str(FileGetNameWoExt(vidfile))
    # add dynamic title addy
    TitleAddy = StringVar("")    
    print ("searching for " + FileGetNameWoExt(vidfile))
    if (FileGetNameWoExt(vidfile) in titles_dict) :
        print("found Title: " + titles_dict[FileGetNameWoExt(vidfile)])
        TitleAddy.set(titles_dict[FileGetNameWoExt(vidfile)])    
    
    
    lBaseTitle = Label(window, text=strBaseTitle)    
    lVidNumber = Label(window, text=strVidNumber)
    lMinus = Label(window, text=" - ")
    eTitleAddy = Entry(width=70, bd=5, textvariable=TitleAddy)
    
    
    
    
    ## Text
    # myFont = tkFont.Font(family="Arial", size = 14) # Test with other Font Family
    # text = Text(window, height=15, width=80, font=myFont)
    
    text = Text(window, height=15, width=80)
    text.insert(INSERT, u"Filename: " + vidfile + "\n")
    text.insert(INSERT, u"Filepath: " + vidpath + "\n")
    if (playlist != "") :   
        text.insert(INSERT, u"Playlist: " + playlist + "\n")
    else :
        text.insert(INSERT, u"No playlist.txt file found\n")
    text.insert(INSERT, u"Description:"+ "\n")    
    ## Buttons
    bOk = Button(window, text="Ok", command = lambda: WriteNyuFile(
                 window,
                 nyuFileName, 
                 vidpath, 
                 strBaseTitle + strVidNumber, 
                 TitleAddy.get(),
                 text.get('5.0', 'end-1c')
                 ))
    bCancel = Button(window, text="Cancel", command = lambda: MyCallbacktest2(window))    
    
    
    rowC = 0      
    l1.grid(row=rowC, columnspan=4)
    rowC += 1   
    # Title
    lBaseTitle.grid(row=rowC, column=0)
    lVidNumber.grid(row=rowC, column=1)    
    lMinus.grid(row=rowC, column=2)
    eTitleAddy.grid(row=rowC, column=3)
    # Text
    rowC += 1    
    text.grid(row=rowC, column=0, columnspan=4)
    # Buttons   
    rowC += 1    
    bOk.grid(row=rowC, column=0)    
    bCancel.grid(row=rowC, column=3)
    rowC += 1
        
    
    ## paint window
    window.focus_force()
    eTitleAddy.focus()
    # text.focus()        
    center(window)
    window.mainloop()        
    return    
    


# ---------------------------------------- Main ------------------------------------------------------------------
# --- Settings

allowedVidFileExt = ['mp4','flv','ts','m2ts']

# --- glob. Vars

titles_file_name = "Titles.txt"
titles_dict = {}
globStr = ""
workpath = ""
vidPath = ""
playlist = ""
config_auto_clear = False;
config_titles_only_flag = False;

# --- Src

# --- scan args

print ("Anzahl Args : " + str(len(sys.argv)))

parser = argparse.ArgumentParser(description='Nex Youtube Upload Helper GUI - Helpsection for ARGS')
parser.add_argument('--clear', dest='clearFlag', action='store_true', help='No delete confirmation // auto yes clear for target usbstick')
parser.add_argument('--verbose', dest='verboseFlag', action='store_true', help='verbose mode on')
parser.add_argument('--only-with-titles', dest='titlesFlag', action='store_true', help='if and only if there is an entry in Titles.txt - show it')

args = parser.parse_args()

# Args sind in args.<destname von oben> z.b args.name

# copy flags to config
config_auto_clear = args.clearFlag
config_verbose = args.verboseFlag
config_titles_only_flag = args.titlesFlag

if (config_auto_clear == True) :
    print("Autoclear is active -> no confirmation will be needed to delete files")

if (config_titles_only_flag == True) :
    print("using Titles.txt files only mode")

if (config_verbose == True) :
    print("verbose mode on")

################################

# Arbeitsordner finden
workpath = ReadWorkpath()
print ("Workpath : " + workpath)

# Suche nach Dirs
for dir in os.listdir(workpath):     ## dir = der aktuelle Upload ordner !
    curDir = workpath + os.sep + dir
    if curDir[0]=='.' :          ## ignore . files
        print(".")
        continue    
    if "System Volume" in curDir :
        print ("skipping Windows folder: " + curDir)
        continue
    if os.path.isfile(curDir):   ## ignore files
        print ("file ?")         
        continue           
    elif os.path.isdir(curDir):  ## Ordner gefunden ! Jetzt nach Files suchen        
        vidPath = curDir
        print ("Folder: " + vidPath)
        ## Step 1 : Suche nach playlist file        
        playlist = ReadPlaylist(vidPath)
        if (playlist != "") : 
            print("playlist: " + playlist)
        ## Step 2 : Search for Titels.txt
        titles_dict = {} # reset db   
        ReadTitlesFile(vidPath, titles_dict)
        # print (titles_dict)
                
        ## Step 3 : Suche nach VidFiles   
        for vidFile in os.listdir(vidPath):
            if os.path.isfile(vidPath + os.sep + vidFile):   ## file gefunden!
                # print ("File : " + vidFile)   
                if (not(IsVidFile(vidFile))) :
                    continue        ## ignore non vid files
                if ((config_titles_only_flag == True) and (not(FileGetNameWoExt(vidFile) in titles_dict)) ):
                    print ("skip File - no Title: " + vidFile)
                    continue        ## ignore vid files with no title in Titles.txt

                print("Videofile: " + vidFile)
                # Step 3 .. Search for nyu- upload settings file
                nyufileName = vidFile + ".nyu"
                donefileName = vidFile + ".done"
                if (not(os.path.exists(vidPath + os.sep + nyufileName))) :     # Gibt es kein Setting file ?
                     ShowNewVidFrame(vidPath, vidFile)
                else :
                    # nyu file existiert .. evtl auch schon ein done file ?
                    if (os.path.exists(vidPath + os.sep + donefileName)) :
                        # ask user if everything should be deleted
                        result = False
                        # check if autoclear is set
                        if (config_auto_clear == True) :
                            result = True
                        else :
                            rootWindow = tkinter.Tk()
                            center(rootWindow)
                            rootWindow.withdraw()
                            result = messagebox.askyesno("Delete?", vidPath + os.sep + vidFile + " can be deleted .. it is already uploaded", icon='warning')
                            rootWindow.quit()
                            rootWindow.destroy()

                        if result == True :
                            os.remove(vidPath + os.sep + vidFile)
                            os.remove(vidPath + os.sep + nyufileName)
                            os.remove(vidPath + os.sep + donefileName)
                        else :
                            pass
            else :
                print ("kein file " + vidFile)            
    else :                  ## alles andere ignon
        continue    

  
exit()

