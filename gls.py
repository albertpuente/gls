#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Graphical List Directory contents command
# Author: Albert Puente Encinas
# Version: 0.2

# Hint: chmod +x gls.py && alias gls=$PWD/gls.py

from __future__ import division
import os, sys, time, re
from math import ceil
import subprocess # less x.pdf

# Initial definitions

nLines = 6
elem_cols = None

try:
    if len(sys.argv) > 1: nLines = max(0, int(sys.argv[1]))    
    if len(sys.argv) > 2: elem_cols = max(1, int(sys.argv[2]))
except ValueError:
    print "Uknown parameter"
    sys.exit()
        
DEFAULT_WIDTH = 36
HEIGHT = 4 + nLines

getConsoleSize = lambda: [int(x) for x in os.popen('stty size', 'r').read().split()]    
def disp(c): sys.stdout.write(c)

rows, cols = getConsoleSize()

if cols < 30:
    print 'Console size is too small (' + str(cols) + 'x' + str(rows) + ')'
    sys.exit()

fileNames = sorted(os.listdir(os.getcwd()))

# Format
if not elem_cols: # The user has not specified the desired number of cols
    elem_cols = int(cols/DEFAULT_WIDTH)
elem_width = int(cols/elem_cols)
elem_rows = int(ceil(len(fileNames)/elem_cols))
elem_height = HEIGHT

rows = elem_rows * elem_height

BUFF = [[' ' for _ in range(cols)] for _ in range(rows)] # To be printed

# Functions
def square(x1, x2, y1, y2, border = 'other'):    
    if border == 'file':     box = u'┌└┐┘─│'
    elif border == 'folder': box = u'╔╚╗╝═║'
    else:                    box = u'┏┗┓┛━┃'    
    BUFF[y1][x1] = box[0]; BUFF[y2][x1] = box[1]
    BUFF[y1][x2] = box[2]; BUFF[y2][x2] = box[3]
    for i in range(x1+1, x2): BUFF[y1][i] = BUFF[y2][i] = box[4]
    for i in range(y1+1, y2): BUFF[i][x1] = BUFF[i][x2] = box[5]
    
def insertWord(x1, y1, s):    
    for i in range(len(s)):
        BUFF[y1][x1+i] = s[i]        

# Run
colours = dict()

sizeLabels = ['B', 'kB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB']
printableExts = ['.cpp', '.py', '.h', '.txt', '.c', '.md', '.pyx']

elem_col = 0
elem_row = 0
for fileName in fileNames:
    fullName = os.getcwd() + '/'+ fileName
    _, file_extension = os.path.splitext(fullName)
    size = float(os.path.getsize(fullName))
    sizeOrder = 0
    while size > 1024:
        size /= 1024
        sizeOrder += 1
    sizeText = '(' + '{0:.2f}'.format(round(size,2)) + ' ' + sizeLabels[sizeOrder]  + ')'
    
    x1 = elem_col*elem_width
    x2 = x1 + elem_width - 1    
    y1 = elem_row*elem_height
    y2 = y1 + elem_height - 1
    if os.path.isdir(fileName):
        square(x1, x2, y1, y2, 'folder')
        colours[(y1, x1+1)] = "\033[1;34;10m"
        insertWord(x1+1, y2, 'FOLDER')        
        try:
            subNames = sorted(os.listdir(fullName))
        except:
            subNames = []
        l = 0
        subNames = subNames[:elem_height-4]
        for line in subNames:
            if len(line) > elem_width - 5:
                line = line[:elem_width-7]+'...'
            insertWord(x1+2, y1 + l + 2, line)
            colours[(y1+ l + 2, x1+2)] = "\033[0;32;10m"
            colours[(y1+ l + 2, x1+2 + len(line))] = "\033[0;0;0m"
            l += 1
        
    elif os.path.isfile(fullName) and os.access(fullName, os.X_OK) and file_extension == '':
        colours[(y1, x1+1)] = "\033[1;31;10m"
        square(x1, x2, y1, y2)
        insertWord(x1+1, y2, 'EXE')
        insertWord(x1+2, y1 + 2, "Last  modified:")
        insertWord(x1+2, y1 + 3, str(time.ctime(os.path.getmtime(fullName))))
        # insertWord(x1+2, y1 + 5, "Created:")
        # insertWord(x1+2, y1 + 6, str(time.ctime(os.path.getctime(fullName)))) 
    else:
        colours[(y1, x1+1)] = "\033[1;32;10m"
        square(x1, x2, y1, y2, 'file')    
        modTime = filter(None, time.ctime(os.path.getmtime(fullName)).split(' '))
        insertWord(x1+1, y2, '('+modTime[2]+'/'+modTime[1]+'/'+modTime[4]+' '+modTime[3]+')')

    # Contents
    if file_extension in printableExts:
        head = list()
        with open(fileName) as f:
            n = 0
            while n < elem_height - 4:
                try:
                    head.append(next(f))
                except StopIteration:
                    break
                n += 1
        l = 0
        for line in head:
            if len(line) > elem_width - 5:
                line = line[:elem_width-7]+'...'
            insertWord(x1+2, y1 + l + 2, line)
            colours[(y1+ l + 2, x1+2)] = "\033[0;36;10m"
            colours[(y1+ l + 2, x1+2 + len(line))] = "\033[0;0;0m"
            l += 1
    elif file_extension == '.pdf':
        output = subprocess.Popen(["less", fileName], stdout=subprocess.PIPE).communicate()[0]
        l = 0
        output = output.split('\n')
        output = output[:elem_height - 4]
        for line in output:
            if len(line) > elem_width - 5:
                line = line[:elem_width-7]+'...'
            insertWord(x1+2, y1 + l + 2, ''.join(c for c in line if c.isalnum() or c == ' '))
            colours[(y1+ l + 2, x1+2)] = "\033[0;33;10m"
            colours[(y1+ l + 2, x1+2 + len(line))] = "\033[0;0;0m"
            l += 1
    
    if len(fileName) > elem_width-3:
        fileName = fileName[:elem_width-5] + '...'
        
    insertWord(x1+1, y1, fileName)    
    colours[(y1, x1+len(fileName)+1)] = "\033[0;0;0m"    
    insertWord(x2-len(sizeText), y2, sizeText)
    # Next
    elem_col += 1
    if elem_col == elem_cols:
        elem_col = 0
        elem_row += 1

# Display
for r in range(rows):
    for c in range(cols):
        if (r,c) in colours:
            disp(colours[(r,c)])
        if BUFF[r][c] in ['\n', '\t']:
            disp(' ')
        else:
            disp(BUFF[r][c])