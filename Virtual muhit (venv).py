import pygame
import sys
import copy
import threading

pygame.init()

SIZE = 600
INFO = 60
BOARD = 8
SQ = SIZE // BOARD

WHITE=(255,255,255)
BLACK=(0,0,0)
RED=(200,0,0)
LIGHT=(240,217,181)
DARK=(181,136,99)
GREEN=(0,255,0)
YELLOW=(255,255,0)
BLUE=(50,50,200)
GRAY=(100,100,100)

FONT = pygame.font.SysFont("arial",20)
BIG_FONT = pygame.font.SysFont("arial",32)

class GrandmasterDraughts:

    def __init__(self):
        self.screen=pygame.display.set_mode((SIZE,SIZE+INFO))
        pygame.display.set_caption("Draughts")
        self.clock=pygame.time.Clock()
        self.reset()

    def reset(self):
        self.board=[[None]*8 for _ in range(8)]
        for r in range(3):
            for c in range(8):
                if (r+c)%2==1:
                    self.board[r][c]={'color':'black','king':False}
        for r in range(5,8):
            for c in range(8):
                if (r+c)%2==1:
                    self.board[r][c]={'color':'red','king':False}

        self.turn='red'
        self.selected=None
        self.moves=[]
        self.current_sequences=[]
        self.ai_thinking=False

        self.difficulty=None
        self.in_menu=True

    # MENU
    def draw_menu(self):
        self.screen.fill(BLUE)
        title = BIG_FONT.render("Darajani tanlang", True, WHITE)
        self.screen.blit(title, (SIZE//2 - 120, 150))

        easy = pygame.Rect(SIZE//2-100,250,200,50)
        med  = pygame.Rect(SIZE//2-100,320,200,50)
        hard = pygame.Rect(SIZE//2-100,390,200,50)

        pygame.draw.rect(self.screen,GRAY,easy)
        pygame.draw.rect(self.screen,GRAY,med)
        pygame.draw.rect(self.screen,GRAY,hard)

        self.screen.blit(FONT.render("Oson",True,WHITE),(easy.x+70,easy.y+15))
        self.screen.blit(FONT.render("O‘rtacha",True,WHITE),(med.x+55,med.y+15))
        self.screen.blit(FONT.render("Qiyin",True,WHITE),(hard.x+65,hard.y+15))

        return easy,med,hard

    # DRAW
    def draw(self):
        self.screen.fill(BLUE)
        for r in range(8):
            for c in range(8):
                color=LIGHT if (r+c)%2==0 else DARK
                pygame.draw.rect(self.screen,color,(c*SQ,r*SQ,SQ,SQ))

                if self.selected==(r,c):
                    pygame.draw.rect(self.screen,GREEN,(c*SQ,r*SQ,SQ,SQ),3)

                if (r,c) in self.moves:
                    pygame.draw.rect(self.screen,YELLOW,(c*SQ,r*SQ,SQ,SQ),3)

                p=self.board[r][c]
                if p:
                    center=(c*SQ+SQ//2,r*SQ+SQ//2)
                    radius=SQ//2-10
                    col=RED if p['color']=='red' else BLACK
                    pygame.draw.circle(self.screen,col,center,radius)
                    pygame.draw.circle(self.screen,WHITE,center,radius,2)
                    if p['king']:
                        pygame.draw.circle(self.screen,WHITE,center,radius//2,3)

        if self.difficulty:
            status = f"Daraja: {self.difficulty}"
            self.screen.blit(FONT.render(status,True,WHITE),(10,SIZE+10))

    # MOVE
    def move_piece(self,r,c,nr,nc,board):
        piece=board[r][c]
        board[nr][nc]=copy.deepcopy(piece)
        board[r][c]=None

        dr=1 if nr>r else -1
        dc=1 if nc>c else -1
        cr=r+dr
        cc=c+dc

        while cr!=nr and cc!=nc:
            if board[cr][cc] and board[cr][cc]['color']!=piece['color']:
                board[cr][cc]=None
                break
            cr+=dr
            cc+=dc

        if piece['color']=='red' and nr==0:
            board[nr][nc]['king']=True
        if piece['color']=='black' and nr==7:
            board[nr][nc]['king']=True

    # CAPTURE
    def get_captures(self,r,c,board):
        piece=board[r][c]
        dirs=[(-1,-1),(-1,1),(1,-1),(1,1)]
        sequences=[]

        def dfs(r,c,b,path):
            found=False
            for dr,dc in dirs:
                nr=r+dr
                nc=c+dc
                jr=nr+dr
                jc=nc+dc

                if 0<=jr<8 and 0<=jc<8:
                    if b[nr][nc] and b[nr][nc]['color']!=piece['color'] and b[jr][jc] is None:
                        newb=copy.deepcopy(b)
                        self.move_piece(r,c,jr,jc,newb)
                        dfs(jr,jc,newb,path+[(jr,jc)])
                        found=True

            if not found and path:
                sequences.append(path)

        dfs(r,c,board,[])
        return sequences

    # MOVES
    def get_all_moves_for_color(self, color, board):
        moves=[]
        captures_exist=False

        # majburiy urish
        for r in range(8):
            for c in range(8):
                if board[r][c] and board[r][c]['color']==color:
                    caps=self.get_captures(r,c,board)
                    for seq in caps:
                        moves.append((r,c,seq))
                        captures_exist=True

        if captures_exist:
            return moves,True

        # oddiy moves
        for r in range(8):
            for c in range(8):
                p=board[r][c]
                if p and p['color']==color:

                    if not p['king']:
                        dirs=[(-1,-1),(-1,1)] if p['color']=='red' else [(1,-1),(1,1)]
                    else:
                        dirs=[(-1,-1),(-1,1),(1,-1),(1,1)]

                    for dr,dc in dirs:
                        nr=r+dr
                        nc=c+dc
                        if 0<=nr<8 and 0<=nc<8 and board[nr][nc] is None:
                            moves.append((r,c,[(nr,nc)]))

        return moves,False

    # AI
    def evaluate(self,board):
        score=0
        for r in range(8):
            for c in range(8):
                p=board[r][c]
                if p:
                    val=15 if p['king'] else 5
                    score += val if p['color']=='black' else -val
        return score

    def minimax(self,board,depth,alpha,beta,maximizing):
        if depth==0:
            return self.evaluate(board),None

        color='black' if maximizing else 'red'
        moves,_=self.get_all_moves_for_color(color,board)

        best=None

        if maximizing:
            max_eval=-9999
            for r,c,seq in moves:
                newb=copy.deepcopy(board)
                cr,cc=r,c
                for nr,nc in seq:
                    self.move_piece(cr,cc,nr,nc,newb)
                    cr,cc=nr,nc
                eval,_=self.minimax(newb,depth-1,alpha,beta,False)
                if eval>max_eval:
                    max_eval=eval
                    best=(r,c,seq)
                alpha=max(alpha,eval)
                if beta<=alpha: break
            return max_eval,best
        else:
            min_eval=9999
            for r,c,seq in moves:
                newb=copy.deepcopy(board)
                cr,cc=r,c
                for nr,nc in seq:
                    self.move_piece(cr,cc,nr,nc,newb)
                    cr,cc=nr,nc
                eval,_=self.minimax(newb,depth-1,alpha,beta,True)
                if eval<min_eval:
                    min_eval=eval
                    best=(r,c,seq)
                beta=min(beta,eval)
                if beta<=alpha: break
            return min_eval,best

    def ai_turn(self):
        self.ai_thinking=True
        depth = 2 if self.difficulty=='easy' else 4 if self.difficulty=='medium' else 6

        _,move=self.minimax(self.board,depth,-9999,9999,True)

        if move:
            r,c,seq=move
            cr,cc=r,c
            for nr,nc in seq:
                self.move_piece(cr,cc,nr,nc,self.board)
                cr,cc=nr,nc

        self.turn='red'
        self.ai_thinking=False

    # LOOP
    def run(self):
        while True:
            if self.in_menu:
                easy,med,hard=self.draw_menu()
                pygame.display.update()

                for e in pygame.event.get():
                    if e.type==pygame.QUIT:
                        pygame.quit()
                        sys.exit()

                    if e.type==pygame.MOUSEBUTTONDOWN:
                        x,y=pygame.mouse.get_pos()
                        if easy.collidepoint(x,y):
                            self.difficulty='easy'
                            self.in_menu=False
                        elif med.collidepoint(x,y):
                            self.difficulty='medium'
                            self.in_menu=False
                        elif hard.collidepoint(x,y):
                            self.difficulty='hard'
                            self.in_menu=False
                continue

            for e in pygame.event.get():
                if e.type==pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if e.type==pygame.MOUSEBUTTONDOWN and not self.ai_thinking:
                    x,y=pygame.mouse.get_pos()
                    if y<SIZE:
                        r=y//SQ
                        c=x//SQ
                        all_moves,capture_exist=self.get_all_moves_for_color('red',self.board)

                        # agar qizil tosh bosilgan bo'lsa
                        if self.board[r][c] and self.board[r][c]['color']=='red':
                            self.selected=(r,c)
                            self.moves=[]
                            self.current_sequences=[]
                            for sr,sc,seq in all_moves:
                                if (sr,sc)==(r,c):
                                    self.moves.append(seq[0])
                                    self.current_sequences.append(seq)

                        # aks holda move qilamiz
                        elif self.selected:
                            for i,(sr,sc,seq) in enumerate(all_moves):
                                if (sr,sc)==self.selected and seq[0]==(r,c):
                                    cr,cc=sr,sc
                                    for nr,nc in seq:
                                        self.move_piece(cr,cc,nr,nc,self.board)
                                        cr,cc=nr,nc

                                    self.selected=None
                                    self.moves=[]
                                    self.current_sequences=[]
                                    self.turn='black'
                                    threading.Thread(target=self.ai_turn).start()
                                    break

            self.draw()
            pygame.display.update()
            self.clock.tick(60)

if __name__=="__main__":
    game=GrandmasterDraughts()
    game.run()