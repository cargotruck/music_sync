#!/usr/bin/env python3

#--------------------------------------------------------------------------

# MUSIC_SYNC.py written by nicholas.flesch@outlook.com
# last modified: 22 October 2020
# 
# Compares two user designated locations (master and slave) 
# and copies music files from the master to slave location.
#


#--------------------------------------------------------------------------
#--------------------------------------------------------------------------
#--------------------------------------------------------------------------

import argparse
import os
import sys
import shutil
import textwrap

#--------------------------------------------------------------------------

def readConfig():
    
    configFile = "config.options"
    configSource = "SOURCE"
    configTarget = "TARGET"
    sep = ":"
    sourcePath = ""
    targetPath = ""
    
    if os.path.isfile(configFile):
        fp = open(configFile,"r")

        while True:
            buffer = fp.readline()
            if buffer == "":
                break
            else:
                if buffer.split(sep,1)[0] == configSource:
                    sourcePath = buffer.split(sep,1)[1]
                if buffer.split(sep,1)[0] == configTarget:
                    targetPath = buffer.split(sep,1)[1]
        fp.close

    return sourcePath.strip(), targetPath.strip()

#--------------------------------------------------------------------------

def writeConfig(sourcePath,targetPath):

    configFile = "config.options"
    configSource = "SOURCE"
    configTarget = "TARGET"
    sep = ":"

    fp = open(configFile,"w")

    fp.write(configSource + sep + sourcePath + '\n')
    fp.write(configTarget + sep + targetPath + '\n')

    fp.close

#--------------------------------------------------------------------------

def getOptions():

    parser = argparse.ArgumentParser()
    parser.add_argument("-i","--inverse",action = "store_true",help = "copy from mobile device to PC")
    parser.add_argument("-s","--source",help = "sets the source directory")
    parser.add_argument("-t","--target",help = "sets the target directory")
    args = parser.parse_args()

    sourcePath = ""
    targetPath = ""
    configSourcePath, configTargetPath = readConfig()  
    
    if args.source:
        sourcePath = args.source
        sourceName = args.source
    else:
        sourcePath = configSourcePath 
        sourceName = "Computer"

    if args.target:
        targetPath = args.target
        targetName = args.target
    else:
        targetPath = configTargetPath 
        targetName = "Mobile Device"

    if args.inverse:
        tempSrc = sourcePath
        sourcePath = targetPath
        targetPath = tmpSrc 
        sourceName = "Mobile Device"
        targetName = "Computer"
          
    if not os.path.exists(sourcePath): # or not sourcePath:
        print("Invalid source:\n\n",sourcePath,"\n\nPlease check source location.")
        sys.exit()
    if not os.path.exists(targetPath) or not targetPath:
        print("Invalid target:\n\n",targetPath,"\n\nPlease check target location.")
        sys.exit()

    writeConfig(sourcePath,targetPath)
    
    return sourcePath, targetPath, sourceName, targetName

#--------------------------------------------------------------------------

# moves through a directory tree and returns an UNSORTED list of all files and folders within.
# adds all files and directories to fList. If an item is a directory it also adds it to dirts.
# traverseDirTree is then called on all directories in dirts, and their contents added to fList.
# when the recursive call of fList is unable to find any more directories fList is returned to
# the original caller.

def traverseDirTree(directory,fList = None,dirts = None):    

    if fList is None:
        fList = []
    if dirts is None:
        dirts = []

    paths = os.listdir(directory)

    for item in paths:
        itemPath = os.path.join(directory,item)
        fList.append(itemPath)
        if os.path.isdir(itemPath):
            dirts.append(itemPath)

    if len(dirts) == 0:
        return fList
    else:
        for item in dirts:
            dirts.remove(item)
            return traverseDirTree(item,fList = fList,dirts = dirts)

#--------------------------------------------------------------------------

# strips the "prefix" path off of a directory so that two directory 
# trees in two different locations can be compared. 
# For example, if there is /location-1/movies/... and /location-2/movies/... 
# provided proper input this function will 
# strip /location-1 and /location-2 off the file paths so that 
# everything else can be compared. THERE ARE SIMILAR FUNCTIONS TO GET THIS JOB DONE, 
# NAMELY os.path.basename() AND os.path.dirname(). LOOK AT PCA.pdf page 188 for further details. 

def stripParentDir(parent,dirTree):     
    newTree = []

    for i in dirTree:
        i = i[len(parent):]
        newTree.append(i)

    newTree.sort()
    return newTree

#--------------------------------------------------------------------------
 
# this function compares two directory trees, one is the master and the other the slave. 
# Items in the master list are compared to those in the slave list, if there is a 
# duplicate in the slave then that duplicate is added to a duplicate list. 
# The items in the duplicate list are then removed from the master list. 
# RETURNS the modifed master list.

def compareTrees(masterTree,slaveTree):     

    duplicates = []

    for item in masterTree:
        if item in slaveTree:
            duplicates.append(item)
    
    for dup in duplicates:
        if dup in masterTree:
            masterTree.remove(dup)

    prunedTree = [] #Remove leading '/'
    for item in masterTree:
        item = item.lstrip('/')
        prunedTree.append(item)
        
    return prunedTree

#--------------------------------------------------------------------------

def isMusicFile(srcFile):
    musicFiles = [ \
        ".mp3", \
        ".ogg", \
        ".wma", \
        "m4a" \
    ]

    for ext in musicFiles:
        if srcFile.endswith(ext):
            return True

    return False

#--------------------------------------------------------------------------

def copyMusic(sourceFile,destDir):

    if os.path.isfile(sourceFile) and isMusicFile(sourceFile):
        try:
            command = "gio copy -P"\
                        + " "\
                        + "\""\
                        + sourceFile\
                        + "\""\
                        + " "\
                        + "\""\
                        + destDir\
                        + "\""
            print("copy...", sourceFile)
            os.system(command)
            print(destDir)
        except:
            print(command)
            print("File:\n", sourceFile, "\ncould not be copied.")

    if os.path.isdir(sourceFile):
        try:
            command = "gio mkdir"\
                        + " "\
                        + "\""\
                        + os.path.join(destDir,os.path.basename(sourceFile))\
                        + "\""
            os.system(command)
        except:
            print(command)
            print("Directory:\n", sourceFile, "\ncould not be copied.")

#--------------------------------------------------------------------------

def main():
    
    sourcePath, targetPath, sourceName, targetName = getOptions()
    print("GETTING PATHS...")

    print("TRAVERSING SOURCE: {}".format(sourceName))
    sourceMusicTree = traverseDirTree(sourcePath)

    print("TRAVERSING TARGET: {}".format(targetName))
    targetMusicTree = traverseDirTree(targetPath) 

    print("SORTING LISTS...")
    sourceMusicTree.sort()
    targetMusicTree.sort()

    sourceMusicTree = stripParentDir(sourcePath,sourceMusicTree)
    targetMusicTree = stripParentDir(targetPath,targetMusicTree)
    compareTree = compareTrees(sourceMusicTree,targetMusicTree)

    print("BEGINNING COPY...")
    for item in compareTree:
        source = os.path.join(sourcePath,item)
        target = os.path.dirname(os.path.join(targetPath,item))
        copyMusic(source,target)

if __name__ == "__main__":
    main()
