import math
import os
import random

from PIL import Image
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon


#PARAMETERS TO CUSTOM :

pool = Polygon([(70,995),(70,80),(1840,90), (1840,995),(70,995)]) #Polygon representing the pool table possible balls center positions
classes = ['red','yellow','black','white','cue_extrimity','blue_tape']

#dataset split train-valid-test : to choose
train_nb = 2
valid_nb = 1
test_nb = 1

#output images size
size = 320,180 #given background size is (1920,1080)

#apply gray shades for output images
grayshade = False

#objects quantity on samples
max_red_ball    = 8
max_yellow_ball = 8
max_black_ball  = 8
max_white_ball  = 8
max_cue         = 1
max_obstacles   = 1


def createPointInPolygon(polygon): #return a point inside the given polygon
    point = Point(-1,-1)
    minx, miny, maxx, maxy = polygon.bounds
    while not polygon.contains(point):
        point = Point(random.randint(minx, maxx), random.randint(miny, maxy))
    return int(point.x),int(point.y)

def touchingAnotherBall(x,y,r):
    for tup in balls:
        if((x-tup[0])*(x-tup[0])+(y-tup[1])*(y-tup[1])<(tup[2]+r)**2):
            return True #yes
    return False #no

def placeInImage(background, img_to_paste,x,y): #place image in background at x,y (x,y are center of the image)
    return background.paste(img_to_paste,(int(x-(img_to_paste.size[0]/2)),int(y-(img_to_paste.size[1]/2))),img_to_paste)

def selectRandomFileInFolder(filename):
    return random.choice(os.listdir(filename)) #return a string. Ex: background_5.jpg

def MakeWhiteTransparentBall(img):
    img = img.convert("RGBA")
    datas = list(img.getdata())

    width, height = img.size
    a=img.size[0]/2
    b=img.size[1]/2
    r=(a+b-1)/2
    datas = [datas[i * width:(i + 1) * width] for i in range(height)]
    for x in range(height):
        for y in range(width):
            if datas[x][y][0] > 195 and datas[x][y][1] > 195 and datas[x][y][2] > 195 and (((x-a)**2)+((y-b)**2))>(r**2):
                datas[x][y]=(255, 255, 255, 0)
    newData= [item for sublist in datas for item in sublist]
    img.putdata(newData)
    return img

def MakeWhiteTransparent(img):
    img = img.convert("RGBA")
    datas = img.getdata()

    newData = []
    for item in datas:
        if item[0] > 235 and item[1] > 235 and item[2] > 235:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)

    img.putdata(newData)
    return img

def rotate(origin, point, angle): 
    #counterclockwise rotation
    #angle in radian
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return int(qx), int(qy)

def changeCoordSystem(coord,l,h):
    a=coord[0]+l/2
    b=h/2-coord[1]
    return a,b

def verticalbox(tab):
    x=[]
    y=[]
    for i in tab:
        x.append(i[0])
        y.append(i[1])
    a=min(x),min(y)
    b=max(x),min(y)
    c=min(x),max(y)
    d=max(x),max(y)
    return a,b,c,d     

def rectangleToTxtYolo(l,r,t,b):
    x=(((r+l)/2)/background.size[0])
    y=(((b+t)/2)/background.size[1])
    u=((r-l)/background.size[0])
    v=((b-t)/background.size[1])
    return x,y,u,v

def writeFile(classe,x,y,u,v):
    dw=background.size[0]
    dh=background.size[1]
    l = int((x - u / 2) * dw)
    r = int((x + u / 2) * dw)
    t = int((y - v / 2) * dh)
    b = int((y + v / 2) * dh)
    
    #if outside of image:
    if l < 0:
        l = 0
    if r > dw - 1:
        r = dw - 1
    if t < 0:
        t = 0
    if b > dh - 1:
        b = dh - 1
    if l>dw-1 or r<0 or t>dh-1 or l<0:
        return 
    
    x,y,u,v = rectangleToTxtYolo(l,r,t,b)
    file1.write(str(classe)+" "+str(x)+" "+str(y)+" "+str(u)+" "+str(v)+"\n")  

def placeBalls(nb,filename): 
    #nb is the number of ball to place
    #filename is the folder path of balls to place
    for _ in range(nb):
        point= createPointInPolygon(pool)
        img= Image.open(filename + '/' +selectRandomFileInFolder(filename),'r')
        while(touchingAnotherBall(point[0],point[1],img.size[0]/2)==True):
            point=createPointInPolygon(pool)
        img=MakeWhiteTransparentBall(img)
        placeInImage(background, img,point[0],point[1])
        file1.write(
            str(classes.index(filename))         +" "
            + str(point[0]/background.size[0])   +" "
            + str(point[1]/background.size[1])   +" "
            + str(img.size[0]/background.size[0])+" "
            + str(img.size[1]/background.size[1])+"\n")
        balls.append((point[0],point[1],int(img.size[0]/2)))

def placeCue(filename):
    img= Image.open(filename + '/' +selectRandomFileInFolder(filename),'r')
    img = MakeWhiteTransparent(img)

    #cue dimension on normal pic
    l_n,_ = img.size

    #rotation
    angle = random.randint(0,360)
    img = img.rotate(angle, expand=True)

    #cue_extrimity on rotated pic (but without rotation)
    l_r,h_r = img.size
    topleft=(l_n/2-41,8) #COORDINATES TO CHANGE
    topright=(l_n/2-1,8)
    downleft=(l_n/2-41,-8)
    downright=(l_n/2-1,-8)

    #Blue tape on rotated pic (but without rotation)
    bluetopleft=(l_n/2-185,5)
    bluetopright=(l_n/2-160,5)
    bluedownleft=(l_n/2-185,-11)
    bluedownright=(l_n/2-160,-11)

    #cue_extrimity on rotated pic (with rotation)
    origin = (0,0)
    topleft = changeCoordSystem(rotate(origin, topleft, math.radians(angle)),l_r,h_r)
    topright = changeCoordSystem(rotate(origin, topright, math.radians(angle)),l_r,h_r)
    downleft = changeCoordSystem(rotate(origin, downleft, math.radians(angle)),l_r,h_r)
    downright = changeCoordSystem(rotate(origin, downright, math.radians(angle)),l_r,h_r)

    #Blue tape on rotated pic (with rotation)
    bluetopleft = changeCoordSystem(rotate(origin, bluetopleft, math.radians(angle)),l_r,h_r)
    bluetopright = changeCoordSystem(rotate(origin, bluetopright, math.radians(angle)),l_r,h_r)
    bluedownleft = changeCoordSystem(rotate(origin, bluedownleft, math.radians(angle)),l_r,h_r)
    bluedownright = changeCoordSystem(rotate(origin, bluedownright, math.radians(angle)),l_r,h_r)

    topleft,topright,downleft,downright=verticalbox([topleft,topright,downleft,downright])
    bluetopleft,bluetopright,bluedownleft,bluedownright=verticalbox([bluetopleft,bluetopright,bluedownleft,bluedownright])

    #Place Cue in image
    point= createPointInPolygon(pool)
    placeInImage(background, img,point[0],point[1])

    #Write txt file
    writeFile(classes.index('cue_extrimity'),(((topleft[0]+downright[0])/2)+point[0]-l_r/2)/background.size[0],(((topleft[1]+downright[1])/2)+point[1]-h_r/2)/background.size[1],(topright[0]-topleft[0])/background.size[0],(downleft[1]-topleft[1])/background.size[1])
    writeFile(classes.index('blue_tape'),(((bluetopleft[0]+bluedownright[0])/2)+point[0]-l_r/2)/background.size[0],(((bluetopleft[1]+bluedownright[1])/2)+point[1]-h_r/2)/background.size[1],(bluetopright[0]-bluetopleft[0])/background.size[0],(bluedownleft[1]-bluetopleft[1])/background.size[1])

def placeObstacle(filename):
    img= Image.open(filename + '/' +selectRandomFileInFolder(filename),'r')
    img = MakeWhiteTransparent(img)
    angle = random.randint(0,360)
    img=img.rotate(angle)
    point= createPointInPolygon(pool)
    placeInImage(background, img,point[0],point[1])


if __name__ == "__main__":
    steps = ["train","valid","test"]
    for step in steps:
        nb_sample = 0
        if step == "train": nb_sample=train_nb
        if step == "valid": nb_sample=valid_nb
        if step == "test" : nb_sample=test_nb
        for i in range(nb_sample): #Le nombre de data que l'on veut créer
            background = Image.open('background/' +selectRandomFileInFolder("background"),'r')
            txt = "dataset/" + step +"/labels/"+"%s.txt" % str(i).zfill(4)
            file1 = open(txt,"w")
            balls=[] #repertories of balls coordinates and radius

            nb_red = random.randint(0,max_red_ball) #both boundaries included
            nb_yellow = random.randint(0,max_yellow_ball)
            nb_black = random.randint(0,max_black_ball)
            nb_white = random.randint(0,max_white_ball)
            cue = random.randint(0,max_cue)
            obstacle = random.randint(0,max_obstacles)

            print(step,i)
            print("nb red                  :", nb_red)
            print("nb yellow               :", nb_yellow)
            print("nb black                :", nb_black)
            print("nb white                :", nb_white)
            print("cue?                    :", 'Yes' if cue == 0 else 'No')
            print("obstacle?               :", 'Yes' if obstacle == 0 else 'No', end="\n\n")

            placeBalls(nb_red,"red")
            placeBalls(nb_yellow,"yellow")
            placeBalls(nb_black,"black")
            placeBalls(nb_white,"white")
            if(cue==0): placeCue("cue")
            if(obstacle==0): placeObstacle("obstacle")

            file1.close()
            outfile = "dataset/" + step +"/images/"+"%s.jpeg" % str(i).zfill(4)
            if grayshade:
                background = background.convert('L') #apply grayshade transformation
            background.thumbnail(size, Image.ANTIALIAS)
            background.save(outfile, "JPEG")