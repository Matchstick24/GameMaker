import pygame
import json

pygame.init()

# Saving And Loading

Save_Load = input("Load? : ")
Save_LoadName = ""

while not (Save_Load != "False") or (Save_Load != "True"):
    
    if Save_Load == "False": break
    Save_Load = input("Load? : ")

if Save_Load == "True":
    Save_LoadName = input("Name Of The Load : ")

Save_OnLeave = input("Save? : ")
Save_Name = ""

while not (Save_OnLeave != "False") or (Save_OnLeave != "True"):

    if Save_OnLeave == "False": break
    Save_OnLeave = input("Save? : ")

if Save_OnLeave == "True":
    Save_Name = input("Name Of The Save : ")

ScreenWidth, ScreenHeight = 1280, 720
Screen = pygame.display.set_mode((ScreenWidth, ScreenHeight))
Clock = pygame.time.Clock()
Running = True

# Settings

Fps = 30
Font = pygame.font.Font(None, 40) 
Background = (255, 255, 255)

# Settings Threw Game(Changable in Game)

CellSize = 30
Cols = 60
Rows = 60
ScrollY = 0
ScollAmount = 30
CameraX, CameraY = 0, 0
CameraSpeed = 6
Camera_LastPosX, Camera_LastPosY = 0, 0

Grid = {}
Grid_Rects = {}
Grid_Generating = True
Mouse_Down = False
MouseRight_Down = False
Current_CellValue = False

# Imports

import CellValues as Values
CellValues = Values.Values

# Images

# Images - Selection

Selection_Spacing = 100
Selection_TextColour = (255, 0, 0)
Selection_CellSize = 30
Selection_XSpacing = 240
Selection_Rects = {}
Selection_Generating = True

Selection_OpenSize, Selection_OpenPos = (50, 50), (15, 300)
Selection_Open = pygame.transform.scale(pygame.image.load("Images/Selection_Open.bmp").convert_alpha(), Selection_OpenSize)
Selection_OpenRect = Selection_Open.get_rect(topleft = Selection_OpenPos)

Selection_CloseSize, Selection_ClosePos = (50, 50), (310, 300)
Selection_Close = pygame.transform.scale(pygame.image.load("Images/Selection_Close.bmp").convert_alpha(), Selection_CloseSize)
Selection_CloseRect = Selection_Close.get_rect(topleft = Selection_ClosePos)

Selection_IsOpen = False
Selection_BackgroundSize, Selection_BackgroundPos = (300, 600), (0, 50)
Selection_Background = pygame.transform.scale(pygame.image.load("Images/Selection_Background.bmp").convert_alpha(), Selection_BackgroundSize)

# Functions

def DrawText(Text, x, y, Colour):

    Surface = Font.render(Text, True, Colour)
    Screen.blit(Surface, (x, y))

def SetUp_Grid(Grid):

    if Save_Load == "True":

        LoadGrid = False

        with open(Save_LoadName, "r") as File:
            LoadGrid = json.load(File)

        for x in range(0, Cols):

            Grid[x] = {}

            for y in range(0, Rows):

                Grid[x][y] = LoadGrid[str(x)][str(y)]

    else:
    
        for x in range(0, Cols):

            Grid[x] = {}

            for y in range(0, Rows):

                Grid[x][y] = 0

def Render_Grid(Grid):

    global Grid_Generating, Grid_Rects

    Current_i = 1

    for x in range(0, Cols):
        for y in range(0, Rows):

            Cell = Grid[x][y]
            ScreenX, ScreenY = int((x * CellSize) + (CameraX * CameraSpeed)), int((y * CellSize) + (CameraY * CameraSpeed))

            if Grid_Generating:
                
                Grid_Rects[Current_i] = {

                    "Rect" : pygame.rect.Rect(ScreenX, ScreenY, CellSize, CellSize),
                    "x" : x,
                    "y" : y,

                }
            
            elif (Camera_LastPosX == CameraX) and (Camera_LastPosY == CameraY):

                Grid_Rects[Current_i]["Rect"] = pygame.rect.Rect(ScreenX, ScreenY, CellSize, CellSize)

            Current_i += 1

            if Cell == 0: continue # Air Or Nothing

            if (ScreenX > ScreenWidth + CellSize or ScreenX < -CellSize) or (ScreenY > ScreenHeight + CellSize or ScreenY < -CellSize):
                continue

            CellTable = CellValues[Cell]   
            Image = pygame.transform.scale(pygame.image.load(CellTable["Image"]).convert_alpha(), (CellSize, CellSize))

            Screen.blit(Image, (ScreenX, ScreenY))

    Grid_Generating = False

def Render_Selection():

    Mouse_Pos = pygame.mouse.get_pos()
    global Selection_IsOpen, Selection_Generating, Selection_Rects

    if Selection_IsOpen:

        Screen.blit(Selection_Background, Selection_BackgroundPos)
        Screen.blit(Selection_Close, Selection_CloseRect)

        if Mouse_Down and Selection_CloseRect.collidepoint(Mouse_Pos) and Mouse_Pos != (0, 0):
            Selection_IsOpen = False

    else: 

        Screen.blit(Selection_Open, Selection_OpenRect)

        if Mouse_Down and Selection_OpenRect.collidepoint(Mouse_Pos) and Mouse_Pos != (0, 0):
            Selection_IsOpen = True

    if Selection_IsOpen:

        for Index in range(1, len(CellValues) + 1):

            if Selection_Generating:

                Selection_Rects[Index] = {

                    "Rect" : pygame.rect.Rect(15, (Index * Selection_Spacing) + ScrollY, Selection_XSpacing, Selection_Spacing),
                    "Index" : Index,

                }

            if (Index * Selection_Spacing) + ScrollY > Selection_BackgroundSize[1]: continue
            if (Index * Selection_Spacing) + ScrollY < Selection_BackgroundPos[1]: continue

            if not Selection_Generating: Selection_Rects[Index]["Rect"] = pygame.rect.Rect(15, (Index * Selection_Spacing) + ScrollY, Selection_XSpacing, Selection_Spacing)

            if Current_CellValue != False and Current_CellValue["Name"] == CellValues[Index]["Name"]: DrawText(CellValues[Index]["Name"], 15, (Index * Selection_Spacing) + ScrollY, (0, 255, 0))
            else: DrawText(CellValues[Index]["Name"], 15, (Index * Selection_Spacing) + ScrollY, Selection_TextColour)

            Image = pygame.transform.scale(pygame.image.load(CellValues[Index]["Image"]).convert_alpha(), (Selection_CellSize, Selection_CellSize))
            Screen.blit(Image, (Selection_XSpacing, (Index * Selection_Spacing) + ScrollY))

        Selection_Generating = False

def Render():

    Screen.fill(Background)
    Render_Grid(Grid)
    Render_Selection()
    pygame.display.flip()

def ManageInput_Selection():

    if not Selection_IsOpen:

        ManageInput_Grid()
        return

    Mouse_Pos = pygame.mouse.get_pos()

    global Current_CellValue

    for Index in range(1, len(Selection_Rects) + 1):

        Table = Selection_Rects[Index]

        if Mouse_Down and Table["Rect"].collidepoint(Mouse_Pos) and Mouse_Pos != (0, 0):

            Current_CellValue = CellValues[Table["Index"]]
            return

def ManageInput_Grid():

    Mouse_Pos = pygame.mouse.get_pos()

    if not Current_CellValue: return
    if (Selection_IsOpen and Mouse_Down and Selection_CloseRect.collidepoint(Mouse_Pos) and Mouse_Pos != (0, 0)) or ((Mouse_Down and Selection_OpenRect.collidepoint(Mouse_Pos) and Mouse_Pos != (0, 0))): return

    global Grid

    for Index in range(1, len(Grid_Rects) + 1):

        Table = Grid_Rects[Index]

        if Mouse_Down and Table["Rect"].collidepoint(Mouse_Pos) and Mouse_Pos != (0, 0):

            Grid[Table["x"]][Table["y"]] = Current_CellValue["Index"]
            break
    
        elif MouseRight_Down and Table["Rect"].collidepoint(Mouse_Pos) and Mouse_Pos != (0, 0):

            Grid[Table["x"]][Table["y"]] = 0
            break

def ManageInput():

    Keys = pygame.key.get_pressed()

    # Selection

    global Running, ScrollY, Mouse_Down, MouseRight_Down, CameraX, CameraY, Camera_LastPosX, Camera_LastPosY
    Camera_LastPosX, Camera_LastPosY = CameraX, CameraY

    for Event in pygame.event.get():#

        if Event.type == pygame.QUIT:
            Running = False

        elif Event.type == pygame.MOUSEBUTTONDOWN:

            if Event.button == 1:
                Mouse_Down = True
            elif Event.button == 3:
                MouseRight_Down = True

            if Selection_IsOpen:

                if Event.button == 4:
                    ScrollY += ScollAmount
                elif Event.button == 5:
                    ScrollY -= ScollAmount
        
        elif Event.type == pygame.MOUSEBUTTONUP:

            if Event.button == 1:
                Mouse_Down = False
            elif Event.button == 3:
                MouseRight_Down = False

    if ScrollY < -((Selection_Spacing * (len(CellValues) - 6)) + Selection_Spacing): ScrollY = -((Selection_Spacing * (len(CellValues) - 6)) + Selection_Spacing)
    elif ScrollY > Selection_Spacing * len(CellValues): ScrollY = Selection_Spacing * len(CellValues)

    # Other

    if Keys[pygame.K_w]:
        CameraY += 1
    if Keys[pygame.K_s]:
        CameraY -= 1
    if Keys[pygame.K_a]:
        CameraX += 1
    if Keys[pygame.K_d]:
        CameraX -= 1

    ManageInput_Selection()

def Save():
    
    if not Save_OnLeave: return

    with open(Save_Name, "w") as File:

        json.dump(Grid, File)

# Main

SetUp_Grid(Grid)

while Running:

    ManageInput()
    Render()

    Clock.tick(Fps)

Save()
pygame.quit()