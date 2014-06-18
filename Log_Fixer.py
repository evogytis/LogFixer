import csv
import re
import os
import Tkinter, tkFileDialog

def index(data,item):
    return [i for i,x in enumerate(data) if x == item]

def unique(o, idfun=repr):
    seen = {}
    return [seen.setdefault(idfun(e),e) for e in o if idfun(e) not in seen]

choosing=False
usingTree=False

root = Tkinter.Tk()
file = tkFileDialog.askopenfile(parent=root,mode='rb',title='Choose a tree file')
if file != None:
        trees=file
        usingTree=True
        print 'Tree file:\n%s'%(file.name.split('/')[-1])
else:
    print 'Not checking tree file for consistency.'
root.withdraw()

## contains references to the logfiles to be analysed
logfileList=[]

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

## contains state numbers from all the files
if usingTree==True:
    logfileStates=list([] for q in range(len(logfileList)+1))
else:
    logfileStates=list([] for q in logfileList)
 
## loads state numbers from tree file, closes it
if usingTree==True:
    #logfileStates.append([])
    treefile=open(trees.name,'r')
    for i in treefile:
        if i.count('\x00') == 0:
            cerberus=re.search("tree STATE_([0-9]+)",i)
            if cerberus is not None:
                logfileStates[0].append(int(cerberus.group(1)))
    treefile.close()

## rewrite every file in case of null bytes
for i in logfileList:
    fi = open(i.name, 'rb')
    data = fi.read()
    fi.close()
    fo = open(i.name+'2.txt', 'wb')
    fo.write(data.replace('\x00', ''))
    fo.close()
  

logfileColLength=list(0 for q in logfileList)
    
## collect state numbers from all files
for logIndex in range(len(logfileList)):
    print '\nCollecting states from file %s'%(logfileList[logIndex].name)
    logFile=csv.reader(open(logfileList[logIndex].name+'2.txt','r'),delimiter='\t',quotechar='"')
    storeState=0
    subsampling=0
    for line in logFile:
        ## first line doesn't have any useful info
        if len(line)==1:
            pass
        else:
            ## check number of columns
            colnum=len(line)
            ## finds the column length
            if line[0]=='state':
                print '\nExpected number of columns for file \n%s: %s'%(logfileList[logIndex].name,colnum)
                logfileColLength[logIndex]=colnum

            ## only includes states where the full column complement is present
            if colnum==logfileColLength[logIndex]:
                if usingTree==True:
                    if line[0]!='state':
                        logfileStates[logIndex+1].append(int(line[0]))
                else:
                    if line[0]!='state':
                        if subsampling==0:
                            subsampling=int(line[0])

                    if line[0]!='state' and int(line[0])==storeState+subsampling:
                        logfileStates[logIndex].append(int(line[0]))
                        storeState=int(line[0])
            else:
                pass
            
## finds the states shared by all files
common=[]
for fname in logfileStates:
    for state in fname:
        common.append(state)
        
common=unique([x for x in common if common.count(x)==len(logfileStates)])

print '\nNumber of states shared by all files: %s'%(len(common))

## writes only complete states that are shared by all files
for i in range(len(logfileList)):
    #print '\nWriting shared states from file %s'%(logfileList[i].name)
    with open(logfileList[i].name+'2.txt') as f:
        inFile=csv.reader(f,delimiter='\t')
        if '.txt' in logfileList[i].name:
            out=open(logfileList[i].name.replace('.txt','.fixed.txt'),'w+')
        else:
            out=open(logfileList[i].name+'.fixed.txt','w+')
        linecounter=0
        for line in inFile:
            if len(line)==1:
                print>>out,line[0]
            else:
                outString=[]
                if line[0]=='state':
                    for l in line:
                        outString.append(l)
                    print>>out,'\t'.join(outString)
                elif int(line[0]) in common:
                    outString.append(str(linecounter))
                    for l in line[1:]:
                        outString.append(l)
                    print>>out,'\t'.join(outString)
                    linecounter+=1
        out.close()

## writes trees which are associated with complete states shared by all files
if usingTree==True:
    treescounter=-1
    trees=open(trees.name,'r')
    if '.txt' in trees.name:
        out=open(trees.name.replace('.txt','.fixed.txt'),'w+')
    else:
        out=open(trees.name+'.fixed.txt','w+')
    for line in trees:
        cerberus=re.search("tree STATE_([0-9]+)",line)
        if "tree STATE_" not in line:
            print>>out,line.strip('\n')
        if cerberus is not None:
            if int(cerberus.group(1)) in common:
                print>>out,'tree STATE_%s\t%s'%(treescounter,line[len(cerberus.group()):])
                treescounter+=1
    ## finishing touches
    out.write('End;')
    out.close()

## cleanup - remove temporary files used for removing null bytes
for line in logfileList:
    os.remove('%s2.txt'%(line.name))
    print '\nTemporary file %s2.txt removed'%(line.name)

print '\nDone!'
