##!/usr/bin/python3
import os
import subprocess
import sys
import progressbar
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

## Read playlist.txt file
## Line 1 : playlist name
## Line 2 : playlist link
## Line 3 : All video privacy
def ReadPlaylist(path) :
    playlistfilepath = path + os.sep + "playlist.txt"
    if (os.path.exists(playlistfilepath)) :
        file = open(playlistfilepath, 'r')
        playlist = file.readline().strip().replace('\n','').replace('\r','')
        playlist_link = file.readline().strip().replace('\n','').replace('\r','')
        video_privacy = file.readline().strip().replace('\n','').replace('\r','')
        if (not(video_privacy == "unlisted" or video_privacy == "public" or video_privacy == "private")) :
            video_privacy = "public"             
        file.close
    else :
        playlist = ""
        playlist_link = ""
        video_privacy = "public"
    return playlist, playlist_link, video_privacy
    
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

program_option_verbose = False
if ( len(sys.argv) > 1) :
    if (sys.argv[1] == "--shutdown") :
        config_post_shutdown = True
    if (sys.argv[1] == "-h" or sys.argv[1] == "--help") :
        print("--shutdown = post shutdown")
        print("-v = verbose mode on")
        exit(0);
    if (sys.argv[1] == "-v") :
        print("verbose mode on")
        program_option_verbose = True



# Arbeitsordner finden
workpath = ReadWorkpath()
print ("Workpath : " + workpath)

vidCounter = 0
vidMaxCount = 1

# Suche nach Dirs
for dir in os.listdir(workpath):     ## dir = der aktuelle Upload ordner !
    if (vidCounter >= vidMaxCount) :
        break
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
        ## Step 1 : Search for playlist file (Filestructure is inside this func)                
        playlist,playlist_link,video_privacy = ReadPlaylist(vidpath)       
        ## Step 2 : Search for VidFiles        
        for vidFile in os.listdir(vidpath):            
            if (vidCounter >= vidMaxCount) :
                break
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
                    logfileName = "uploadedFiles.txt"

                    if (not(os.path.exists(vidpath + os.sep + nyufileName))) :     # Gibt es kein Setting file ?                         
                         print("No nyu-config for : " + vidpath + os.sep + vidFile)                                      
                    else :
                        # nyu file existiert .. evtl auch schon ein done file ?
                        if (os.path.exists(vidpath + os.sep + donefileName)) :
                            # nachfrage ob alles geloescht werden soll                            
                            print(vidFile + " can be deleted .. it is already uploaded")
                        else :
                            # ok noch nicht uploaded .. lesen des nyu files und upload starten
                            nyuconfigfile = open(vidpath + os.sep + nyufileName, encoding='utf8')
                            vidTitle =  nyuconfigfile.readline().replace('\n','').replace('\r','').replace("\\n",'')
                            vidDesc =  nyuconfigfile.readline().replace("\\n",'\n').replace('\r','')

                            if (playlist_link != "") :
                                vidDesc = vidDesc + "\n\n------------\nplaylist:\n" + playlist_link
                            nyuconfigfile.close()
                            print ("Title : " + vidTitle)    
                            # print ("Desc  : " + vidDesc) 
                            print ("Desc : <hidden>")
                            if (playlist != "") :
                                print ("Playlist : " + playlist)  
                            # ok los gehts mit dem upload 
                            keyfile = workpath + os.sep + "key" + os.sep + "key.json"
                            cmd = "youtube-upload -t \"" + vidTitle+ "\" -d \"" + vidDesc + "\" " \
                                  "--client-secrets=\"" + keyfile  + "\" " \
                                  "--playlist \"" + playlist + "\" " \
                                  "--privacy " + video_privacy + " " \
                                  "\"" + vidpath + os.sep + vidFile + "\"" + " " \
                                  "" # ">> " + str(strftime("%Y-%m-%d-%H-%M-%S", gmtime())) + "." + vidFile + ".ytlog"
                                  
                            if (program_option_verbose) : 
                                print ("cmd: " , cmd)
                            
                            print ("starting upload: " + str(strftime("%Y-%m-%d %H:%M:%S", gmtime())))

                            # cmd = "export PYTHONIOENCODING=UTF-8 && " + cmd
                            #process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                            process = subprocess.Popen(cmd, shell=True, universal_newlines=True)
                            p_output, p_errors = process.communicate()
                            retcode = process.returncode
                            print (str(strftime("%Y-%m-%d %H:%M:%S  ", gmtime())) + "retcode : " + str(retcode))

                            # We are fine from here on ! Upload was successful !
                            if (retcode == 0 or retcode == 3) : 
                                if (retcode == 3) : 
                                     print ("Quickfix against internal Error")
                                     #print("Output : \n" + p_output)
                                     #print("Errors: \n" + p_errors)
                                # create done file
                                fdone = open(vidpath + os.sep + donefileName,"w")
                                fdone.write(str(strftime("%Y-%m-%d %H:%M:%S", gmtime())))
                                #if (program_option_verbose) :                                    
                                    #print("output:\n" + p_output)
                                fdone.close()
                                # append to logfile
                                fdone = open(vidpath + os.sep + logfileName,"a")
                                fdone.write(str(strftime("%Y-%m-%d %H:%M:%S", gmtime())) + "   -   " + vidFile + "\n")
                                fdone.close()
                                # add 1 to vidcounter that vidcounter >= vidMaxCount pulls off
                                vidCounter = vidCounter + 1
                            elif (retcode == 3) :
                                print ("Looks like you'r out of GoogleQuota :)")
                                #print("Output : \n" + p_output)
                                #print("Errors: \n" + p_errors)
                                exit(3)
                            else :
                                print ("Retcode invalid")
                                #print (p_errors)
                                exit(retcode)
                
            else :
                print ("kein Video-file " + vidFile)
    else :                  ## alles andere ignon
        continue
if (config_post_shutdown == True) :
    print("shutting down now");
    p = subprocess.Popen("sudo shutdown -h now", shell=True)
    p.wait()
exit()


