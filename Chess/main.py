import pygame as p
from utilities import chessengine
WIDTH = HEIGHT = 512
DIMENSION = 8 
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15 #For animation
IMAGES = {}

"""
Initialize a global dict of images.This will be called exactly once in the main
"""
def load_Images():
    pieces = ["bB","bK","bQ","bR","bN","bp","wB","wK","wQ","wR","wN","wp"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"),(SQ_SIZE,SQ_SIZE))
#Note we can access image by saying IMAGES["wp"]


#The main driver of our code This will handle user input and update the graphics
def main():
    p.init()
    screen = p.display.set_mode((WIDTH,HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = chessengine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False #flagvariable for when a move is made
    animate = False #flag variable for when we should animate a move
    load_Images() #will only do this once, before the while loop
    running = True
    sqSelected = () #no square selected,keep track of the last click of the user (tuple: row,cloumn)
    playerclicks = [] #keep track of player clicks (two tuples[(6,4),(4,4)])
    gameOver = False
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            #mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos() #(x,y) location of mouse
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    
                    if sqSelected == (row,col):  #the user clicked the same square twice
                        sqSelected = () #deselect
                        playerclicks = [] #clear player clicks

                    else:
                        sqSelected = (row,col)
                        playerclicks.append(sqSelected) #append for both 1st and 2nd clicks
                    if len(playerclicks) == 2:  #means it is after the 2nd click
                        move = chessengine.Move(playerclicks[0], playerclicks[1], gs.board)
                        print(move.getChessNotation())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = () #reset user clicks
                                playerclicks = []
                        if not moveMade:
                            playerclicks = [sqSelected]

                    
            #key handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: #undo when "z" is pressed 
                    gs.undoMove()
                    moveMade = True
                    animate = False
                if e.key == p.K_r: #reset the board when r is pressed
                    gs = chessengine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerclicks = []
                    moveMade = False
                    animate = False
        if moveMade:
            if animate:
                animateMove(gs.movelog[-1],screen,gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False

        if gs.checkMate:
            gameOver = True
            if gs.whiteTomove:
                drawText(screen,"Black wins by CheckMate")
            else:
                drawText(screen, "White wins by CheckMate")
        
        elif gs.staleMate:
            gameOver = True
            drawText(screen, "StaleMate")


        draw_gamestate(screen,gs, validMoves, sqSelected)
        clock.tick(MAX_FPS)
        p.display.flip()

#this will highlight the square selected and moves for the piece selected
def highlightsquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r,c = sqSelected
        if gs.board[r][c][0] == ("w" if gs.whiteTomove else "b"): #sqSelected is a piece that can be moved
            #highlight selected square 
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100) #transparency value -> 0 transparent; 255 opaque
            s.fill(p.Color("blue"))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            #highlight moves from that square
            s.fill(p.Color("yellow"))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))
"""
Responsible for all the graphics within the current gamestate
"""
def draw_gamestate(screen,gs,validMoves,sqSelected):
    drawboard(screen) #will draw squares on the board
    highlightsquares(screen, gs, validMoves, sqSelected)
    drawpieces(screen,gs.board) #will draw pieces on top of those squares


def drawboard(screen):#will draw the squares on the board
    global colors
    colors = [p.Color("white"),p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c)%2)]
            p.draw.rect(screen,color,p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))

def drawpieces(screen,board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board [r][c]
            if piece != "--":
                screen.blit(IMAGES[piece],p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))

def animateMove(move, screen, board, clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 10 #frames to move one square
    frameCount = (abs(dR)+ abs(dC)) * framesPerSquare
    for frame in range(frameCount+1):
        r,c = ((move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount))
        drawboard(screen)
        drawpieces(screen, board)

        #erase the piece moved from the ending square
        color = colors[(move.endRow + move.endCol)% 2]
        endSquare = p.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE,SQ_SIZE,SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        #draw captured piece onto rectangle
        if move.pieceCaptured != "--":
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        #draw moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c*SQ_SIZE, r*SQ_SIZE,SQ_SIZE,SQ_SIZE))
        p.display.flip()
        clock.tick(60)

def drawText(screen, text):
    font = p.font.SysFont("Helvitca",32,True, False)
    textObject = font.render(text, 0, p.Color("Black"))
    textLocation = p.Rect(0,0,WIDTH,HEIGHT).move(WIDTH/2 - textObject.get_width()/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color("Gray"))
    screen.blit(textObject, textLocation.move(2,2))
  

    

if __name__=="__main__":
    main()






