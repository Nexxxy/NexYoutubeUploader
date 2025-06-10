##!/usr/bin/python3
import os
import subprocess
import sys
import progressbar
import json
from time import gmtime, strftime


# TODO -----------------------------------------------------------------------
# TODO * Parameterhandling enhancement
# TODO * Better Ratelimit handling
# TODO * rename playlist.txt into config.txt
# TODO * fix auth token filename management


# dir_path = os.path.dirname(os.path.realpath(__file__))

# ---------------------------------------- Functions ------------------------------------------------------------


def ReadWorkpath():
    if os.path.exists("settings.dat") == False:
        print("there is no settings file")
        file = open('settings.dat', 'w')
        file.write(os.getcwd())
        file.close
        return os.getcwd()
    else:
        file = open('settings.dat', 'r')
        tmp = file.readline().replace('\n', '')
        file.close
        return tmp


## Read playlist.txt file
## Line 1 : playlist name
## Line 2 : playlist link
## Line 3 : All video privacy
## Line 4 : Authfile name
def ReadPlaylist(path):
    playlistfilepath = path + os.sep + "playlist.txt"
    authFileName = "auth.token"
    if (os.path.exists(playlistfilepath)):
        file = open(playlistfilepath, 'r')
        playlist = file.readline().strip().replace('\n', '').replace('\r', '')
        playlist_link = file.readline().strip().replace('\n', '').replace('\r', '')
        video_privacy = file.readline().strip().replace('\n', '').replace('\r', '')
        try : 
            authFileName = file.readline().strip().replace('\n', '').replace('\r', '')
            if (authFileName == "") :
                print("defaulting Authfile : auth.token")
                authFileName = "auth.token"
            else :
                print ("Using Authfile : " + authFileName)
        except :
            print ("Failed reading playlist.txt")
            pass

        if (not (video_privacy == "unlisted" or video_privacy == "public" or video_privacy == "private")):
            video_privacy = "public"
        file.close
    else:
        playlist = ""
        playlist_link = ""
        video_privacy = "public"
    return playlist, playlist_link, video_privacy, authFileName


def FileGetExt(filename):
    tmpstr = filename.split('.')
    n = len(tmpstr)
    if (n == 1):
        return ""
    return (tmpstr[n - 1])


def FileGetNameWoExt(filename):
    tmpstr = filename.split('.')
    n = len(tmpstr)
    if (n == 1):
        return ""
    return (tmpstr[0])


def GetCurFolder(path):
    tmpstr = path.split(os.sep)
    n = len(tmpstr)
    if (n == 1):
        return ""
    return (tmpstr[n - 1])


def IsVidFile(filename):
    if allowedVidFileExt.count(FileGetExt(filename)) == 0:  ## super einfach .. wenn der string in der liste vorkommt isses nen vid
        return False
    else:
        return True


def dumpMetadataToFile(pTitle, pDesc, pPrivacy, pPlaylist):
    metaData = {
        "title": pTitle,
        "description": pDesc,
        "privacyStatus": pPrivacy,
        "madeForKids": False,
        "language": "de",
    }
    if (len(pPlaylist) > 0) :
        metaData["playlistTitles"] = [pPlaylist]

    with open('data.json', 'w', encoding='utf-8') as myFile:
        json.dump(metaData, myFile, ensure_ascii=False, indent=4)


# ---------------------------------------- Main ------------------------------------------------------------------
# --- Settings

allowedVidFileExt = ['mp4', 'flv', 'ts', 'm2ts']

# --- glob. Vars

globStr = ""
workpath = ""
vidpath = ""
playlist = ""
config_post_shutdown = False
config_ytupload_bin_path = "/usr/local/ytupload/youtube-upload-armv6"
config_ratelimit_in_Mbit = 0


NO_EXEC = False

# --- Src

# Args verarbeiten

print("Anzahl Args : " + str(len(sys.argv)))

program_option_verbose = False
if (len(sys.argv) > 1):
    if (sys.argv[1] == "--shutdown"):
        config_post_shutdown = True
    if (sys.argv[1] == "-h" or sys.argv[1] == "--help"):
        print("--shutdown = post shutdown")
        print("-v = verbose mode on")
        exit(0);
    if (sys.argv[1] == "-v"):
        print("verbose mode on")
        program_option_verbose = True

# Arbeitsordner finden
workpath = ReadWorkpath()
print("Workpath : " + workpath)

# set Ratelimit

ratelimit_string = ""
if (config_ratelimit_in_Mbit > 0) :
    print("Ratelimit active : " + str(config_ratelimit_in_Mbit) + " Mbit")
    config_ratelimit_in_Mbit = config_ratelimit_in_Mbit * 1024
    ratelimit_string = "-ratelimit " + str(config_ratelimit_in_Mbit) + " "



vidCounter = 0
vidMaxCount = 999

# Suche nach Dirs
for dir in os.listdir(workpath):  ## dir = der aktuelle Upload ordner !
    if (vidCounter >= vidMaxCount):
        break
    curDir = workpath + os.sep + dir
    if curDir[0] == '.':  ## ignore . files
        print("ignore file ." + curDir)
        continue
    if "System Volume" in curDir:
        print("skipping Windows folder: " + curDir)
        continue
    if os.path.isfile(curDir):  ## ignore files
        print("file ?")
        continue
    elif os.path.isdir(curDir):  ## Ordner gefunden ! Jetzt nach Files suchen
        vidpath = curDir
        print("Folder: " + vidpath)
        ## Step 1 : Search for playlist file (Filestructure is inside this func)
        playlist, playlist_link, video_privacy, authTokenFileName = ReadPlaylist(vidpath)
        ## Step 2 : Search for VidFiles
        for vidFile in os.listdir(vidpath):
            if (vidCounter >= vidMaxCount):
                break
            if os.path.isfile(vidpath + os.sep + vidFile):  ## file gefunden!
                # print ("File : " + vidFile)
                if (not (IsVidFile(vidFile))):
                    continue  ## ignore non vid files
                else:
                    print("--------------------------------------------------")
                    print("Videofile: " + vidFile)
                    # Step 3 .. Search for nyu- upload settings file
                    nyufileName = vidFile + ".nyu"
                    donefileName = vidFile + ".done"
                    logfileName = "uploadedFiles.txt"

                    if (not (os.path.exists(vidpath + os.sep + nyufileName))):  # Gibt es kein Setting file ?
                        print("No nyu-config for : " + vidpath + os.sep + vidFile)
                    else:
                        # nyu file existiert .. evtl auch schon ein done file ?
                        if (os.path.exists(vidpath + os.sep + donefileName)):
                            # nachfrage ob alles geloescht werden soll
                            print(vidFile + " can be deleted .. it is already uploaded")
                        else:
                            # ok noch nicht uploaded .. lesen des nyu files und upload starten
                            nyuconfigfile = open(vidpath + os.sep + nyufileName, encoding='utf8')
                            vidTitle = nyuconfigfile.readline().replace('\n', '').replace('\r', '').replace("\\n", '')
                            vidDesc = nyuconfigfile.readline().replace("\\n", '\n').replace('\r', '')

                            if (playlist_link != ""):
                                vidDesc = vidDesc + "\n\n------------\nPlaylist:\n" + playlist_link
                            nyuconfigfile.close()
                            print("Title : " + vidTitle)
                            # print ("Desc  : " + vidDesc)
                            print("Desc : <hidden>")
                            if (playlist != ""):
                                print("Playlist : " + playlist)
                            # ok los gehts mit dem upload
                            keyfile = workpath + os.sep + "key" + os.sep + "client_secret_webapp-raspy-nyu.json"                            
                            authToken = workpath + os.sep + "key" + os.sep + authTokenFileName                            
                            # Care if authToken is not a File :) - Evtl nochmal ueberdenken ob man hier nicht dann auf default auth.token geht
                            if (authToken[-1] == '/' or authToken[-1] == '\\') :
                                print("authdecriptor missing in playlist.txt in subfolder")
                                exit(4)
                            print ("Authtoken : " + authToken)
                            # cmd = "youtube-upload -t \"" + vidTitle+ "\" -d \"" + vidDesc + "\" " \
                            #      "--client-secrets=\"" + keyfile  + "\" " \
                            #      "--playlist \"" + playlist + "\" " \
                            #      "--privacy " + video_privacy + " " \
                            #      "\"" + vidpath + os.sep + vidFile + "\"" + " " \
                            #      "" # ">> " + str(strftime("%Y-%m-%d-%H-%M-%S", gmtime())) + "." + vidFile + ".ytlog"

                            # dump into MetaDataFile
                            dumpMetadataToFile(vidTitle, vidDesc, video_privacy, playlist)                           
                            
                            cmd = config_ytupload_bin_path + " " \
                                  "-filename " + "\"" + vidpath + os.sep + vidFile + "\"" + " " \
                                  "-metaJSON \"data.json\"" + " " \
                                  "-notify=false" + " " \
                                  "" + ratelimit_string + "" \
                                  "-secrets " + "\"" + keyfile + "\"" + " " \
                                  "-cache " + "\"" + authToken + "\"" + " "


                            if (program_option_verbose):
                                print("cmd: ", cmd)

                            print("starting upload: " + str(strftime("%Y-%m-%d %H:%M:%S", gmtime())))
                            # old ver --
                            # cmd = "export PYTHONIOENCODING=UTF-8 && " + cmd
                            # process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                            # old ver --
                            retcode = 0
                            if (NO_EXEC == False):
                                process = subprocess.Popen(cmd, shell=True, universal_newlines=True)
                                p_output, p_errors = process.communicate()
                                retcode = process.returncode
                            else:
                                retcode = 95
                            print(str(strftime("%Y-%m-%d %H:%M:%S  ", gmtime())) + "retcode : " + str(retcode))

                            # We are fine from here on ! Upload was successful !
                            if (retcode == 0 or retcode == 3):
                                if (retcode == 3):
                                    print("Quickfix against internal Error")
                                    # print("Output : \n" + p_output)
                                    # print("Errors: \n" + p_errors)
                                # create done file
                                fdone = open(vidpath + os.sep + donefileName, "w")
                                fdone.write(str(strftime("%Y-%m-%d %H:%M:%S", gmtime())))
                                # if (program_option_verbose) :
                                # print("output:\n" + p_output)
                                fdone.close()
                                # append to logfile
                                fdone = open(vidpath + os.sep + logfileName, "a")
                                fdone.write(str(strftime("%Y-%m-%d %H:%M:%S", gmtime())) + "   -   " + vidFile + "\n")
                                fdone.close()
                                # add 1 to vidcounter that vidcounter >= vidMaxCount pulls off
                                vidCounter = vidCounter + 1
                            elif (retcode == 3):
                                print("Looks like you'r out of GoogleQuota :)")
                                # print("Output : \n" + p_output)
                                # print("Errors: \n" + p_errors)
                                exit(3)
                            elif (retcode == 95):
                                print("Not executing Cmd line")
                            else:
                                print("Retcode invalid")
                                # print (p_errors)
                                exit(retcode)

            else:
                print("kein Video-file " + vidFile)
    else:  ## alles andere ignon
        continue
if (config_post_shutdown == True):
    print("shutting down now");
    p = subprocess.Popen("sudo shutdown -h now", shell=True)
    p.wait()
exit()
