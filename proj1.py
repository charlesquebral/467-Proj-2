#COMP 467 Project 2 - Charles Quebral
#import Baselight file and xytech work order
import csv
f = open('Baselight_export.txt', 'r')
f = open('Xytech.txt', 'r')

subarr = []
xytechOrders = []
fixedOrders = []

def getRanges(fls):
    temp = []
    for i in range(len(fls)):
        if ((int(fls[i]) - int(fls[i - 1])) == 1) or i == 0:
            temp.append(int(fls[i]))
        else:
            subarr.append(temp)
            temp = [int(fls[i])]
    if temp:
        subarr.append(temp)
    return subarr

def getLocation(line, i):
    linesplit = line.split("/")[i:]
    result = "/".join(linesplit)
    return result

doHeaders = True

#parse Xytech.txt
with open('Xytech.txt') as f:
    headers = []
    lines1 = f.read().splitlines()
    for ls1 in lines1:
        if (getLocation(ls1, 1) != ""):
            xytechOrders.append(getLocation(ls1, 0))

        if(ls1.split(":")[0] == "Producer" or ls1.split(":")[0] == "Operator" or ls1.split(":")[0] == "Job"):
            string = (ls1.split(":")[1:])
            headers.append(str(string[0]))
        elif(ls1.split(" ")[0] == "Please"):
            headers.append(ls1)
    with open("output.csv", 'w', newline='') as csvfile:
        writer = csv.writer(csvfile) 
        writer.writerow(headers)
        writer.writerow([])
        writer.writerow([])

#parse Baselight_export.txt
with open('Baselight_export.txt') as f:
    lines = f.read().splitlines()
    for ls in lines:
        if ls != "":
            lsplit = ls.split(" ")
            first, rest = lsplit[0], lsplit[1:]
            for i in rest:
                if (i == "<err>" or i == "<null>" or i == ""):
                    rest.remove(i)
            subarr = getRanges(rest)
            for xy in xytechOrders:
                xyresult = getLocation(xy, 3)
                if xyresult == getLocation(first, 2):
                    for sub in subarr:
                        order = []
                        if (len(sub) == 1):
                            order.append(str(xy))
                            order.append(str(sub[0]))  
                        else:
                            rangestr = str(sub[0]) + "-" + str(sub[len(sub) - 1])
                            order.append(str(xy))
                            order.append(rangestr)
                        with open("output.csv", 'a', newline='') as csvfile:
                            writer = csv.writer(csvfile) 
                            writer.writerow(order)
        subarr = []