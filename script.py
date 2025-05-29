import os
import re
from PIL import Image
from wand.image import Image as wandImg


#Create local files
wd = os.path.realpath(__file__)[0:len(os.path.realpath(__file__))-9]
gif = os.path.join(wd, "0-gif")
b_frames = os.path.join(wd,"1-big_frames")
s_frames = os.path.join(wd,"2-small_frames")
s_text = os.path.join(wd,"3-small_text")
out_loc = os.path.join(wd, "4-output_file")

if not os.path.exists(gif):
    os.makedirs(gif)
if not os.path.exists(b_frames):
    os.makedirs(b_frames)
if not os.path.exists(s_frames):
    os.makedirs(s_frames)
if not os.path.exists(s_text):
    os.makedirs(s_text)
if not os.path.exists(out_loc):
    os.makedirs(out_loc)
# ==========

# Get the name of the gif and create output file
print("Please place your gif in "+gif+" and press enter.\n")
input("[Press ENTER when you're ready.]\n")
print(str(len(os.listdir(gif)))+" files found.\n")

for a in os.listdir(gif):
    outname = a[0:len(a)-4] + "_lcd_animated"  
out_file = os.path.join(os.path.join(out_loc, outname), outname + ".ino")

if not os.path.exists(os.path.join(out_loc,outname)):
    os.makedirs(os.path.join(out_loc,outname))

print("The folders 0 to 3 will be cleared. be sure that there's nothing you need still in there.\n")
input("[Press ENTER to start.]\n")
# ==========

# Clearing folders
print("Clearing "+b_frames)
for f in os.listdir(b_frames):
    os.remove(os.path.join(b_frames,f))
print("Done.")
print("Clearing "+s_frames)
for f in os.listdir(s_frames):
    os.remove(os.path.join(s_frames,f))
print("Done.")
print("Clearing "+s_text)
for f in os.listdir(s_text):
    os.remove(os.path.join(s_text,f))
print("Done.")
if os.path.isfile(out_file):
    print("Deleting "+out_file)
    os.remove(out_file)
    print("Done.\n")
# ========== 

# gif to png frames
print("Changing gif to png and saving to "+b_frames)

for filename in os.listdir(gif):
    if filename.lower().endswith('.gif'):
        gif_path = os.path.join(gif, filename)

frame = Image.open(gif_path)
nframes = 0
while frame:
        frame.save( '%s/%s_%s.png' % (b_frames, os.path.splitext(os.path.basename(gif_path))[0], nframes ) )
        nframes += 1
        try:
            frame.seek( nframes )
        except EOFError:
            break;

print("DONE converting gif to png frames."+b_frames)
# ==========


print("Changing size and saving to "+s_frames)
# conversion
for f in sorted(os.listdir(b_frames)):
    with wandImg(filename = os.path.join(b_frames,f)) as img:
        img.resize(20,16)
        img.threshold(0.5)
        img.save(filename = os.path.join(s_frames,f))
# ==========


print("DONE converting. (1/2)\n")
print("Converting to byte arrays and saving in "+s_text)
# Conversion
for frame in sorted(os.listdir(s_frames)):
    in_loc = os.path.join(s_frames,frame)
    out_loc = os.path.join(s_text,frame)
    img = Image.open(in_loc)
    pix = img.load()
    for y in range(16):
        line = ""
        for x in range(20):
            if pix[x,y] < 127:
                val = "0"
            else:
                val = "1"
            line = line + val
        if y <= 7:
            f = open(out_loc[0:len(out_loc)-4]+"_A.txt","a")
            f.write(line[0:5]+"\n")
            f.close()
            f = open(out_loc[0:len(out_loc)-4]+"_B.txt","a")
            f.write(line[5:10]+"\n")
            f.close()
            f = open(out_loc[0:len(out_loc)-4]+"_C.txt","a")
            f.write(line[10:15]+"\n")
            f.close()
            f = open(out_loc[0:len(out_loc)-4]+"_D.txt","a")
            f.write(line[15:20]+"\n")
            f.close()
        else:
            f = open(out_loc[0:len(out_loc)-4]+"_E.txt","a")
            f.write(line[0:5]+"\n")
            f.close()
            f = open(out_loc[0:len(out_loc)-4]+"_F.txt","a")
            f.write(line[5:10]+"\n")
            f.close()
            f = open(out_loc[0:len(out_loc)-4]+"_G.txt","a")
            f.write(line[10:15]+"\n")
            f.close()
            f = open(out_loc[0:len(out_loc)-4]+"_H.txt","a")
            f.write(line[15:20]+"\n")
            f.close()
# ==========
print("DONE converting. (2/2)\n")

# lcd address input
while True:
    lcd_address = input("Give your LCD Screen Addrees (for example 0x27) : \n")

    if re.fullmatch(r'[0-9]x[0-9]{2}', lcd_address):
        print("Valid address:", lcd_address)
        break  
    else:
        print("Wrong format!!  True format example(0x19 =>  number x number number\n)")
# ==========      


print("Building .ino file in "+out_loc)
# Building
f = open(out_file,"w")
f.write("#include <LiquidCrystal_I2C.h>\n")
f.write("#include <Wire.h>\n")
f.write("LiquidCrystal_I2C lcd("+ lcd_address +",16,2);\n")
# b arrays
for bfile in sorted(os.listdir(s_text)):
    bpos = 0
    f.write("byte b"+bfile[0:len(bfile)-4]+"[8] = {\n")
    for bline in open(os.path.join(s_text,bfile),'r'):
        bpos = bpos + 1
        if len(bline) <= 6:
            if bpos < 8:
                f.write("0b"+bline+",\n")
            elif bpos == 8:
                f.write("0b"+bline)
            else:
                print("TOO MANY LINES IN "+os.path.join(s_text,bfile)+" ("+str(bpos)+")")
        else:
            print("LINES TOO SHORT OR LONG IN "+os.path.join(s_text,bfile)+" AT LINE "+str(bpos)+" LENGTH "+str(len(bline)-1)+" INSTEAD OF 5")
    f.write("};\n")
# setup
f.write("void setup() { \n")
f.write("lcd.init();\n")
f.write("lcd.backlight();\n")
f.write("lcd.clear(); }\n")
# loop
f.write("void loop() {\n")
# writes
lcd_pos = 0
for bfile in sorted(os.listdir(s_text)):
    if lcd_pos == 0:
        f.write("lcd.createChar(0, b"+bfile[0:len(bfile)-5]+"A);\n")
        f.write("lcd.createChar(1, b"+bfile[0:len(bfile)-5]+"B);\n")
        f.write("lcd.createChar(2, b"+bfile[0:len(bfile)-5]+"C);\n")
        f.write("lcd.createChar(3, b"+bfile[0:len(bfile)-5]+"D);\n")
        f.write("lcd.createChar(4, b"+bfile[0:len(bfile)-5]+"E);\n")
        f.write("lcd.createChar(5, b"+bfile[0:len(bfile)-5]+"F);\n")
        f.write("lcd.createChar(6, b"+bfile[0:len(bfile)-5]+"G);\n")
        f.write("lcd.createChar(7, b"+bfile[0:len(bfile)-5]+"H);\n")
        f.write("delay(200);\n")
        f.write("lcd.setCursor(0,0);\n")
        f.write("lcd.write((byte)0);\n")
    elif lcd_pos < 4:
        f.write("lcd.setCursor("+str(lcd_pos)+", 0);\n")
        f.write("lcd.write((byte)"+str(lcd_pos)+");\n")
    else:
        f.write("lcd.setCursor("+str(lcd_pos-4)+", 1);\n")
        f.write("lcd.write((byte)"+str(lcd_pos)+");\n")
    if lcd_pos >= 7:
        lcd_pos = 0
    else:
        lcd_pos = lcd_pos + 1
# end
f.write("}")
f.close()
# ==========
print("DONE building file. The file you're looking for is "+out_file)
print("\nThe temporary files can be cleaned up automatically. If you want that, press now enter. (Doesn't afffect original frames.)")
input("[Press ENTER for cleanup.]\n")
# Cleanup
print("Clearing "+b_frames)
for f in os.listdir(b_frames):
    os.remove(os.path.join(b_frames,f))
print("Done.")
print("Clearing "+s_frames)
for f in os.listdir(s_frames):
    os.remove(os.path.join(s_frames,f))
print("Done.")
print("Clearing "+s_text)
for f in os.listdir(s_text):
    os.remove(os.path.join(s_text,f))
print("Done.")
# ==========
print("DONE cleaning up.")
