import picamera
import pygame
import time
import os
import shutil
import subprocess
from PIL import Image
from time import sleep



######## Settings
# Idle Time
IDLETIME = 30

# Time before changing to the next effect
DEMOCYCLETIME = 10

# Preview Alpha, 0-255
PREVIEW_ALPHA = 60

# Screen Dimensions
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# Number of Photos
NUMPHOTOS = 4

# Camera Rotation
CAMROTATION = 0
CAMFRAMERATE = 60

# Working Directory
globalWorkDir = '/home/pi/vancouver-se-monkeys'
globalDCIMDir = globalWorkDir + '/DCIM'

# Session Directory
globalSessionDir = ''

# Width of previous and next tap zones
ZONEWIDTH = 100

# Montage Settings
MONTAGESPACING_W = 30
MONTAGESPACING_H = 20
MONTAGE_W = 1920
MONTAGE_H = 2880


######## Global variables.
# For readable code
LEFTMOUSEBUTTON = 1

# Center of display
CENTER_X = SCREEN_WIDTH/2
CENTER_Y = SCREEN_HEIGHT/2

# Tap Zones
PREV_X = 10
PREV_Y = 0
NEXT_X = SCREEN_WIDTH - ZONEWIDTH * 3 - PREV_X
NEXT_Y = SCREEN_HEIGHT

# Start Box, Center of Screen?
START_MIN_X = CENTER_X-(ZONEWIDTH*2)
START_MAX_X = START_MIN_X+ZONEWIDTH*4
START_MIN_Y = CENTER_Y-(ZONEWIDTH*2)
START_MAX_Y = START_MIN_Y+ZONEWIDTH*4

# RGB Codes
rgbRED = (241, 241, 65)
rgbGREEN = (0,255,0)
rgbBLUE = (0,0,255)
rgbDARKBLUE = (0,0,128)
rgbWHITE = (255,255,255)
rgbBLACK = (0,0,0)
rgbPINK = (168,168,154)

# Background Color!
rgbBACKGROUND = rgbBLACK

# Initialise PyGame
pygame.init() # Initialise pygame
# Don't full screen until you have a way to quit the program. ;)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT),pygame.FULLSCREEN)
pygame.display.set_caption('Photo Booth')

# Setup the game surface
background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill(rgbBACKGROUND)
pygame.mouse.set_visible(True)
pygame.mouse.set_cursor((8, 8), (4, 4), (24, 24, 24, 231, 231, 24, 24, 24), (0, 0, 0, 0, 0, 0, 0, 0))

# Load images and scale them to the screen and tap zones. 
# At some point find a GO! or START! icon that works with the transparency and all that. 
ImgOK = pygame.image.load('images/OK.png')
ImgOK = pygame.transform.scale(ImgOK, (ZONEWIDTH*4, ZONEWIDTH*4))
ImgPointLeft = pygame.image.load('images/PointLeft.png')
ImgPointLeft = pygame.transform.scale(ImgPointLeft, (ZONEWIDTH*3, ZONEWIDTH*3))
ImgPointRight = pygame.image.load('images/PointRight.png')
ImgPointRight = pygame.transform.scale(ImgPointRight, (ZONEWIDTH*3, ZONEWIDTH*3))

# Fonts to be used.
smallfont = pygame.font.Font(None, 75) #Small font for on screen messages.
bigfont = pygame.font.Font(None, 200) # Big font for countdown.

########## Object Initializations.
camera = picamera.PiCamera()
camera.rotation = CAMROTATION
camera.framerate = CAMFRAMERATE
# Flip the camera horizontally so it acts like a mirror.
camera.hflip = True

# List of effects to cycle through.
globalEffectList = ['none','sketch','posterise','negative',
                    'hatch','watercolor','cartoon','washedout','solarize']
# Dictionary of friendly names for the various effects.
globalEffectDict = {'none': 'Normal','sketch':'Artist Sketch','posterise':'Poster',
                    'negative':'Negative Zone','hatch':'Crosshatch','watercolor':'Water Color',
                    'cartoon':'Monke','washedout':'Washed Out','solarize':'Solar Flare'}
# Current effect.
globalEffectCurr = 0
# Number of effects.
globalEffectLeng = len(globalEffectList)-1

# Photobooth SessionID
# When a session is in progress, touchscreen inputs are ignored. 
SessionID = 0

# Show instructions on screen?
ShowInstructions = True
LastTap = 0

# Run the Demo
RunDemo = True
RunDemoCounter = 0

 ########## Functions

# Replacing ShowTapZones() with a more generic UpdateDisplay(). 
# When I'm done, ShowTapZones() will do exactly what it says. 
# Update display will take care of deciding which elements should be on screen.
def UpdateDisplay():
    global screen
    global background
    # Blit everything to the screen
    screen.blit(background, (0, 0))
    pygame.display.flip()
    return
# End of function
 
# Draws the Previous, Next, and Start tap zones on screen.
def ShowTapZones():
    global screen
    global background
    background.fill(rgbBACKGROUND)  # Black background
    # Draw the Start tap zone on screen.
    pygame.draw.rect(background, rgbPINK, pygame.Rect(START_MIN_X -40, START_MIN_Y-40, 4*ZONEWIDTH +80, 4*ZONEWIDTH +80))

    background.blit(ImgPointLeft, (PREV_X, START_MIN_Y - 30))
    background.blit(ImgPointRight, (NEXT_X, START_MIN_Y - 30))
    background.blit(ImgOK, (START_MIN_X, START_MIN_Y))

    if ShowInstructions == True:
        SetInstructions()
    SetEffectText(globalEffectList[globalEffectCurr])
    UpdateDisplay()
    return
# End of function

def SetBlankScreen():
    background.fill(rgbBACKGROUND)
    UpdateDisplay()
    return
# End of function. 

# Show the instructions on screen.
def SetInstructions():
    global background
    global smallfont
    Text = "Click the monkey to take photos."
    Text = smallfont.render(Text, 1, rgbRED)
    textpos = Text.get_rect()
    textpos.centerx = background.get_rect().centerx
    height = Text.get_height()
    background.blit(Text,(textpos)) #Write the small text
    return

# Writes the current effect to the screen using PyGame. 
def SetEffectText(NewEffect):
    global globalEffectDict
    global background
    global smallfont
    #Text = "Effect: " + globalEffectDict[NewEffect]
    Text = "Effect: " + globalEffectDict[NewEffect]
    Text = smallfont.render(Text, 1, rgbRED)
    textpos = Text.get_rect()
    textpos.centerx = background.get_rect().centerx
    textpos.centery = SCREEN_HEIGHT - Text.get_height() + 30
    background.blit(Text,(textpos)) #Write the small text
    return

def QuitGracefully():
    camera.stop_preview()
    camera.close()
    pygame.quit()
    quit()
# End of function

# Process Input from the Left Mouse Button being depressed.
# Also tapping on the touch screen.
def LeftMouseButtonDown(xx, yy):
    # Detect Taps in Previous Zone
    if xx >= PREV_X and xx <= ZONEWIDTH:
        TapPrev()
    # Detect Taps in Next Zone
    elif xx >= NEXT_X and xx <= SCREEN_WIDTH:
        TapNext()
    # Detect Taps in the Start Zone
    elif xx >= START_MIN_X and yy >= START_MIN_Y and xx <= START_MAX_X and yy <= START_MAX_Y:
        TapStart()
    return
# End of function.

# Function to change effect.
def SetEffect(NewEffect):
    global globalEffectList
    global globalEffectCurr
    global camera
    print('Switching to effect ' + NewEffect)
    camera.image_effect = NewEffect
    SetEffectText(NewEffect)
    globalEffectCurr = globalEffectList.index(NewEffect)
    return
# End of function.

# Function to cycle effects forward.
def NextEffect():
    global globalEffectList
    global globalEffectCurr
    if SessionID != 0:
        return False
    if globalEffectCurr == globalEffectLeng:
        globalEffectCurr = 0
    else:
        globalEffectCurr = globalEffectCurr + 1

    NextEff = globalEffectList[globalEffectCurr]
    SetEffect(NextEff)
# End of function.

# Function to cycle effects backward.
def PrevEffect():
    global globalEffectList
    global globalEffectCurr
    if SessionID != 0:
        return False
    if globalEffectCurr == 0:
        globalEffectCurr = globalEffectLeng
    else:
        globalEffectCurr = globalEffectCurr - 1
    NextEff = globalEffectList[globalEffectCurr]
    SetEffect(NextEff)
    return True
# End of Function

# Generates a PhotoBoot Session
def SetupPhotoboothSession():
    global SessionID
    global globalWorkDir
    global globalSessionDir
    SessionID = int(time.time())  # Use UNIX epoc time as session ID.
    # Create the Session Directory for storing photos.
    globalSessionDir = globalWorkDir + '/' + str(SessionID)
    os.makedirs(globalSessionDir, exist_ok=True)
# End of function

def StartCameraPreview():
    camera.hflip = True
    camera.resolution = RES_PREVIEW
    camera.start_preview(alpha=PREVIEW_ALPHA)
# End of function.

def TakePhoto(PhotoNum):
    global SessionID
    global globalSessionDir
    PhotoPath = globalSessionDir + '/' + str(PhotoNum) + '.jpg'
    camera.stop_preview()
    camera.resolution = RES_PHOTO
    camera.hflip = False
    background.fill(rgbWHITE)
    UpdateDisplay()
    camera.capture(PhotoPath)
    camera.capture('/home/pi/vancouver-se-monkeys/discord_bot/'+str(PhotoNum) +'.jpg')
    background.fill(rgbBACKGROUND)
    UpdateDisplay()
    StartCameraPreview()
# End of function.

def RunCountdown():
    i = 3
    while i >= 0:
        if i == 0:
            string = 'MONKE!!!'
        else:
            string = str(i)
        text = bigfont.render(string, 1, rgbRED)
        textpos = text.get_rect()
        textpos.centerx = background.get_rect().centerx
        textpos.centery = background.get_rect().centery
        SetBlankScreen()
        background.blit(text, textpos)
        UpdateDisplay()
        i = i - 1
        sleep(1)
    # Blank Cheese off the screen.
    SetBlankScreen()
    UpdateDisplay()
    return
# End of function.

def ResetPhotoboothSession():
    global SessionID
    SessionID = 0
    StartCameraPreview()
    SetEffect('none')
# End of function.

def CopyMontageDCIM(montageFile):
    global globalDCIMDir
    # Use copy not copyfile to copy a file to a directory.
    if os.path.isdir(globalDCIMDir):
        return shutil.copy(montageFile,globalDCIMDir)
    else:
        return False
# End of function.

def RunPhotoboothSession():
    global NUMPHOTOS
    currentPhoto = 1 # File name for photo.
    SetupPhotoboothSession()
    while currentPhoto <= NUMPHOTOS:
        RunCountdown()
        TakePhoto(currentPhoto)
        currentPhoto = currentPhoto + 1
    montageFile = CreateMontage()
    CopyMontageDCIM(montageFile)
    print("Montage File: " + montageFile)
    PreviewMontage(montageFile)
    ResetPhotoboothSession()
# End of function.

# Function called when the Start zone is tapped.
def TapStart():
    global RunDemo
    print("Start")
    RunDemo = False
    # I think this will clear the screen?
    background.fill(rgbBACKGROUND)
    UpdateDisplay()
    RunPhotoboothSession()
    return
# End of Function.

# Function called when the Previous zone is tapped.
def TapPrev():
    global RunDemo
    RunDemo = False
    global ShowInstructions
    global LastTap
    print("Previous")
    ShowInstructions = False
    LastTap = time.time()
    PrevEffect()
    return
# End of Function

# Function called when the Next zone is tapped.
def TapNext():
    global ShowInstructions
    global LastTap
    global RunDemo
    RunDemo = False
    print("Next")
    ShowInstructions = False
    LastTap = time.time()
    NextEffect()
    return
# End of Function

def IdleReset():
    global ShowInstructions
    global LastTap
    global RunDemo
    LastTap = 0
    ShowInstructions = True
    RunDemo = True
    RunDemoCounter = 0
    SetEffect('none')
    UpdateDisplay()
# End of function.

# Creates the Montage image using ImageMagick.
def CreateMontage():
    global globalSessionDir
    global SessionID
    global globalWorkDir
    binMontage = 'montage '
    outFile = globalSessionDir + "/" + str(SessionID) + ".jpg"
    argsMontage = "-tile 2x6 "
    # Loop controls.
    incrementCounter = False
    photoCounter = 1
    for counter in range(1, NUMPHOTOS*2+1):
        argsMontage = argsMontage + str(globalSessionDir) + "/" + str(photoCounter) + ".jpg "
        if incrementCounter:
            photoCounter = photoCounter + 1
            incrementCounter = False
        else:
            incrementCounter = True
    argsMontage = argsMontage + globalWorkDir + "/Logo.png " + globalWorkDir + "/Logo.png "
    argsMontage = argsMontage + "-geometry " + "+" + str(MONTAGESPACING_W) + "+" + str(MONTAGESPACING_H)
    subprocess.call(binMontage + " " + argsMontage + " " + outFile, shell=True)
    print(binMontage + " " + argsMontage)
    # Display Processing On screen.
    string = "Processing, Please Wait."
    text = smallfont.render(string, 1, rgbRED)
    textpos = text.get_rect()
    textpos.centerx = background.get_rect().centerx
    textpos.centery = background.get_rect().centery
    SetBlankScreen()
    background.blit(text, textpos)
    UpdateDisplay()
    outFile = "/home/pi/vancouver-se-monkeys/discord_bot/cat.jpg"
    subprocess.call(binMontage + " " + argsMontage + " " + outFile, shell=True)
    return outFile
# End of function.

# Show preview of the montage.
def PreviewMontage(MontageFile):
    print("Show something.")
    preview = pygame.image.load(MontageFile)
    PILpreview = Image.open(MontageFile)
    previewSize = PILpreview.size # returns (width, height) tuple
    ScaleW = AspectRatioCalc(previewSize[0], previewSize[1], SCREEN_HEIGHT)
    preview = pygame.transform.scale(preview, (ScaleW, SCREEN_HEIGHT))
    SetBlankScreen()
    background.blit(preview, (SCREEN_WIDTH/2-ScaleW/2, 0))
    camera.stop_preview()
    UpdateDisplay()
    sleep(6)
    QuitGracefully()
    return
# End of function.

# Aspect Ratio Calculator
def AspectRatioCalc(OldH, OldW, NewW):
    #(original height / original width) x new width = new height
    return int((OldH/OldW)*NewW)
# End of function.
########## End of functions.

def DemoFlip():
    global RunDemo
    global RunDemoCounter
    if (time.time()-RunDemoCounter >= DEMOCYCLETIME):
        NextEffect()
        RunDemoCounter = time.time()
# End of function.

######### Main

# Setup Camera resolution for picture taking.
CAMRES_W = int((MONTAGE_W/2)-(MONTAGESPACING_W*2))
# Maintain the Aspect Ratio Math:
# (original height / original width) x new width = new height
CAMRES_H = AspectRatioCalc(1920, 2880, CAMRES_W)
RES_PREVIEW = (640, 480)
RES_PHOTO = (CAMRES_W, CAMRES_H)


SetEffect('none')
camera.resolution = RES_PREVIEW
camera.start_preview(alpha=PREVIEW_ALPHA)
sleep(2) # This seems to be recommended when starting the camera.

running = 1
RunDemoCounter = time.time()

while running:
    sleep(20)
    RunPhotoboothSession()

########## End of Main
