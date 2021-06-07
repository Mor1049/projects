from csv import reader, DictReader
import sys
import csv

# Ensure correct usage
if len(sys.argv) != 3:
    exit("Usage: python dna.py data.csv sequence.txt")

# Creating a dictionary to store the sequences the program counts
dnasequences = {}

# Read from csv file and store DNA Sequences
with open(sys.argv[2]) as dna_file:
    DNA_read = csv.reader(dna_file)
    for row in DNA_read:
        dna_list = row

# Storing the sequences in a string
DNASTRING = dna_list[0]

# Extracting the sequences from the dna database to a list
with open(sys.argv[1]) as people_file:
    people = csv.reader(people_file)
    for row in people:
        dnaseq = row
        del dnaseq[0]
        break

for item in dnaseq:
    dnasequences[item] = 1

# Iterating through the sequence dictionary and counting repetitions

for key in dnasequences:
    k = len(key)
    maxlength = 0
    templength = 0

    for i in range(len(DNASTRING)):
        while templength > 0:
            templength -= 1
# Increase counter if the key finds a consecutive DNA segment
        if DNASTRING[i: i+k] == key:
            while DNASTRING[i-k: i] == DNASTRING[i: i+k]:
                templength += 1
                i += k

# Comparing the value to previous longest sequence and replacing previous longest value if it is longer
        if templength > maxlength:
            maxlength = templength


# Storing longest sequence in a dictionary with the key
    dnasequences[key] += maxlength

# Opening people database and checking if there is a match
with open(sys.argv[1]) as people_file:
    people = DictReader(people_file)
    for person in people:
        dnamatch = 0
# Comparing the sequences to the people and printing names
        for DNASTRING in dnasequences:
            if dnasequences[DNASTRING] == int(person[DNASTRING]):
                dnamatch += 1
        if dnamatch == (len)(dnasequences):
            print(person["name"])
            exit()
    else:
        print("No match")

