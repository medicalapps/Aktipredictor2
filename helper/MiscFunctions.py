import csv
import json
import os

'''
w  write mode
r  read mode
a  append mode

w+  create file if it doesn't exist and open it in (over)write mode
    [it overwrites the file if it already exists]
r+  open an existing file in read+write mode
a+  create file if it doesn't exist and open it in append mode
'''

def writetodisk(mydata, myfile):
    with open(myfile, 'a+', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(mydata)

def overwritelisttodisk(mydata, myfile):
    with open(myfile, 'w+', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(mydata)
    
def overwritetodisk(mydata, myfile):
    with open(myfile, 'w+', newline='') as file:
        writer = csv.writer(file,  delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
        for row in mydata:
            writer.writerow(row)


def writeJson(filename, Writedata):
    with open(filename, 'a+') as json_file:
        json.dump(Writedata, json_file)

def OverWriteJson(filename, Writedata):
    with open(filename, 'w+') as json_file:
        json.dump(Writedata, json_file)

