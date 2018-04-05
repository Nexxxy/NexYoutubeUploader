#!/usr/bin/python3
import tkinter # note that module name has changed from Tkinter in Python 2 to tkinter in Python 3
import os 


# dir_path = os.path.dirname(os.path.realpath(__file__))

# ---------------------------------------- Functions ------------------------------------------------------------

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
    
def IsVidFile(filename) :       
    if allowedVidFileExt.count(FileGetExt(filename))==0 :            ## super einfach .. wenn der string in der liste vorkommt isses nen vid
        return False
    else :
        return True
    


# ---------------------------------------- Main ------------------------------------------------------------------
# --- Settings

allowedVidFileExt = ['mp4','flv']

# --- glob. Vars

workpath = ""
vidpath = ""

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
        for vidFile in os.listdir(vidpath):            
            if os.path.isfile(vidpath + "\\" + vidFile):   ## file gefunden!
                # print ("File : " + vidFile)   
                if (not(IsVidFile(vidFile))) :
                    continue        ## ignore non vid files 
                else :
                    print("Videofile: " + vidFile)
                    # Step 1 .. Search for nyu- upload settings file
                        
            else :
                print ("kein file " + vidFile)            
    else :                  ## alles andere ignon
        print("u-" + dir)
    

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
