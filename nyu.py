#!/usr/bin/python3
import tkinter # note that module name has changed from Tkinter in Python 2 to tkinter in Python 3
import os 
from tkinter import *
from scripts.regsetup import description


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
    if os.path.exists("settings.dat")==False:
        print("there is no settings file")    
        file = open('settings.dat', 'w')
        file.write(os.getcwd())
        file.close
        return os.getcwd()
    else :
        file = open('settings.dat', 'r')
        tmp =  file.readline()
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
    tmpstr=path.split('\\')
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
    playlistfilepath = path + "\\playlist.txt"
    if (os.path.exists(playlistfilepath)) :
        file = open(playlistfilepath, 'r')
        ret = file.readline()
        file.close
    else :
        ret = ""
    return ret

def WriteNyuFile(nyufileName, nyuFilePath, title, description) :
    print (test123.get('4.0', 'end-1c'))
    return
    
def MyCallbacktest2() :
    print ("callback2")
    return

def ShowNewVidFrame(vidpath, vidfile) :
    ## Setup window
    window = tkinter.Tk()
    window.title("Filename: " + vidfile)
    
    
    ## Title
    l1 = Label(window, text="Title")
    
    strBaseTitle = GetCurFolder(vidpath)
    lTitle = Label(window, text=strBaseTitle)
    
    ## Text
    text = Text(window, height=15, width=80)
    text.insert(INSERT, "Filename: " + vidfile + "\n")
    text.insert(INSERT, "Filepath: " + vidpath + "\n")
    if (playlist != "") :   
        text.insert(INSERT, "Playlist: " + playlist + "\n")
    else :
        text.insert(INSERT, "No playlist.txt file found\n")
    text.insert(INSERT, "Description:"+ "\n")
    ## Buttons
    bOk = Button(window, text="Ok", command = lambda: MyCallbacktest(text))
    bCancel = Button(window, text="Cancel", command = MyCallbacktest2)    
    
    window.focus_force()
    l1.pack()   
    lTitle.grid(row=0, column=0)
    lTitle.grid(row=0, column=1)
    lTitle.grid(row=0, column=2)
    text.focus()
    text.pack()   
    bOk.pack()
    bCancel.pack()
        
    
    ## paint window
    center(window)
    window.mainloop()    
    
    return    
    


# ---------------------------------------- Main ------------------------------------------------------------------
# --- Settings

allowedVidFileExt = ['mp4','flv']

# --- glob. Vars

globStr = ""
workpath = ""
vidpath = ""
playlist = ""

# --- Src

# Arbeitsordner finden
workpath = ReadWorkpath()
print ("Workpath : " + workpath)

# Suche nach Dirs
for dir in os.listdir(workpath):     ## dir = der aktuelle Upload ordner !
    if dir[0]=='.' :          ## ignore . files
        continue    
    if os.path.isfile(dir):   ## ignore files 
        continue           
    elif os.path.isdir(dir):  ## Ordner gefunden ! Jetzt nach Files suchen        
        vidpath = workpath + "\\" + dir
        print ("Folder: " + vidpath)
        ## Step 1 : Suche nach playlist file        
        playlist = ReadPlaylist(vidpath) 
        print("playlist: " + playlist)
        ## Step 2 : Suche nach VidFiles        
        for vidFile in os.listdir(vidpath):            
            if os.path.isfile(vidpath + "\\" + vidFile):   ## file gefunden!
                # print ("File : " + vidFile)   
                if (not(IsVidFile(vidFile))) :
                    continue        ## ignore non vid files 
                else :
                    print("Videofile: " + vidFile)
                    # Step 3 .. Search for nyu- upload settings file
                    nyufileName = FileGetNameWoExt(vidFile) + ".nyu"
                    if (not(os.path.exists(nyufileName))) :     # Gibt es kein Setting file ?                         
                         ShowNewVidFrame(vidpath, vidFile)
                         pass             
                    else :
                        # kann gelöscht werden wenn gewollt
                        pass        # << das heißt to be done                        
            else :
                print ("kein file " + vidFile)            
    else :                  ## alles andere ignon
        continue    

exit()









top = tkinter.Tk()
# Code to add widgets will go here...
top.mainloop()
exit()


# Ab hier MUELL !
# -- string splitten für Path für max Dir
# str1=os.getcwd()
# str2=str1.split('\\')
# n=len(str2)
# print str2[n-1]
