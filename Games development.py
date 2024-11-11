import tkinter as tk
from tkinter import messagebox as msg
import sqlite3
import random

global move_history

# Hàm tạo bàn cờ rỗng
def make_empty_board(sz):
    return [[' '] * sz for _ in range(sz)]

# Kiểm tra nếu bàn cờ rỗng
def is_empty(board):
    return all(cell == ' ' for row in board for cell in row)

def is_in(board, y, x):
    return 0 <= y < len(board) and 0 <= x < len(board)

def is_win(board):
    
    black = score_of_col(board,'b')
    white = score_of_col(board,'w')
    
    sum_sumcol_values(black)
    sum_sumcol_values(white)
    
    if 5 in black and black[5] == 1:
        return 'Black wins'
    elif 5 in white and white[5] == 1:
        return 'White wins'
        
    if sum(black.values()) == black[-1] and sum(white.values()) == white[-1] or possible_moves(board)==[]:
        return 'Draw'
    return 'Continue playing'

# Hàm vẽ quân cờ
def draw_stone(canvas, x, y, color):
    cell_size = 40
    offset = cell_size // 2
    canvas.create_oval(x * cell_size + 5, y * cell_size + 5, (x + 1) * cell_size - 5, (y + 1) * cell_size - 5, fill=color, outline="")

# Xử lý sự kiện click chuột
def click(event):
    global board, colors, move_history, turn, mode
    cell_size = 40
    x, y = event.x // cell_size, event.y // cell_size

    if not is_in(board, y, x) or board[y][x] != ' ':
        return

    # Lượt người chơi 1
    if turn == 'black':
        draw_stone(canvas, x, y, "black")
        board[y][x] = 'b'
        move_history.append((x, y))

        game_res = is_win(board)
        if game_res != 'Continue playing':
            msg.showinfo("Kết quả", f"Chúc mừng! {game_res}")
            save_game(game_res, move_history)
            reset_game(len(board))
            return

        turn = 'white'  # Đổi lượt

        # Nếu chế độ là chơi với AI, thực hiện lượt của AI
        if mode == 'ai':
            ay, ax = best_move(board, 'w')
            draw_stone(canvas, ax, ay, "white")
            board[ay][ax] = 'w'
            move_history.append((ax, ay))

            game_res = is_win(board)
            if game_res != 'Continue playing':
                msg.showinfo("Kết quả", f"Chúc mừng! {game_res}")  # Hiển thị hộp thoại khi AI thắng
                save_game(game_res, move_history)
                reset_game(len(board))
            turn = 'black'
    else:
        # Nếu là chế độ hai người chơi
        if mode == '2p':
            draw_stone(canvas, x, y, "white")
            board[y][x] = 'w'
            move_history.append((x, y))

            game_res = is_win(board)
            if game_res != 'Continue playing':
                msg.showinfo("Kết quả", f"Chúc mừng! {game_res}")  # Hiển thị hộp thoại khi người chơi 2 thắng
                save_game(game_res, move_history)
                reset_game(len(board))
                return

            turn = 'black'  # Đổi lượt lại cho người chơi 1

# Khởi tạo game
def initialize(size):
    global board, move_history, canvas, turn, root, mode

    move_history = []
    board = make_empty_board(size)
    turn = 'black'  # Luôn bắt đầu với màu đen (người chơi 1)
    mode = 'ai'

    root = tk.Tk()
    root.title("Nguyễn Quốc Tuấn")
    root.iconbitmap('icon.ico')

    canvas = tk.Canvas(root, width=600, height=600, bg='orange')
    canvas.pack()

    # Vẽ bàn cờ
    draw_board(canvas, size)

    # Lắng nghe sự kiện click chuột
    canvas.bind("<Button-1>", click)

    # Thêm các nút điều khiển
    control_frame = tk.Frame(root)
    control_frame.pack()

    # Nút chọn chế độ
    mode_var = tk.StringVar(value='ai')
    tk.Radiobutton(control_frame, text="Chơi với AI", variable=mode_var, value='ai', command=lambda: set_mode('ai')).pack(side=tk.LEFT)
    tk.Radiobutton(control_frame, text="2 Người Chơi", variable=mode_var, value='2p', command=lambda: set_mode('2p')).pack(side=tk.LEFT)

    # Nút đặt lại
    tk.Button(control_frame, text="Reset", command=lambda: reset_game(size)).pack(side=tk.LEFT)

    root.mainloop()

def draw_board(canvas, size):
    '''
    Draws the game board grid on the canvas.
    '''
    for i in range(size):
        # Draw vertical lines
        canvas.create_line(i * 40, 0, i * 40, size * 40, fill="black")
        # Draw horizontal lines
        canvas.create_line(0, i * 40, size * 40, i * 40, fill="black")

def set_mode(selected_mode):
    global mode
    mode = selected_mode

def reset_game(size):
    '''Đặt lại bàn cờ và khởi động lại trò chơi'''
    global board, move_history, turn
    canvas.delete("all")  # Xóa tất cả trên canvas
    board = make_empty_board(size)
    move_history = []
    turn = 'black'  # Luôn bắt đầu với màu đen
    draw_board(canvas, size)

##AI Engine

def march(board,y,x,dy,dx,length):
    '''
    tìm vị trí xa nhất trong dy,dx trong khoảng length

    '''
    yf = y + length*dy 
    xf = x + length*dx
    # chừng nào yf,xf không có trong board
    while not is_in(board,yf,xf):
        yf -= dy
        xf -= dx
        
    return yf,xf
    
def score_ready(scorecol):
    '''
    Khởi tạo hệ thống điểm

    '''
    sumcol = {0: {},1: {},2: {},3: {},4: {},5: {},-1: {}}
    for key in scorecol:
        for score in scorecol[key]:
            if key in sumcol[score]:
                sumcol[score][key] += 1
            else:
                sumcol[score][key] = 1
            
    return sumcol
    
def sum_sumcol_values(sumcol):
    '''
    hợp nhất điểm của mỗi hướng
    '''
    
    for key in sumcol:
        if key == 5:
            sumcol[5] = int(1 in sumcol[5].values())
        else:
            sumcol[key] = sum(sumcol[key].values())
            
def score_of_list(lis,col):
    
    blank = lis.count(' ')
    filled = lis.count(col)
    
    if blank + filled < 5:
        return -1
    elif blank == 5:
        return 0
    else:
        return filled

def row_to_list(board,y,x,dy,dx,yf,xf):
    '''
    trả về list của y,x từ yf,xf
    
    '''
    row = []
    while y != yf + dy or x !=xf + dx:
        row.append(board[y][x])
        y += dy
        x += dx
    return row
    
def score_of_row(board,cordi,dy,dx,cordf,col):
    '''
    trả về một list với mỗi phần tử đại diện cho số điểm của 5 khối

    '''
    colscores = []
    y,x = cordi
    yf,xf = cordf
    row = row_to_list(board,y,x,dy,dx,yf,xf)
    for start in range(len(row)-4):
        score = score_of_list(row[start:start+5],col)
        colscores.append(score)
    
    return colscores

def score_of_col(board,col):
    '''
    tính toán điểm số mỗi hướng của column dùng cho is_win;
    '''

    f = len(board)
    #scores của 4 hướng đi
    scores = {(0,1):[],(-1,1):[],(1,0):[],(1,1):[]}
    for start in range(len(board)):
        scores[(0,1)].extend(score_of_row(board,(start, 0), 0, 1,(start,f-1), col))
        scores[(1,0)].extend(score_of_row(board,(0, start), 1, 0,(f-1,start), col))
        scores[(1,1)].extend(score_of_row(board,(start, 0), 1,1,(f-1,f-1-start), col))
        scores[(-1,1)].extend(score_of_row(board,(start,0), -1, 1,(0,start), col))
        
        if start + 1 < len(board):
            scores[(1,1)].extend(score_of_row(board,(0, start+1), 1, 1,(f-2-start,f-1), col)) 
            scores[(-1,1)].extend(score_of_row(board,(f -1 , start + 1), -1,1,(start+1,f-1), col))
            
    return score_ready(scores)
    
def score_of_col_one(board,col,y,x):
    '''
    trả lại điểm số của column trong y,x theo 4 hướng,
    key: điểm số khối đơn vị đó -> chỉ ktra 5 khối thay vì toàn bộ
    '''
    
    scores = {(0,1):[],(-1,1):[],(1,0):[],(1,1):[]}
    
    scores[(0,1)].extend(score_of_row(board,march(board,y,x,0,-1,4), 0, 1,march(board,y,x,0,1,4), col))
    
    scores[(1,0)].extend(score_of_row(board,march(board,y,x,-1,0,4), 1, 0,march(board,y,x,1,0,4), col))
    
    scores[(1,1)].extend(score_of_row(board,march(board,y,x,-1,-1,4), 1, 1,march(board,y,x,1,1,4), col))

    scores[(-1,1)].extend(score_of_row(board,march(board,y,x,-1,1,4), 1,-1,march(board,y,x,1,-1,4), col))
    
    return score_ready(scores)
    
def possible_moves(board):  
    '''
    khởi tạo danh sách tọa độ có thể có tại danh giới các nơi đã đánh phạm vi 3 đơn vị
    '''
    #mảng taken lưu giá trị của người chơi và của máy trên bàn cờ
    taken = []
    # mảng directions lưu hướng đi (8 hướng)
    directions = [(0,1),(0,-1),(1,0),(-1,0),(1,1),(-1,-1),(-1,1),(1,-1)]
    # cord: lưu các vị trí không đi 
    cord = {}
    
    for i in range(len(board)):
        for j in range(len(board)):
            if board[i][j] != ' ':
                taken.append((i,j))
    ''' duyệt trong hướng đi và mảng giá trị trên bàn cờ của người chơi và máy, kiểm tra nước không thể đi(trùng với 
    nước đã có trên bàn cờ)
    '''
    for direction in directions:
        dy,dx = direction
        for coord in taken:
            y,x = coord
            for length in [1,2,3,4]:
                move = march(board,y,x,dy,dx,length)
                if move not in taken and move not in cord:
                    cord[move]=False
    return cord
    
def TF34score(score3,score4):
    '''
    trả lại trường hợp chắc chắn có thể thắng(4 ô liên tiếp)
    '''
    for key4 in score4:
        if score4[key4] >=1:
            for key3 in score3:
                if key3 != key4 and score3[key3] >=2:
                        return True
    return False
    
def stupid_score(board,col,anticol,y,x):
    '''
    cố gắng di chuyển y,x
    trả về điểm số tượng trưng lợi thế 
    '''
    
    global colors
    M = 1000
    res,adv, dis = 0, 0, 0
    
    #tấn công
    board[y][x]=col
    #draw_stone(x,y,colors[col])
    sumcol = score_of_col_one(board,col,y,x)       
    a = winning_situation(sumcol)
    adv += a * M
    sum_sumcol_values(sumcol)
    #{0: 0, 1: 15, 2: 0, 3: 0, 4: 0, 5: 0, -1: 0}
    adv +=  sumcol[-1] + sumcol[1] + 4*sumcol[2] + 8*sumcol[3] + 16*sumcol[4]
    
    #phòng thủ
    board[y][x]=anticol
    sumanticol = score_of_col_one(board,anticol,y,x)  
    d = winning_situation(sumanticol)
    dis += d * (M-100)
    sum_sumcol_values(sumanticol)
    dis += sumanticol[-1] + sumanticol[1] + 4*sumanticol[2] + 8*sumanticol[3] + 16*sumanticol[4]

    res = adv + dis
    
    board[y][x]=' '
    return res
    
def winning_situation(sumcol):
    '''
    trả lại tình huống chiến thắng dạng như:
    {0: {}, 1: {(0, 1): 4, (-1, 1): 3, (1, 0): 4, (1, 1): 4}, 2: {}, 3: {}, 4: {}, 5: {}, -1: {}}
    1-5 lưu điểm có độ nguy hiểm từ thấp đến cao,
    -1 là rơi vào trạng thái tồi, cần phòng thủ
    '''
    
    if 1 in sumcol[5].values():
        return 5
    elif len(sumcol[4])>=2 or (len(sumcol[4])>=1 and max(sumcol[4].values())>=2):
        return 4
    elif TF34score(sumcol[3],sumcol[4]):
        return 4
    else:
        score3 = sorted(sumcol[3].values(),reverse = True)
        if len(score3) >= 2 and score3[0] >= score3[1] >= 2:
            return 3
    return 0
    
def best_move(board,col):
    '''
    trả lại điểm số của mảng trong lợi thế của từng màu
    '''
    if col == 'w':
        anticol = 'b'
    else:
        anticol = 'w'
        
    movecol = (0,0)
    maxscorecol = ''
    # kiểm tra nếu bàn cờ rỗng thì cho vị trí random nếu không thì đưa ra giá trị trên bàn cờ nên đi 
    if is_empty(board):
        movecol = ( int((len(board))*random.random()),int((len(board[0]))*random.random()))
    else:
        moves = possible_moves(board)

        for move in moves:
            y,x = move
            if maxscorecol == '':
                scorecol=stupid_score(board,col,anticol,y,x)
                maxscorecol = scorecol
                movecol = move
            else:
                scorecol=stupid_score(board,col,anticol,y,x)
                if scorecol > maxscorecol:
                    maxscorecol = scorecol
                    movecol = move
    return movecol

##Graphics Engine

def best_move(board, col):
    if col == 'w':
        anticol = 'b'
    else:
        anticol = 'w'
        
    movecol = (0, 0)
    if is_empty(board):
        movecol = (random.randint(0, len(board) - 1), random.randint(0, len(board) - 1))
    else:
        moves = possible_moves(board)
        maxscorecol = ''
        for move in moves:
            y, x = move
            if maxscorecol == '':
                scorecol = stupid_score(board, col, anticol, y, x)
                maxscorecol = scorecol
                movecol = move
            else:
                scorecol = stupid_score(board, col, anticol, y, x)
                if scorecol > maxscorecol:
                    maxscorecol = scorecol
                    movecol = move
    return movecol


def march(board, y, x, dy, dx, length):
    # Hàm di chuyển kiểm tra khoảng cách
    yf = y + length * dy 
    xf = x + length * dx
    while not is_in(board, yf, xf):
        yf -= dy
        xf -= dx
    return yf, xf

# Kết nối tới cơ sở dữ liệu (hoặc tạo nếu chưa có)
def connect_to_db():
    conn = sqlite3.connect('tic_tac_toe_game.db')
    return conn

def create_games_table():
    conn = connect_to_db()
    cursor = conn.cursor()

    # Tạo bảng nếu chưa có
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS games (
        game_id INTEGER PRIMARY KEY AUTOINCREMENT,
        winner TEXT,
        moves TEXT
    )
    ''')
    conn.commit()
    conn.close()

def save_game(winner, moves):
    conn = connect_to_db()
    cursor = conn.cursor()

    # Chuyển các tuple trong moves thành chuỗi
    moves_str = [f"{move[0]}: {move[1]}" for move in moves]

    # Lưu thông tin vào bảng games
    cursor.execute('''
    INSERT INTO games (winner, moves) 
    VALUES (?, ?)
    ''', (winner, ','.join(moves_str)))

    conn.commit()
    conn.close()

def get_game_history():
    conn = connect_to_db()
    cursor = conn.cursor()

    # Lấy danh sách các ván đấu đã hoàn thành
    cursor.execute('SELECT * FROM games')
    games = cursor.fetchall()

    conn.close()
    return games
    
if __name__ == '__main__':
    create_games_table()
    initialize(15)