#!/usr/bin/python3
import os
import subprocess
import sys
from time import gmtime, strftime


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
        tmp =  file.readline().replace('\n','')
        file.close
        return tmp

def ReadPlaylist(path) :
    playlistfilepath = path + os.sep + "playlist.txt"
    if (os.path.exists(playlistfilepath)) :
        file = open(playlistfilepath, 'r')
        playlist = file.readline().strip().replace('\n','').replace('\r','')
        playlist_link = file.readline().strip().replace('\n','').replace('\r','')
        file.close
    else :
        playlist = ""
        playlist_link = ""
    return playlist, playlist_link
    
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

# ---------------------------------------- Main ------------------------------------------------------------------
# --- Settings

allowedVidFileExt = ['mp4','flv','ts','m2ts']

# --- glob. Vars

globStr = ""
workpath = ""
vidpath = ""
playlist = ""
config_post_shutdown = False

# --- Src

# Args verarbeiten

print ("Anzahl Args : " + str(len(sys.argv)))

if ( len(sys.argv) > 1) :
    if (sys.argv[1] == "--shutdown") :
        config_post_shutdown = True
    if (sys.argv[1] == "-h") :
        print("--shutdown = post shutdown")
        exit(0);



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
        vidpath = curDir 
        print ("Folder: " + vidpath)
        ## Step 1 : Suche nach playlist file        
        playlist,playlist_link = ReadPlaylist(vidpath)       
        ## Step 2 : Suche nach VidFiles        
        for vidFile in os.listdir(vidpath):            
            if os.path.isfile(vidpath + os.sep + vidFile):   ## file gefunden!
                # print ("File : " + vidFile)   
                if (not(IsVidFile(vidFile))) :
                    continue        ## ignore non vid files 
                else :
                    print("--------------------------------------------------")
                    print("Videofile: " + vidFile)
                    # Step 3 .. Search for nyu- upload settings file
                    nyufileName = vidFile + ".nyu"
                    donefileName = vidFile + ".done"
                    if (not(os.path.exists(vidpath + os.sep + nyufileName))) :     # Gibt es kein Setting file ?                         
                         print("No nyu-config for : " + vidpath + os.sep + vidFile)                                      
                    else :
                        # nyu file existiert .. evtl auch schon ein done file ?
                        if (os.path.exists(vidpath + os.sep + donefileName)) :
                            # nachfrage ob alles geloescht werden soll                            
                            print(vidFile + " can be deleted .. it is already uploaded")
                        else :
                            # ok noch nicht uploaded .. lesen des nyu files und upload starten
                            nyuconfigfile = open(vidpath + os.sep + nyufileName, 'r')
                            vidTitle =  nyuconfigfile.readline().replace('\n','').replace('\r','').replace("\\n",'')
                            vidDesc =  nyuconfigfile.readline().replace("\\n",'\n').replace('\r','')
                            if (playlist_link != "") :
                                vidDesc = vidDesc + "\n\n------------\nplaylist:\n" + playlist_link
                            nyuconfigfile.close()
                            print ("Title : " + vidTitle)    
                            print ("Desc  : " + vidDesc) 
                            if (playlist != "") :
                                print ("Playlist : " + playlist)  
                            # ok los gehts mit dem upload 
                            keyfile = workpath + os.sep + "key" + os.sep + "key.json"
                            cmd = "youtube-upload -t \"" + vidTitle+ "\" -d \"" + vidDesc + "\" --client-secrets=\"" + keyfile  + "\" --playlist \"" + playlist + "\" \"" + vidpath + os.sep + vidFile + "\""
                            print ("cmd: " , cmd)
                            process = subprocess.Popen(cmd, shell=True)
                            process.wait()
                            retcode = process.returncode
                            print ("retcode : " + str(retcode))
                            if (retcode == 0) : 
                                fdone = open(vidpath + os.sep + donefileName,"w")
                                fdone.write(str(strftime("%Y-%m-%d %H:%M:%S", gmtime())))
                                fdone.close()
                            else :
                                print ("Retcode invalid")
            else :
                print ("kein file " + vidFile)
    else :                  ## alles andere ignon
        continue
if (config_post_shutdown == True) :
	print("shutting down now");
	##p = subprocess.Popen("sudo shutdown -h now", shell=True)
	##p.wait()
exit()


