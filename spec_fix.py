import os

lines = []

f = open("AudicaSongSpeeder.spec", "r")

for line in f:
    lines.append(line)
    
f.close()

newlines = []

newlines.append("from kivy.deps import sdl2, glew\n")
newlines.append("\n")

for line in lines:
    if "COLLECT" in line:
        path = ", Tree(" + "\"" + os.getcwd() + os.sep + "source\"" + "),\n"
        line = line.split(",", 1)[0] + path
    elif "               strip=False" in line:
        newlines.append("               *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],\n")
    newlines.append(line)
    
f = open("AudicaSongSpeeder.spec", "w")

for line in newlines:
    f.write(line)
    
f.close()