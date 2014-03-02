#Bulkrename Tool for CS1410 Class - Ross Rydman - Jan 2012
import sys
import os
import random

def printusage():
    print ('Usage: bulkrename <directory> [<prefix>]') 
    sys.exit(1)
def printheader(args):
    print ('Directory: ') + args[1]
    if len(args) == 2:
        print ('Prefix: ') + args[1] + (' (No prefix, using directory name as prefix)')
    else:
        print ('Prefix: ') + args[2]
def filterByExtension(root, allfiles, extensions):
    matching = []
    for i in allfiles:
        if (i.rfind('.') == -1):
            continue
        elif ((i[i.rfind('.')+1:]).lower() not in extensions):
            continue
        elif os.path.isfile(os.path.join(root,i)) == False:
            print ('Odd, it appears this files name is also a directory.')
        else:
            matching.append(i)
    return matching
def sortByMTime(root, matching):
    templist = []
    inorder = []
    for i in matching:
        templist.append((os.path.getmtime(os.path.join(root,i)),i))
    templist.sort()
    for (_,name) in templist:
        inorder.append(name)
    return inorder
def assignNames(prefix, inorder):
    digits = len(str(len(inorder)))
    template = '%%0%dd' % digits
    newnames = {}
    number = 1
    for i in inorder:
        suffix = template % number
        ext = i[i.rfind('.'):].lower()
        newnames[i] = prefix + suffix + ext
        number += 1
    return newnames
def makeTempName(allfiles):
    randnum = random.randint(0,1000000000)
    allfilesnoext = []
    for i in allfiles:
        allfilesnoext.append(i[0:i.rfind('.')].lower())
    while True:
        tempname = "__temp%r__" % random.randint(0,1000000000)
        if tempname not in allfilesnoext:
            break
    return tempname
def makeScript(inorder, newnames, tempname):
    script = []
    for oldname in inorder:
        if oldname not in newnames:
            continue
        elif oldname == newnames[oldname]:
            del newnames[oldname]
        elif newnames[oldname] not in newnames.keys():
            script.append((oldname, newnames[oldname]))
            del newnames[oldname]
        else:
            chain = []
            inthechain = {}
            link = oldname
            while True:
                targetname = newnames[link]
                if targetname in inthechain:
                    newnames[link] = tempname
                    newnames[tempname] = targetname
                    chain.append((link, tempname))
                    chain.insert(0, (tempname, targetname))
                    break
                chain.append((link, targetname))
                inthechain[link] = True
                link = targetname
                if link not in newnames.keys():
                    break
            chain.reverse()
            for i in chain:
                script.append(i)
                del newnames[i[0]]
    return script
def doRenames(root, script):
    for i in script:
        print (i[0] + ' -> ' + i[1])
        oldpath = os.path.join(root, i[0])
        newpath = os.path.join(root, i[1])
        if os.path.exists(newpath):
            os.exit(1)
        else:
            os.rename(oldpath, newpath)
def main():
    args = sys.argv
    #set prefix to path if one was not supplied by user
    if (len(args) == 2):
        root = os.path.abspath(args[1])
        prefix = os.path.basename(os.path.abspath(args[1]))
        printheader(args)
    #set prefix to use for files to rename
    elif (len(args) == 3): 
        root = os.path.abspath(args[1])
        prefix = args[2]
        printheader(args)
    else:
        printusage()
    #get list of all files in directory
    allfiles = os.listdir(root)
    #set extensions to use - ensure entries here are lowercase
    extensions = ['jpeg', 'jpg', 'png', 'gif']
    matching = filterByExtension(root, allfiles, extensions)
    inorder = sortByMTime(root, matching)
    newnames = assignNames(prefix, inorder)
    tempname = makeTempName(allfiles) #note that tempname has no extension
    script = makeScript(inorder, newnames, tempname)
    doRenames(root, script)

main()
