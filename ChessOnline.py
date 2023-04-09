import os
import pygame as p
import ChessEngine
import ChessAI
import time
import sys
import socket
import threading

HOST = '127.0.0.1'
SERVER_PORT = 65432
FORMAT = 'utf8'



EASY_MODE = "1"
MEDIUM_MODE = "2"
HARD_MODE = "3"

SCREEN_MODE = "MAN"
TERMINAL_MODE = "AUTO"

OUR_AI_WHITE = "WHITE_AGENT_OPPONENT_BLACK"
OUR_AI_BLACK = "BLACK_AGENT_OPPONENT_WHITE"
HUMAN_WHITE_AI_BLACK = "WHITE_HUMAN_BLACK_AI"

TIME = 48
BORDER = 32
BOARD = 640
MENU = 100
MOVE_LOG = 350
WIDTH = MENU + BOARD + BORDER * 2 + MOVE_LOG
HEIGHT = BOARD + TIME * 2 + BORDER * 2
DIMENSION = 8
SQ_SIZE = (HEIGHT - 2 * BORDER - 2 * TIME) // DIMENSION
MAX_FPS = 15
IMAGES = {}

COLORGAME = False

AILEVEL = True

FISRTMOVE = True

PAUSE = False



def connect_server( username ):
    global client, turned, start_threading, screen
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('CLIENT SIDE')
    client.connect((HOST, SERVER_PORT))
    print('client address:', client.getsockname())
    msg = f"USERNAME {username}"
    client.sendall(msg.encode(FORMAT))

    msg = client.recv(1024).decode(FORMAT)
    if msg == 'WHITE':
        print('Your chess: WHITE')
        turned = True
        start_threading = False
    else:
        print('Your chess: BLACK')
        turned = False
        start_threading = True

def recv_mess():
    global turned, client, ok, gameState, moveMade, opponent
    
    try:
        msg = client.recv(1024).decode(FORMAT)
    except:
        return
   
    msg = msg.split(' ')

    if (msg[0] == 'MOVE'):
        turned = True
        move = ChessEngine.Move((int(msg[1]), int(msg[2])), (int(msg[3]), int(msg[4])), gameState.board)
        gameState.makeMove(move)
        moveMade = True
    
    if (msg[0] == 'OPPONENT'):
        print("opponent", msg[1])
        opponent = msg[1]


    if msg[0] == 'EXIT2':
        print('LOSE')
        ok = False
        client.sendall("EXIT".encode(FORMAT))

def main(mode=MEDIUM_MODE):
    global client, turned, start_threading, opponent 
    opponent = None

    p.init()
    global screen
    screen = p.display.set_mode((WIDTH, HEIGHT))
    p.display.set_caption("Auto Chess", "None")
    isPlaying = False  # Start a game
    playerOne = True
    playerTwo = True
    global COLORGAME
    global FISRTMOVE
    mode = mode
    
    # In Menu:
    playerOne = True
    playerTwo = True
    isPlaying = True
    menuGame = False

    loadImages()  # Load images of pieces, board
    clock = p.time.Clock()
    global gameState
    gameState = ChessEngine.GameState()

    validMoves = gameState.getValidMoves()  # Get all the valid move
    global moveMade # Moving a piece
    moveMade = False
    gameOver = False
    sqSelected = ()  # Square player selected (tuple)
    playerClicks = []  # keep track of player clicks (2 tuples: [(6, 4), (4, 4)]
    p1Time = p2Time = 1800
    motlan = True
    global PAUSE

    loginGame = True
    font = p.font.Font(None, 32)
    input_box = p.Rect(520, 540, 250, 40)
    color_inactive = p.Color('lightskyblue3')
    color_active = p.Color('dodgerblue2')
    color = color_inactive
    text = ''
    active = False

    while loginGame:
        background = p.transform.scale(p.image.load("chessv2/menuusername.png"), (WIDTH, HEIGHT))
        screen.blit(background, (0, 0))
        for event in p.event.get():
            if event.type == p.QUIT:
                p.quit()
                quit()
            
            if event.type == p.MOUSEBUTTONDOWN:
                # kiểm tra xem con trỏ chuột có nằm trong hộp văn bản không
                location = p.mouse.get_pos()
                print(location)
                if input_box.collidepoint(event.pos):
                    active = not active
                elif 500 <= location[0] <= 650 and 615 <= location[1] <= 675:
                    loginGame = False
                    print(text)
                else:
                    active = False
                color = color_active if active else color_inactive
            
            if event.type == p.KEYDOWN:
                if active:
                    if event.key == p.K_RETURN:
                        # lấy giá trị từ hộp văn bản khi người dùng nhấn Enter
                        loginGame = False
                        print(text)
                    elif event.key == p.K_BACKSPACE:
                        # xóa ký tự cuối cùng khi người dùng nhấn phím Backspace
                        text = text[:-1]
                    else:
                        # thêm ký tự mới vào hộp văn bản
                        text += event.unicode
        # vẽ màn hình
        # screen.fill((255, 255, 255))
        # vẽ hộp văn bản
        p.draw.rect(screen, color, input_box, 2)
        # vẽ nội dung trong hộp văn bản
        txt_surface = font.render(text, True, (255, 255, 255))
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        p.display.update()
    
    nameOnTop = True
    connect_server(text)

    threadingOponent = False    
    
    while opponent == None:
        if threadingOponent == False:
            start_threading = True
            thr = threading.Thread(target=recv_mess)
            thr.start()

        screen.fill((100, 100, 100))
        font = p.font.Font(None, 60)
        screen.blit(font.render("Waiting for an opponent...", True, (255, 255, 255)), (350, 350))
        p.display.update()

    font = p.font.Font(None, 40)
    txt_surface = font.render(text, True, (255, 255, 255))
    txt_op_surface = font.render(opponent, True, (255, 255, 255))

    if (turned and gameState.whiteToMove) or (not turned and not gameState.whiteToMove):
        nameOnTop = False

    while isPlaying:
        time.sleep(0.2)
        start_time = time.time()
        background = p.transform.scale(p.image.load("chessv2/menu.png"), (WIDTH, HEIGHT))
        screen.blit(background, (0, 0))
        # If player 1 turn and white turn or player 2 turn and black turn
        humanTurn = (gameState.whiteToMove and playerOne) or (not gameState.whiteToMove and playerTwo)
     
        
        for e in p.event.get():
            if e.type == p.QUIT:
                isPlaying = False
            
            if turned == True:
                if e.type == p.MOUSEBUTTONDOWN:
                    # LEFT CLICK
                    if e.button == 1:
                        location = p.mouse.get_pos()  # (x, y) location of mouse
                        print(location)
                        {
                        # print(location)
                        # Sidebar
                        # if 25 <= location[0] < 75:
                        #     # Menu
                        #     if 63 <= location[1] < 113:
                        #         # isPlaying = False
                        #         PAUSE = True
                        #     # Start a new 1 player game
                        #     if 150 <= location[1] < 200:
                        #         gameState = ChessEngine.GameState()

                        #         # global COLORGAME
                        #         COLORGAME = not COLORGAME
                        #         loadImages()

                        #         validMoves = gameState.getValidMoves()  # Get all the valid move
                        #         moveMade = False  # Moving a piece
                        #         gameOver = False
                        #         playerOne = True
                        #         playerTwo = False
                        #         # playerAI = False
                        #         p1Time = p2Time = 1800
                        #         humanTurn = (gameState.whiteToMove and playerOne) or (
                        #                 not gameState.whiteToMove and playerTwo)
                        #         drawGameState(screen, gameState, gameState.getValidMoves(), sqSelected)
                                
                                
                                
                                
                                
                        #     # Start a new 2 player game
                        #     if 230 <= location[1] < 280:
                        #         gameState = ChessEngine.GameState()

                        #         # global COLORGAME
                        #         COLORGAME = not COLORGAME
                        #         loadImages()

                        #         validMoves = gameState.getValidMoves()  # Get all the valid move
                        #         moveMade = False  # Moving a piece
                        #         gameOver = False
                        #         playerOne = True
                        #         playerTwo = True
                        #         # playerAI = False
                        #         p1Time = p2Time = 1800
                        #         humanTurn = (gameState.whiteToMove and playerOne) or (
                        #                 not gameState.whiteToMove and playerTwo)
                        #         drawGameState(screen, gameState, gameState.getValidMoves(), sqSelected)
                                
                        #     # Start a new none player game
                        #     if 330 <= location[1] < 380:
                        #         gameState = ChessEngine.GameState()

                        #         # gameState.whiteToMove = bool(random.getrandbits(1))
                        #         # global COLORGAME
                        #         COLORGAME = not COLORGAME
                        #         FISRTMOVE = not FISRTMOVE
                        #         # Our Agent:  True  --> Go first, False --> Go Second

                        #         # if player_option == OUR_AI_WHITE:
                        #         #     FIRSTMOVE = True
                        #         # elif player_option == OUR_AI_BLACK:
                        #         #     FIRSTMOVE = False

                        #         gameState.whiteToMove = FISRTMOVE
                        #         loadImages()

                        #         validMoves = gameState.getValidMoves()  # Get all the valid move
                        #         moveMade = False  # Moving a piece
                        #         gameOver = False
                        #         playerOne = False
                        #         playerTwo = False
                        #         # playerAI = True
                        #         p1Time = p2Time = 1800
                        #         drawGameState(screen, gameState, gameState.getValidMoves(), sqSelected)
                        #     # Undo
                        #     if 417 <= location[1] < 471 and not gameOver:
                        #         # If is a PvP
                        #         if playerOne and playerTwo:
                        #             gameState.undoMove()
                        #         # Else, undo both white and black
                        #         else:
                        #             gameState.undoMove()
                        #             gameState.undoMove()
                        #         moveMade = True
                        #         gameOver = False
                        #     # New Game
                        #     if 516 <= location[1] < 569:
                        #         gameState = ChessEngine.GameState()
                        #         validMoves = gameState.getValidMoves()  # Get all the valid move
                        #         moveMade = False  # Moving a piece
                        #         gameOver = False
                        #         p1Time = p2Time = 1800
                        #         drawGameState(screen, gameState, gameState.getValidMoves(), sqSelected)

                        }
                        # Mouse in board and it's human turn
                        if MENU + BORDER <= location[0] < MENU + BORDER + BOARD \
                                and 80 <= location[1] < 720 \
                                and not gameOver and humanTurn:
                            col = (location[0] - BORDER - MENU) // SQ_SIZE
                            row = (location[1] - BORDER - TIME) // SQ_SIZE
                            # Deselect square if click 2 time on a same square
                            if sqSelected == (row,col):
                                sqSelected = ()
                                playerClicks = []
                            else:
                                sqSelected = (row,col)
                                playerClicks.append(sqSelected)
                            if len(playerClicks) == 2:
                                move = ChessEngine.Move(playerClicks[0], playerClicks[1], gameState.board)
                                curMove = playerClicks
                                for i in range(len(validMoves)):
                                    # If move is a valid move, make the move
                                    if move == validMoves[i]:
                                        # print(str(move.pieceMoved)+str((move.startRow, move.startCol))+str((move.endRow, move.endCol
                                        gameState.makeMove(validMoves[i])
                                        moveMade = True
                                        # reset the sqSel, playerClicks
                                        msg = f"MOVE {curMove[0][0]} {curMove[0][1]} {curMove[1][0]} {curMove[1][1]}"
                                        start_time = time.time()
                                        client.sendall(msg.encode(FORMAT))
                                        sqSelected = ()
                                        playerClicks = []
                                        start_threading = True
                                        turned = False

                                    # move not in valid moves
                                    if not moveMade:
                                        playerClicks = [sqSelected]
        
        if turned == False and start_threading == True:
            start_threading = False
            thr = threading.Thread(target=recv_mess)
            thr.start()

        if moveMade:
            validMoves = gameState.getValidMoves()
            moveMade = False

        drawGameState(screen, gameState, gameState.getValidMoves(), sqSelected)

        if not gameState.promotionDone:
            if motlan:
                gameState.whiteToMove = not gameState.whiteToMove
                motlan = False
            board = p.transform.scale(p.image.load("chessv2/pawnPromotion.png"), (WIDTH, HEIGHT))
            screen.blit(board, (0, 0))
            for e in p.event.get():
                if e.type == p.MOUSEBUTTONDOWN:
                    location = p.mouse.get_pos()
                    x = location[0]
                    y = location[1]
                    
                    if 310 <= y < 396:
                        if 217 <= x < 298:
                            gameState.pawnPromotion('B')
                            motlan = True
                        if 350 <= x < 427:
                            gameState.pawnPromotion('N')
                            motlan = True
                        if 488 <= x < 583:
                            gameState.pawnPromotion('Q')
                            motlan = True
                        if 631 <= x < 707:
                            gameState.pawnPromotion('R')
                            motlan = True

        if gameState.checkmate:
            gameOver = True
            gameOverText(screen, gameState.whiteToMove)
            # if gameState.color == 1:
            #     gameOverText(screen, gameState.whiteToMove)
            # else:
            #     gameOverText(screen, ~gameState.whiteToMove)
        elif gameState.stalemate:
            gameOver = True
            gameOverText(screen, gameState.whiteToMove)
            # if gameState.color == 1:
            #     gameOverText(screen, gameState.whiteToMove)
            # else:
            #     gameOverText(screen, ~gameState.whiteToMove)
        if gameState.whiteToMove:
            p1Time -= time.time() - start_time if p1Time > 0 else 0
        else:
            p2Time -= time.time() - start_time if p2Time > 0 else 0
        # remain_time = TIME_LIMIT - int(time.time() - start_time)
        gameOver = drawTime(screen, int(p1Time), int(p2Time), gameState.whiteToMove, gameOver)
        clock.tick(MAX_FPS)

        if nameOnTop:
            screen.blit(txt_surface, (670, 20))
            screen.blit(txt_op_surface, (670, 765))
        else:
            screen.blit(txt_op_surface, (670, 20))
            screen.blit(txt_surface, (670, 765))

        p.display.flip()


'''
Initialize a global dictionary of images. This will be called exactly once in the main
'''

def loadImages():
    pieces = ['bR', 'bN', 'bB', 'bQ', 'bK', 'bp', 'wB', 'wN', 'wR', 'wQ', 'wK', 'wp']
    blocks = ['blackBlock', 'whiteBlock', 'blackBlock1', 'whiteBlock1', 'highlightBlock']
    for piece in pieces:
        # IMAGES[piece] = p.transform.scale(p.image.load("chessOri/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))

        if COLORGAME:
            IMAGES[piece] = p.transform.scale(p.image.load("chessOri2/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
        else:
            # IMAGES[piece] = p.transform.scale(p.image.load("chessOri/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
            IMAGES[piece] = p.transform.scale(p.image.load("chessOri/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))

        # IMAGES[piece + "l"] = p.transform.scale(p.image.load("images/" + piece + "l.png"), (SQ_SIZE, SQ_SIZE))
    for block in blocks:
        image_path = os.path.join(os.curdir, "images", block + ".png")
        IMAGES[block] = p.transform.scale(p.image.load("images/" + block + ".png"), (SQ_SIZE, SQ_SIZE))

def drawMenuState(screen):
    # Cai menu 1 nay moi la menu :v
    board = p.transform.scale(p.image.load("chessv2/menu1.png"), (WIDTH, HEIGHT))
    screen.blit(board, (0, 0))

def drawGameState(screen, gameState, validMoves, sqSelected):
    # Board
    drawBroad(screen)
    # Background piece selected
    highlightPiece(screen, gameState, sqSelected)
    # Pieces
    drawPieces(screen, gameState.board)
    # Possible moves
    highlightMoves(screen, gameState, validMoves, sqSelected)
    # Move log
    drawMoveLog(screen, gameState)

def drawBroad(screen):
    board = p.transform.scale(p.image.load("chessv2/board2big.png"), (BOARD + BORDER * 2, BOARD + BORDER * 2))
    screen.blit(board, (MENU, TIME))

def highlightPiece(screen, gameState, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if r >= 0 and c >= 0:
            if gameState.board[r][c][0] == ('w' if gameState.whiteToMove else 'b'):
                s = p.Surface((SQ_SIZE, SQ_SIZE))
                s.set_alpha(100)
                s.fill(p.Color('#004CFF'))
                screen.blit(s, (c * SQ_SIZE + BORDER + MENU, r * SQ_SIZE + BORDER + TIME))

def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != '--':  # Not empty
                screen.blit(IMAGES[piece],
                            p.Rect(c * SQ_SIZE + BORDER + MENU, r * SQ_SIZE + BORDER + TIME, SQ_SIZE, SQ_SIZE))

def highlightMoves(screen, gameState, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if r >= 0 and c >= 0:
            if gameState.board[r][c][0] == ('w' if gameState.whiteToMove else 'b'):
                for move in validMoves:
                    if move.startRow == r and move.startCol == c:
                        p.draw.circle(screen, p.Color('#004CFF'), (
                            (move.endCol + 0.5) * SQ_SIZE + BORDER + MENU,
                            (move.endRow + 0.5) * SQ_SIZE + BORDER + TIME), 12)

def drawTime(screen, p1time, p2time, whiteToMove, gameOver):
    if not gameOver:
        m1, s1 = divmod(p1time, 60)
        h1, m1 = divmod(m1, 60)
        timeLeftP1 = str(h1).zfill(2) + ":" + str(m1).zfill(2) + ":" + str(s1).zfill(2)
        m2, s2 = divmod(p2time, 60)
        h2, m2 = divmod(m2, 60)
        timeLeftP2 = str(h2).zfill(2) + ":" + str(m2).zfill(2) + ":" + str(s2).zfill(2)

        # Background color
        White = p.Color('#D9D2D2')
        Black = p.Color('#121212')

        if p1time == 0 or p2time == 0:
            gameOver = True
            gameOverText(screen, whiteToMove)

        GAME_FONT = p.font.Font('./Font/Digital Dismay.otf', 50)

        # player 1 text color = black, player 2 = white
        if whiteToMove:
            textPlayer1 = GAME_FONT.render(timeLeftP1, 0, Black)
            textPlayer2 = GAME_FONT.render(timeLeftP2, 0, White)
            surfacePlayer1 = p.Surface((textPlayer1.get_width() + 20, TIME))
            surfacePlayer1.fill(White)
            surfacePlayer2 = p.Surface((textPlayer2.get_width() + 20, TIME))
            surfacePlayer2.fill(Black)
        else:
            textPlayer2 = GAME_FONT.render(timeLeftP2, 0, Black)
            textPlayer1 = GAME_FONT.render(timeLeftP1, 0, White)
            surfacePlayer2 = p.Surface((textPlayer2.get_width() + 20, TIME))
            surfacePlayer2.fill(White)
            surfacePlayer1 = p.Surface((textPlayer1.get_width() + 20, TIME))
            surfacePlayer1.fill(Black)

        textPlayer1Location = p.Rect(SQ_SIZE + BORDER + MENU, SQ_SIZE * 8 + TIME + BORDER * 2, 60, 60)
        textPlayer2Location = p.Rect(SQ_SIZE + BORDER + MENU, 0, 60, 60)
        backgroundPlayer1Location = p.Rect(SQ_SIZE + BORDER - 10 + MENU, SQ_SIZE * 8 + TIME + BORDER * 2, 60, 60)
        backgroundPlayer2Location = p.Rect(SQ_SIZE + BORDER - 10 + MENU, 0, 60, 60)

        screen.blit(surfacePlayer1, backgroundPlayer1Location)
        screen.blit(surfacePlayer2, backgroundPlayer2Location)
        screen.blit(textPlayer1, textPlayer1Location)
        screen.blit(textPlayer2, textPlayer2Location)
    return gameOver

def gameOverText(screen, whiteToMove):
    color = p.Color('#121212') if whiteToMove else p.Color('#D9D2D2')
    font = p.font.Font('freesansbold.ttf', 100)
    # winner = "Black Win!" if whiteToMove else "White Win!"

    if COLORGAME:
        winner = "White Win!" if whiteToMove else "Black Win!"
    else:
        winner = "Black Win!" if whiteToMove else "White Win!"

    textObj = font.render(winner, True, color)
    textLocation = p.Rect(SQ_SIZE * 4 + BORDER - textObj.get_width() / 2 + MENU,
                          SQ_SIZE * 4 + BORDER + TIME - textObj.get_height() / 2, 60, 60)
    screen.blit(textObj, textLocation)

def drawMoveLog(screen, gs):
    font_path = os.path.join(os.curdir, "Font", "seguisym.ttf")
    font = p.font.Font(font_path, 16)
    moveLogRect = p.Rect(MENU + BOARD + BORDER * 2 + 20, TIME + 10, MOVE_LOG, BORDER * 2 + BOARD)
    # p.draw.rect(screen, p.Color('Black'), moveLogRect)
    moveLog = gs.moveLog
    moveTexts = []
    for i in range(0, len(moveLog), 2):
        moveString = str(i // 2 + 1) + "." + moveLog[i].getChessNotation()
        if i + 1 < len(moveLog):
            moveString += moveLog[i + 1].getChessNotation() + "   "
        moveTexts.append(moveString)
    movesPerRow = 3
    padding = 5
    lineSpacing = 2
    textY = padding
    for i in range(0, len(moveTexts), movesPerRow):
        text = ''
        for j in range(movesPerRow):
            if i + j < len(moveTexts):
                text += moveTexts[i + j]
        textObj = font.render(text, True, p.Color('white'))
        textLocation = moveLogRect.move(padding, textY)
        screen.blit(textObj, textLocation)
        textY += textObj.get_height() + lineSpacing
        if textY >= 677:
            break


if __name__ == "__main__":

    main()
#  py .\chessMain.py MAN 3
# py .\chessMain AUTO 3