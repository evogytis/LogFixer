import csv
import re
import os
import Tkinter, tkFileDialog

def index(data,item):
    return [i for i,x in enumerate(data) if x == item]

choosing=False
usingTrees=False

root = Tkinter.Tk()
file = tkFileDialog.askopenfile(parent=root,mode='rb',title='Choose a tree file')
if file != None:
        trees=file
        usingTrees=True
        print 'Tree file:\n%s'%(file.name.split('/')[-1])
else:
    print 'Not checking tree file for consistency.'
root.withdraw()

## contains references to the logfiles to be analysed
logfileList=[]

## contains state numbers from all the files
logfileStates=[]

## matrix to check how many columns there should be vs how many there are
logfileColLength=[]

## loop as long as there are files, proceed if no files left
while choosing==False:
    root = Tkinter.Tk()
    file = tkFileDialog.askopenfile(parent=root,mode='rb',title='Choose a file')
    if file != None:
        logfileList.append(file)
        print '\nFile:\n%s'%(file.name.split('/')[-1])
    else:
        choosing=True
    root.withdraw()

## loads state numbers from tree file, closes it
if usingTrees==True:
    logfileStates.append([])
    treefile=open(trees.name,'r')
    for i in treefile:
        if i.count('\x00') == 0:
            cerberus=re.search("tree STATE_([0-9]+)",i)
            if cerberus is not None:
                logfileStates[0].insert(0,cerberus.group(1))
    treefile.close()

## rewrite every file in case of null bytes
for i in logfileList:
    logfileStates.append([])
    logfileColLength.append([])
    fi = open(i.name, 'rb')
    data = fi.read()
    fi.close()
    fo = open(i.name+'2.txt', 'wb')
    fo.write(data.replace('\x00', ''))
    fo.close()


## collect state numbers from all files
for i in range(len(logfileList)):
    print '\nCollecting states from file %s'%(logfileList[i].name)
    j=csv.reader(open(logfileList[i].name+'2.txt','r'),delimiter='\t',quotechar='"')
    for k in j:
        ## first line doesn't have any useful info
        if len(k)==1:
            pass
        else:
            colnum=len(k)
            ## finds the column length
            if len(logfileColLength[i])==0:
                #print '\nExpected number of columns for file \n%s: %s'%(logfileList[i].name,colnum)
                logfileColLength[i].insert(0,colnum)
            ## only includes states where the full column complement is present
            if colnum==logfileColLength[i][0]:
                if usingTrees==True:
                    logfileStates[i+1].insert(0,k[0])
                else:
                    logfileStates[i].insert(0,k[0])
            else:
                pass
                #print 'State %s from file %s was missing %s columns'%(k[0],logfileList[i].name,colnum-logfileColLength[i][0])

## finds the states shared by all files
common = set(logfileStates[0])
for i in range(len(logfileStates[1:])):
    common.intersection(logfileStates[i+1])

print '\nNumber of states shared by all files: %s'%(len(common))


## writes only complete states that are shared by all files
for i in range(len(logfileList)):
    #print '\nWriting shared states from file %s'%(logfileList[i].name)
    with open(logfileList[i].name+'2.txt') as f:
        j=csv.reader(f,delimiter='\t')
        if '.txt' in logfileList[i].name:
            out=open(logfileList[i].name.replace('.txt','.fixed.txt'),'w+')
        else:
            out=open(logfileList[i].name+'.fixed.txt','w+')
        linecounter=-1
        for k in j:
            if len(k)==1:
                print>>out,k[0]
            else:
                if k[0]=='state':
                    string=''
                    for l in k[:-1]:
                        string+=l+'\t'
                    string+=k[-1]
                    print>>out,string
                elif k[0] in common:
                    string=str(linecounter)+'\t'
                    for l in k[1:-1]:
                        string+=l+'\t'
                    string+=k[-1]
                    print>>out,string
                linecounter+=1
        out.close()


## writes trees which are associated with complete states shared by all files
if usingTrees==True:
    treescounter=-1
    trees=open(trees.name,'r')
    if '.txt' in trees.name:
        out=open(trees.name.replace('.txt','.fixed.txt'),'w+')
    else:
        out=open(trees.name+'.fixed.txt','w+')
    for i in trees:
        cerberus=re.search("tree STATE_([0-9]+)",i)
        if "tree STATE_" not in i:
            print>>out,i.strip('\n')
        if cerberus is not None:
            if str(cerberus.group(1)) in common:
                print>>out,'tree STATE_%s\t%s'%(treescounter,i[len(cerberus.group()):])
                treescounter+=1
    ## finishing touches
    out.write('End;')
    out.close()


## cleanup - remove temporary files used for removing null bytes
for i in logfileList:
    os.remove('%s2.txt'%(i.name))
    #print '\nTemporary file %s2.txt removed'%(i.name)


print '\nDone!'
