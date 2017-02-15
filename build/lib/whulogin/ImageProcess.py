#encoding=utf8
import os
from PIL import *
import Image
from pytesser import *
import pytesseract
import re

codeFile = 'code.png'
threshold = 140
table = []
for i in range(256):
    if i < threshold:
        table.append(0)
    else:
        table.append(1)
def RGB2BlackWhite(infile, outfile):
    img = Image.open(infile)
    imgry = img.convert("L")
    out = imgry.point(table, '1')
    out.save(outfile)

    img = Image.open(outfile)
    (w, h) = img.size
    for x in xrange(w - 1):
        for y in xrange(h - 1):
            pos = (x, y)
            rgb = img.getpixel(pos)
            if x > 0 and y > 0:
                rgb_up = img.getpixel((x, y - 1))
                rgb_down = img.getpixel((x, y + 1))
                rgb_left = img.getpixel((x - 1, y))
                rgb_right = img.getpixel((x + 1, y))
                total = rgb_up + rgb_down + rgb_left + rgb_right
                if total == 1020:
                    img.putpixel(pos, 255)
    img.save(outfile)

def getCode(infile):
    RGB2BlackWhite(infile, codeFile) 
    img = Image.open(codeFile)
    img.load()
    img.split()
    text =  pytesseract.image_to_string(img)
    #print text
    
    pattern = '[^a-zA-Z0-9]'
    reg = re.compile(pattern)
    code = reg.sub("", text)
    os.remove(codeFile)
    return code

#print GetCode("/Users/ZhuChao/Downloads/GenImg.jpeg")
#RGB2BlackWhite("/Users/ZhuChao/Downloads/GenImg.jpeg", codeFile)

