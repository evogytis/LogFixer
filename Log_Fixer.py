import csv
import re
import os

#specify files that need to be analysed for continuity
#gmrf and rates files are what I usually need
#if you only have log and tree files leave gmrffile and ratesfile as empty strings i.e. ''

logfile = '/Users/admin/Documents/Viral sequences/0311 Influenza/HA Yamagata/HA0411Yamagata_1.log.txt'
treefile = '/Users/admin/Documents/Viral sequences/0311 Influenza/HA Yamagata/HA0411Yamagata_1.trees.txt'
gmrffile = '/Users/admin/Documents/Viral sequences/0311 Influenza/HA Yamagata/HA0411Yamagata_1.gmrf.txt'
ratesfile = '/Users/admin/Documents/Viral sequences/0311 Influenza/HA Yamagata/HA0411Yamagata_1.locations.rates.log'

#opens log and tree files
log = csv.reader(open(logfile,'rU'),delimiter='\t',quotechar='"')
trees = open(treefile,'r')

#open gmrf and rates files if they exist
if gmrffile != '':
    gmrf = csv.reader(open(gmrffile,'r'),delimiter='\t',quotechar='"')
if ratesfile != '':
    rates = csv.reader(open(ratesfile,'r'),delimiter='\t',quotechar='"')

#keeps track of non-tree files (file formatting reasons)
allfiles = [logfile,gmrffile,ratesfile]

print '\nNumber of files to be analysed for continuity: %s'%(len(allfiles)-allfiles.count('')+1)

#helps later on
filenames = ['log','tree','gmrf','rate']

#important bit - rereads data into a different file in case the file contains NULL bytes
for files in allfiles:
    if files != '':
        fi = open(files, 'rb')
        data = fi.read()
        fi.close()
        fo = open(files+'2.txt', 'wb')
        fo.write(data.replace('\x00', ''))
        fo.close()

#empty lists where the states from files will be saved
logstates = []
treestates = []
gmrfstates = []
ratestates = []

#list of lists with states
statesfiles = [logstates,treestates,gmrfstates,ratestates]

#appends states from the log file to a list
log2 = csv.reader(open(str(logfile)+'2.txt', 'r'),delimiter='\t',quotechar='"')
for unit in log2:
    if 'a' in unit[0]:
        pass
    else:
        L = re.search("[0-9]+",unit[0])
        if L is not None:
            logstates.append(int(L.group()))

print '\nStates from the log file are loaded'

#appends states from the tree file to a list
for unit in trees:
    P = re.search("tree STATE_[0-9]+",unit)
    if P is not None:
        treestates.append(int(P.group()[11:]))

print 'States from the tree file are loaded'

#if gmrf and rates file exist, appends their states to lists
if gmrffile != '':
    gmrf2 = csv.reader(open(str(gmrffile)+'2.txt', 'r'),delimiter='\t',quotechar='"')
    for unit in gmrf2:
        if 'a' in unit[0]:
            pass
        else:
            G = re.search("[0-9]+",unit[0])
            if G is not None:
                gmrfstates.append(int(G.group()))
    print 'States from the GMRF file are loaded'

if ratesfile != '':
    rates2 = csv.reader(open(str(ratesfile)+'2.txt', 'r'),delimiter='\t',quotechar='"')
    for unit in rates2:
        if 'a' in unit[0]:
            pass
        else:
            R = re.search("[0-9]+",unit[0])
            if R is not None:
                ratestates.append(int(R.group()))
    print 'States from the rates file are loaded'

#this is a list to which states present in all files will be appended
continuous = []

#determines which function to use based on the number of files to be analysed
if len(allfiles)-allfiles.count('')+1 == 2:
    def intersect(a, b):
        return list(set(a) & set(b))
    
if len(allfiles)-allfiles.count('')+1 == 3:
    def intersect(a,b,c):
        return list(set(a) & set(b) & set(c))

if len(allfiles)-allfiles.count('')+1 == 4:
    def intersect(a, b, c, d):
     return list(set(a) & set(b) & set(c) & set(d))

#inters is a list containing sorted states that are common between all files
if len(allfiles)-allfiles.count('')+1 == 2:
    inters = sorted(intersect(logstates,treestates))

if len(allfiles)-allfiles.count('')+1 == 3:
    if gmrffile !='':
        inters = sorted(intersect(logstates,treestates,gmrfstates))
    if ratesfile !='':
        inters = sorted(intersect(logstates,treestates,ratestates))

if len(allfiles)-allfiles.count('')+1 == 4:
    inters = sorted(intersect(logstates,treestates,gmrfstates,ratestates))


#determines subsampling frequency
subsample = inters[1]-inters[0]

print '\n'

#some stats about the files
for files,states in zip(filenames,statesfiles):
    if len(states) != 0:
        print 'Number of states in %s file: %s'%(files,len(states))

print '\nStates shared by all files:'
for unit in range(0,len(inters)):
    if len(inters) < 50:
        print '%s\t%s'%(unit+1,inters[unit])
    else:
        print '%s'%(len(inters))
        break

print '\nSubsampling frequency: %s\n'%(subsample)

#statesfiles contains all the states in each file
#if all files share the same numbers of states then len(status) == sum(status)
status = []
for states in statesfiles:
    if len(states) != 0:
        if len(inters) == len(states):
            status.append(1)
        else:
            status.append(0)

#if states do not completely overlap between all files this makes new files
#with cleaned and renumbered states
if len(status) != sum(status):
    #collects states common to all files
    currstate=-subsample
    for i in range(0,len(inters)-1):
        if int(inters[i]) != (currstate+subsample):
            if inters[i-1]+subsample == inters[i]-subsample:
                print '\nState %s is missing'%(inters[i-1]+subsample)
                continuous.append(str(inters[i]))
                currstate=inters[i]
            else:
                print '\nStates %s to %s (%s in total) are missing\n'%(inters[i-1]+subsample,inters[i]-subsample,(((inters[i]-subsample)-(inters[i-1]+subsample))/subsample))
                continuous.append(str(inters[i]))
                currstate=inters[i]
        else:
            continuous.append(str(inters[i]))
            currstate=inters[i]


    #opens temporary files created previously
    logtemp = csv.reader(open(logfile+'2.txt','rb'),delimiter='\t',quotechar='"')
    treestemp = open(treefile,'r')
    
    if gmrffile != '':
        gmrftemp = csv.reader(open(gmrffile+'2.txt','r'),delimiter='\t',quotechar='"')
        
    if ratesfile != '':
        ratestemp = csv.reader(open(ratesfile+'2.txt','r'),delimiter='\t',quotechar='"')

    #creates corrected files
    newlog = open(str(logfile)+'corrected.txt','w')
    newtrees = open(str(treefile)+'corrected.txt','w')

    if gmrffile != '':
        newgmrf = open(str(gmrffile)+'corrected.txt','w+')
    
    if ratesfile != '':
        newrates = open(str(ratesfile)+'corrected.txt','w+')

    #print renumbered states and values to file only if they are shared between all files
    logcounter=-1
    for unit in logtemp:
        if 'a' in unit[0]:
            newlog.write('\n')
            newlog.write('\t'.join(unit))
        elif unit[0] in continuous:
            del unit[0]
            logcounter+=1
            newlog.write('\n%s\t'%(logcounter))
            newlog.write('\t'.join(unit))

    newlog.close()
    print 'New log file saved'
    
    treescounter=-1
    for unit in treestemp:
        P = re.search("tree STATE_[0-9]+",unit)
        if "tree STATE_" not in unit:
            newtrees.write(unit)
        if P is not None:
            if str(P.group()[11:]) in continuous:
                treescounter+=1
                newtrees.write('\ntree STATE_%s\t'%(treescounter))
                newtrees.write(unit[len(P.group()):])
    newtrees.write('End;')
    newtrees.close()
    print 'New trees file saved'

    if gmrffile != '':
        newgmrf = open(str(gmrffile)+'corrected.txt','wb')
        gmrfcounter=-1
        for unit in gmrftemp:
            if 'a' in unit[0]:
                newgmrf.write('\n')
                newgmrf.write('\t'.join(unit))
            elif unit[0] in continuous:
                del unit[0]
                gmrfcounter+=1
                newgmrf.write('\n%s\t'%(gmrfcounter))
                newgmrf.write('\t'.join(unit))
        newgmrf.close()
        print 'New gmrf file saved'

    if ratesfile != '':
        newrates = open(str(ratesfile)+'corrected.txt','wb')
        ratescounter=-1
        for unit in ratestemp:
            if 'a' in unit[0]:
                newrates.write('\n')
                newrates.write('\t'.join(unit))
            elif unit[0] in continuous:
                del unit[0]
                ratescounter+=1
                newrates.write('\n%s\t'%(ratescounter))
                newrates.write('\t'.join(unit))
        newrates.close()
        print 'New rates file saved'

else:
    print 'All files already have the same numbers of states!\n'

print '\n'

#removes temporary files
for files in allfiles:
    if files != '':
        print 'Temporary file %s2.txt removed'%(files)
        os.remove('%s2.txt'%(files))

print '\nDone!\n'
