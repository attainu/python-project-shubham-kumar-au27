"""
This class is responsible for storing all the information about the current state of a chess game.
It will also be responsible for determining the valid moves at the current state.It will also keep the move log
"""



class GameState():
    def __init__(self):
        #this board is a 8*8 2D list, each element of the list has 2 characters.
        #The first character represents the color of the piece "b"or"w".
        #The second character represents the type of the piece, "K","Q","B","R","N",or "p".
        # "--" represents the empty space in the board.
        self.board = [
            ["bR","bN","bB","bQ","bK","bB","bN","bR"],
            ["bp","bp","bp","bp","bp","bp","bp","bp"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["wp","wp","wp","wp","wp","wp","wp","wp"],
            ["wR","wN","wB","wQ","wK","wB","wN","wR"],
        ]
        self.moveFunctions = {"p": self.getPawnMoves,"R":self.getRookMoves,"N":self.getKnightMoves,
        "B":self.getBishopMoves,"Q":self.getQueenMoves, "K": self.getKingMoves}
        self.whiteTomove = True
        self.movelog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = False
        self.staleMate = False
        self.enpassantPossible = () #co ordinates for the square where en passant capture is possible
       
    #takes a move as a parameter and execute it(This will not work for castling, pawn promition,and en-passant)
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.movelog.append(move) #log the move so we can undo it later
        self.whiteTomove = not self.whiteTomove #swapplayers
        #update king's location if moved
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)
        #pawnpromotion
        if move.isPawnPromotion:
             self.board[move.endRow][move.endCol] = move.pieceMoved[0] + "Q"

        #enpassant Move
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = "--" #capturing the pawn

        #update enpassantpossible variable
        if move.pieceMoved[1] == "p" and abs(move.startRow - move.endRow) == 2: #only on 2 square pawn advances
            self.enpassantPossible = ((move.startRow + move.endRow)//2,move.startCol)
        else:
            self.enpassantPossible = ()


    #Undo the last move made
    def undoMove(self):
        if len(self.movelog) != 0: #makesure there is a move to undo
            move = self.movelog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteTomove  = not self.whiteTomove #switch turns back
            #update the king's position if needed
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)
            #undo enpassant 
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = "--" #leave landing square blank
                self.board[move.startRow][move.endCol] == move.pieceCaptured
                self.enpassantPossible = (move.endRow, move.endCol)
            #undo 2square pawn advance
            if move.pieceMoved[1] == "p" and abs(move.startRow - move.endRow) == 2:
                self.enpassantPossible = ()
            

    #All moves considering checks
    def getValidMoves(self):
        tempEnpassandPossible = self.enpassantPossible
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.whiteTomove:
            KingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            KingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        if self.inCheck:
            if len(self.checks) == 1: #only one check, block check or move king
                moves = self.getAllPossibleMoves()
                #to block a check u must move a piece into one of the squares b/w the enemy piece and king
                check = self.checks[0] #check information
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol] #enemy piece causing the check
                validSquares = [] #squares that pieces can move to
                #if Knight, must capture knight or move King, other pieces can be blocked
                if pieceChecking[1] == "N":
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1,8):
                        validSquare = (KingRow + check[2]*i, kingCol + check[3] *i) #check[2] & check[3] are the check directions
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol: #once u get to piece and checks
                            break
                #get rid of any moves that don't block check or move King
                for i in range(len(moves) -1,-1,-1): #go through backwards when u are removing from a list as iterating
                    if moves[i].pieceMoved[1] != "K": #move doesn't move king so it must block or capture
                        if not (moves[i].endRow,moves[i].endCol) in validSquares: #move doesn't block check or capture piece
                            moves.remove(moves[i])
            else: #double check, king has to move
                self.getKingMoves(KingRow, kingCol, moves)

        else: #not in check so all moves are fine
            moves = self.getAllPossibleMoves()
        self.enpassantPossible = tempEnpassandPossible
        
        return moves
    #determine if the current player is in check
    def inCheck(self):
        if self.whiteTomove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    #determine if the enemy can attack the square r, c
    def squareUnderAttack(self,r,c):
        self.whiteTomove = not self.whiteTomove #switch to opponent's turn
        oppMoves = self.getAllPossibleMoves()
        self.whiteTomove = not self.whiteTomove #switch turns back
        for move in oppMoves:
            if move.endRow == r and move.endCol == c: #square is under attack
                return True
        return False 
    #All moves without considering checks
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)): #no. of rows
            for c in range(len(self.board[r])): #no. of columns in given row
                turn = self.board[r][c][0]
                if (turn == "w" and self.whiteTomove) or (turn == "b" and not self.whiteTomove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r,c, moves) #calls the appropriate move functions based on piece type
        return moves
   
         
    #this will get all the pawn moves for the pawn located at row, col and add these moves to the list
    def getPawnMoves(self,r,c,moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        if self.whiteTomove: #white pawn moves

            if self.board[r-1][c] == "--": #1 square pawn advance
                if not piecePinned or pinDirection == (-1,0):
                    moves.append(Move((r,c),(r-1,c),self.board))
                    if r == 6 and self.board[r-2][c] == "--": #2square pawn advance
                        moves.append(Move((r,c),(r-2,c), self.board))
        #captures
            if c-1 >= 0: #captures to the left
                if self.board[r-1][c-1][0] == "b":  #0 means it's checking whether the piece is enemy piece("b")
                    if not piecePinned or pinDirection == (-1,-1):
                        moves.append(Move((r,c),(r-1,c-1),self.board))
                elif (r-1, c-1) == self.enpassantPossible:
                    moves.append(Move((r,c),(r-1, c-1), self.board, isEnpassantMove= True))

            if c+1 <= 7: #captures to the right
                if self.board[r-1][c+1][0] == "b": #enemy piece to capture
                    if not piecePinned or pinDirection == (-1,1):
                        moves.append(Move((r, c),(r-1, c+1), self.board))
                elif (r-1, c+1) == self.enpassantPossible:
                    moves.append(Move((r,c), (r-1, c+1), self.board, isEnpassantMove = True))

        else: #blackpawnmoves
            if self.board[r+1][c] == "--": #1squaremove
                if not piecePinned or pinDirection == (1, 0):
                    moves.append(Move((r,c),(r+1,c), self.board))
                    if r == 1 and self.board[r+2][c] == "--" : #2 square move
                        moves.append(Move((r,c),(r+2,c), self.board))
            #captures
            if c-1 >=0: #capture to left
                if self.board[r+1][c-1][0] == "w":
                    if not piecePinned or pinDirection == (1, -1):
                        moves.append(Move((r,c),(r+1, c-1), self.board))
                elif (r+1, c-1) == self.enpassantPossible:
                    moves.append(Move((r,c), (r+1, c-1), self.board, isEnpassantMove = True))
            if c+1 <= 7: #capture to right
                if self.board[r+1][c+1][0] == "w":
                     if not piecePinned or pinDirection == (1, 1):
                        moves.append(Move((r,c),(r+1,c+1), self.board))
                elif (r+1, c+1) == self.enpassantPossible:
                      moves.append(Move((r,c),(r+1,c+1), self.board, isEnpassantMove = True))

        #add pawn promotions later

    #this will get all the rook moves for the rook located at row, col and add these moves to the list
    def getRookMoves(self,r,c,moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != "Q": #can't remove queen from pin on rook moves,only remove it on bishop moves
                    self.pins.remove(self.pins[i])
                break
        directions = ((-1,0),(0,-1),(1,0),(0,1))    #up,left,down,right
        enemyColor = "b" if self.whiteTomove else "w"
        for d in directions:
            for i in range(1,8):
                endRow = r + d[0]*i
                endCol = c + d[1] *i
                if 0 <= endRow < 8 and 0 <= endCol <8: #onboard
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--": #Empty space valid
                            moves.append(Move((r,c),(endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor: #enemyPiece valid
                            moves.append(Move((r,c),(endRow,endCol), self.board))
                            break
                        else: #friendlypiece invalid
                            break
                else: #off board
                    break
    ##this will get all the knight moves
    def getKnightMoves(self,r,c,moves):
        piecePinned = False
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break
        KnightMoves = ((-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1))
        enemyColor = "w" if self.whiteTomove else "b"
        for m in KnightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != enemyColor: # (empty or enemypiece)
                        moves.append(Move((r,c),(endRow,endCol), self.board))
    #this will get all the Bishop moves
    def getBishopMoves(self,r,c,moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        directions = ((-1,-1),(-1,1),(1,-1),(1,1)) #4 diaganols
        enemyColor = "b" if self.whiteTomove else "w"
        for d in directions:
            for i in range(1,8): #bishop can move max to 7 squares
                endRow = r + d[0]*i
                endCol = c + d[1]*i
                if 0 <= endRow < 8 and 0 <= endCol < 8: #check if it's still on the board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--": #empty space valid
                            moves.append(Move((r, c),(endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor: #enemy piece valid
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else: #friendly piece invalid
                            break
                else: #off board
                    break

                   
    #this will get all the Queen moves
    def getQueenMoves(self,r,c,moves):
        self.getRookMoves(r,c,moves)
        self.getBishopMoves(r,c,moves)

    ##this will get all the king
    def getKingMoves(self,r,c,moves):
        rowMoves = (-1,-1,-1,0,0,1,1,1)
        colMoves = (-1,0,1,-1,1,-1,0,1)
        enemyColor = "w" if self.whiteTomove else "b"
        for i in range(8):
            endRow = r+ rowMoves[i]
            endCol = c + colMoves[i]
            if 0 <= endRow < 8 and 0 <= endCol <8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != enemyColor: #empty or enemy piece
                    #place king on end square and check for checks
                    if enemyColor == "w":
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((r,c),(endRow, endCol), self.board))
                    #place king back on original location
                    if enemyColor == "w":
                        self.whiteKingLocation = (r, c)
                    else:
                        self.blackKingLocation = (r, c)

    #returns if the player is in check, a list of pins, and a list of checks
    def checkForPinsAndChecks(self):
        pins = [] #squares where the allied pinned piece is and direction pinned from
        checks = []  #squares where enemy is applying a check
        inCheck = False
        if self.whiteTomove:
            enemyColor = "b"
            allyColor = "w"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = "w"
            allyColor = "b"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        #check outward from king for pins and checks, keep track of pins
        directions = ((-1,0),(0,-1),(1,0),(0,1),(-1,-1),(-1,1),(1,-1),(1,1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = () #reset possible pins
            for i in range(1, 8):
                endRow = startRow + d[0]*i
                endCol = startCol + d[1]*i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != "K":
                        if possiblePin == (): #1st allied piece could be pinned
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else: #2nd allied piece, so no pin or check possible in this direction
                            break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        #5possibilities here in this complex condition
                        #1 Orthogonally away from  king and piece is a rook
                        #2 diagonally away from king and piece is a bishop
                        #3 1 square away diagonally away from king and piece is a pawn
                        #4 Any direction and piece is a queen
                        #5 Any direction 1 square away and piece is a king(This is necessary to prevent a king move to a 
                        # square controlled by another king)
                        if (0 <= j <= 3 and type == "R") or \
                            (4 <= j <= 7 and type == "B") or \
                            (i == 1 and type == "p" and ((enemyColor == "w"and 6 <= j <=7)or (enemyColor == "b"and 4 <=j<=5))) or \
                            (type == "Q") or (i == 1 and type == "K"):
                            if possiblePin == (): #no piece blocking, so check
                                inCheck = True
                                checks.append((endRow,endCol, d[0], d[1]))
                                break
                            else: #piece blocking so pin
                                pins.append(possiblePin)
                                break
                        else: #enemy piece not applying check
                            break
                else: #off board
                    break
        #check for knight moves
        Knightmoves = ((-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1))
        for m in Knightmoves:
            endRow = startRow = m[0]
            endCol = startCol = m[1]
            if 0 <= endRow <8 and 0 <= endCol <8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == "N": #enemy knight attacking king
                    inCheck = True
                    checks.append((endRow, endCol, m[0],m[1]))
        return inCheck, pins, checks



       

                  
class Move():
    #maps keys to values
    #key : value
    ranksToRows = {"1":7, "2":6, "3":5, "4":4,
                    "5": 3, "6": 2,"7":1,"8":0}
    rowsToRanks = {v: k for k, v in ranksToRows.items() }
    filesToCols = {"a":0, "b":1, "c":2, "d":3,
                    "e":4, "f":5,"g":6, "h":7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove = False):

        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        #pawnpromotions
        self.isPawnPromotion = False
        if (self.pieceMoved == "wp" and self.endRow == 0) or (self.pieceMoved == "bp" and self.endRow == 7):
            self.isPawnPromotion = True
        #en passant
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = "wp" if self.pieceMoved == "bp" else "bp"



        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        print(self.moveID)

    #over riding the equals method
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False
    def getChessNotation(self):
        #you can add to make this like real chess notation
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)
        
    def getRankFile(self,r,c):
        return self.colsToFiles[c] + self.rowsToRanks[r]










