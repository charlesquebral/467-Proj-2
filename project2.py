import argparse
import os, getpass
import sys
import csv
import pymongo
import datetime

#args
parser = argparse.ArgumentParser(description ='467 Project 2 - Charles Quebral')
parser.add_argument("-f",dest="workFiles", nargs = '+', help="Baselight/Flames Text files")
parser.add_argument("-x",dest="xyTechFiles", help="Xytech file input")
parser.add_argument("-v", "--verbose", action="store_true",help="Console output on/off")
parser.add_argument("-o",dest="outputMode", help="to CSV or Database")
args = parser.parse_args()

subarr = []
xytechOrders = []
fixedOrders = []

def getRanges(fls):
    subarr = []
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

def handle(filestr, xy, num):
    job = filestr
    xyt = xy
    if os.path.exists(job) and os.path.exists(xyt):
        dateOnFile = str(job.split("_")[2].split(".")[0])
        with open(xyt) as f:
            headers = []
            lines1 = f.read().splitlines()
            for ls1 in lines1:
                if (getLocation(ls1, 1) != ""):
                    xytechOrders.append(getLocation(ls1, 0))
                if(ls1.split(":")[0] == "Producer" or ls1.split(":")[0] == "Operator" or ls1.split(":")[0] == "Job"):
                    string = (ls1.split(":")[1:])
                    if args.verbose and num == 0: print(ls1)
                    headers.append(str(string[0]))
                elif(ls1.split(" ")[0] == "Please"):
                    headers.append(ls1)
            if (str(args.outputMode) == 'csv') and (num == 0):
                with open("output" + dateOnFile + ".csv", 'a', newline='') as csvfile:
                    writer = csv.writer(csvfile) 
                    writer.writerow(headers)
                    writer.writerow([])
                    writer.writerow([])
            if args.verbose: print("Creating ranges for file" + str(filestr) + " on workorder " + str(xy))
            with open(job) as f:
                lines = f.read().splitlines()
                for ls in lines:
                    if ls != "":
                        lsplit = ls.split(" ")
                        if (job[0] == 'B'): #if Baselight
                            first, rest = lsplit[0], lsplit[1:]
                            loc = getLocation(first, 2)
                        elif (job[0] == 'F'): #if Flame
                            first, second, rest = lsplit[0], lsplit[1], lsplit[2:]
                            loc = str(second)

                        for i in rest:
                            if (i == "<err>" or i == "<null>" or i == ""):
                                rest.remove(i)
                        subarr = getRanges(rest)
                        for xy in xytechOrders:
                            xyresult = getLocation(xy, 3)
                            if xyresult == loc:
                                machine = str(xy).split("/")[1]
                                nameOnFile = str(job.split("_")[1])
                                dateOnFile = str(job.split("_")[2].split(".")[0])
                                submitteddate = str(datetime.date.today()).replace("-", "")
                                currdict = { 
                                        "User": user,
                                        "Machine": machine, 
                                        "Name": nameOnFile, 
                                        "File Date": dateOnFile,
                                        "Submit Date": submitteddate
                                        }
                                if (args.outputMode == 'db'):
                                    #Parse names for DB, handle collection 1
                                    mycol = mydb["col1"]
                                    if args.verbose: print("Data for collection 1: " + machine + ", " + nameOnFile + ", " + dateOnFile + ", " + submitteddate)
                                    #insert one
                                    existing_doc = mycol.find_one(currdict)
                                    if not existing_doc:
                                        x = mycol.insert_one(currdict)

                                for sub in subarr:
                                    rangestr = ""
                                    order = []
                                    if (len(sub) == 1):
                                        order.append(str(xy))
                                        order.append(str(sub[0]))  
                                    else:
                                        rangestr = str(sub[0]) + "-" + str(sub[len(sub) - 1])
                                        order.append(str(xy))
                                        order.append(rangestr)

                                    if (str(args.outputMode) == 'db'):
                                        #handle data collection 2
                                        mycol2 = mydb["col2"]
                                        location = str(order[0])
                                        if args.verbose: print("Data for collection 2: " + nameOnFile + ", " + dateOnFile + ", " + location + ", " + str(order[1]))
                                        currdict2 = { 
                                        "Name": nameOnFile, 
                                        "File Date": dateOnFile,
                                        "Location": location,
                                        "Range": str(order[1])
                                        }
                                        existing_doc = mycol2.find_one(currdict2)
                                        if not existing_doc:
                                            x2 = mycol2.insert_one(currdict2)
                                    elif (args.outputMode == 'csv'):
                                        with open("output" + dateOnFile + ".csv", 'a', newline='') as csvfile:
                                            writer = csv.writer(csvfile) 
                                            writer.writerow(order)
                subarr = []

if args.workFiles is None:
    print("No BL/Flames files selected")
    sys.exit(2)
else:
    user = str(getpass.getuser())
    #createdatabase
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["project2"]
    for i, file in enumerate(args.workFiles):
        if (str(args.outputMode) != 'db' and str(args.outputMode) != 'csv'):
            print("Please choose a valid output mode! {db, csv}")
        else:
            handle(file, args.xyTechFiles, i)
            xytechOrders = []
            fixedOrders = []