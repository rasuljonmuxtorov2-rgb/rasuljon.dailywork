import pygame
import sys
import copy
import threading

pygame.init()

SIZE = 600
INFO = 60  # YANGILANDI: info bar uchun joy kengaytirildi
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
BIG_FONT = pygame.font.SysFont("arial",32)  # YANGILANDI

class GrandmasterDraughts:

    def __init__(self):
        self.screen=pygame.display.set_mode((SIZE,SIZE+INFO))
        pygame.display.set_caption("Grandmaster Flying King Draughts")
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
        self.game_over=False
        self.winner=None  # YANGILANDI: g'alaba holati

    # ================= DRAW =================

    def draw(self):
        self.screen.fill(BLUE)

        # Doska chizish
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

        # YANGILANDI: Yangi o'yin tugmasi
        button_rect = pygame.Rect(SIZE - 110, SIZE + 10, 100, 40)
        pygame.draw.rect(self.screen, GRAY, button_rect)
        btn_text = FONT.render("Yangi o'yin", True, WHITE)
        text_rect = btn_text.get_rect(center=button_rect.center)
        self.screen.blit(btn_text, text_rect)

        # Holat xabari
        status=""
        if self.game_over:
            if self.winner == 'red':
                status = "Siz g‘alaba qozondingiz!"
            elif self.winner == 'black':
                status = "AI g‘alaba qozondi!"
            else:
                status = "O‘yin durang bilan tugadi!"
        elif self.ai_thinking:
            status="AI o‘ylayapti..."
        elif self.turn=='red':
            status="Sizning navbatingiz"
        else:
            status="AI navbati"

        status_text = FONT.render(status,True,WHITE)
        self.screen.blit(status_text,(10,SIZE+10))

    # ================= MOVE =================

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

    # ================= CAPTURE =================

    def get_captures(self,r,c,board):
        piece=board[r][c]
        dirs=[(-1,-1),(-1,1),(1,-1),(1,1)]
        sequences=[]
        def dfs(r,c,b,path):
            found=False

            for dr,dc in dirs:

                # Damka (cheksiz diagonalda urish)
                if piece['king']:
                    step=1
                    enemy_found=False
                    enemy_r=enemy_c=None

                    while True:
                        nr=r+dr*step
                        nc=c+dc*step

                        if not (0<=nr<8 and 0<=nc<8):
                            break

                        if b[nr][nc] is None:
                            if enemy_found:
                                newb=copy.deepcopy(b)
                                self.move_piece(r,c,nr,nc,newb)
                                dfs(nr,nc,newb,path+[(nr,nc)])
                                found=True
                            step+=1
                            continue

                        if b[nr][nc]['color']==piece['color']:
                            break

                        if not enemy_found:
                            enemy_found=True
                            enemy_r,enemy_c=nr,nc
                            step+=1
                            continue
                        else:
                            break

                # Oddiy tosh uchun
                else:
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

    # ================= GET ALL MOVES FOR IXTİYORIY TOSH =================

    def get_all_moves_for_color(self, color, board):
        moves = []
        captures_exist = False

        # Avvalo hamma toshlar uchun urishlarni topamiz
        for r in range(8):
            for c in range(8):
                if board[r][c] and board[r][c]['color'] == color:
                    caps = self.get_captures(r, c, board)
                    for seq in caps:
                        moves.append((r, c, seq))
                        captures_exist = True

        # Agar urishlar bor bo'lsa, faqat ularni qaytaramiz (ixtiyoriy urish)
        if captures_exist:
            return moves, True

        # Urishlar yo'q bo'lsa, oddiy yurishlarni topamiz
        for r in range(8):
            for c in range(8):
                p = board[r][c]
                if p and p['color'] == color:
                    dirs = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
                    for dr, dc in dirs:
                        if p['king']:
                            step = 1
                            while True:
                                nr = r + dr * step
                                nc = c + dc * step
                                if not (0 <= nr < 8 and 0 <= nc < 8):
                                    break
                                if board[nr][nc] is None:
                                    moves.append((r, c, [(nr, nc)]))
                                    step += 1
                                else:
                                    break
                        else:
                            nr = r + dr
                            nc = c + dc
                            if 0 <= nr < 8 and 0 <= nc < 8 and board[nr][nc] is None:
                                if (p['color'] == 'red' and dr == -1) or (p['color'] == 'black' and dr == 1):
                                    moves.append((r, c, [(nr, nc)]))
        return moves, False

    # ================= AI =================
    def evaluate(self,board):
        score=0
        for r in range(8):
            for c in range(8):
                p=board[r][c]
                if p:
                    val=15 if p['king'] else 5
                    if p['color']=='black':
                        score+=val+(7-r)*0.3
                    else:
                        score-=val+r*0.3
        return score

    def minimax(self,board,depth,alpha,beta,maximizing):
        if depth==0:
            return self.evaluate(board),None

        color='black' if maximizing else 'red'
        moves,_=self.get_all_moves_for_color(color,board)
        if not moves:
            return self.evaluate(board),None

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
        pygame.display.update()

        _,move=self.minimax(self.board,6,-9999,9999,True)

        if move:
            r,c,seq=move
            cr,cc=r,c
            for nr,nc in seq:
                self.move_piece(cr,cc,nr,nc,self.board)
                cr,cc=nr,nc

        self.turn='red'
        self.ai_thinking=False

    # ================= CHECK GAME OVER =================
    def check_game_over(self):
        # Agar raqib toshlari qolmasa yoki yurish imkoniyati bo'lmasa
        red_exists = any(self.board[r][c] and self.board[r][c]['color']=='red' for r in range(8) for c in range(8))
        black_exists = any(self.board[r][c] and self.board[r][c]['color']=='black' for r in range(8) for c in range(8))

        if not red_exists:
            self.game_over = True
            self.winner = 'black'
            return True

        if not black_exists:
            self.game_over = True
            self.winner = 'red'
            return True

        # Navbati kimda bo'lsa, u uchun yurishlar borligini tekshirish
        moves, _ = self.get_all_moves_for_color(self.turn, self.board)
        if not moves:
            self.game_over = True
            # Agar navbati "red" bo'lsa, demak red yurish qilolmayapti, AI g'alaba qozondi
            # aks holda red g'alaba qozondi
            self.winner = 'black' if self.turn == 'red' else 'red'
            return True

        return False

    # ================= LOOP =================

    def run(self):
        while True:
            for e in pygame.event.get():
                if e.type==pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if e.type==pygame.MOUSEBUTTONDOWN and not self.ai_thinking:
                    x,y=pygame.mouse.get_pos()

                    # YANGILANDI: Yangi o'yin tugmasi bosilganligini tekshirish
                    button_rect = pygame.Rect(SIZE - 110, SIZE + 10, 100, 40)
                    if button_rect.collidepoint(x,y):
                        self.reset()
                        continue

                    if y<SIZE and not self.game_over:
                        r=y//SQ
                        c=x//SQ
                        all_moves, captures_exist = self.get_all_moves_for_color('red', self.board)

                        if self.selected:
                            if self.board[r][c] and self.board[r][c]['color']=='red':
                                self.selected = (r,c)
                                self.moves = []
                                self.current_sequences = []
                                for sr,sc,seq in all_moves:
                                    if (sr,sc) == (r,c):
                                        self.moves.append(seq[0])
                                        self.current_sequences.append(seq)
                            else:
                                for i,mv in enumerate(self.moves):
                                    if (r,c) == mv:
                                        seq = self.current_sequences[i]
                                        cr,cc = self.selected
                                        for nr,nc in seq:
                                            self.move_piece(cr,cc,nr,nc,self.board)
                                            cr,cc = nr,nc
                                        self.selected = None
                                        self.moves = []
                                        self.current_sequences = []
                                        self.turn = 'black'
                                        threading.Thread(target=self.ai_turn).start()
                                        break
                        else:
                            if self.board[r][c] and self.board[r][c]['color']=='red':
                                self.selected = (r,c)
                                self.moves = []
                                self.current_sequences = []
                                for sr,sc,seq in all_moves:
                                    if (sr,sc) == (r,c):
                                        self.moves.append(seq[0])
                                        self.current_sequences.append(seq)

            # O'yin tugadi-yo'qligini tekshirish
            if not self.game_over:
                self.check_game_over()

            self.draw()
            pygame.display.update()
            self.clock.tick(60)

if __name__=="__main__":
    game=GrandmasterDraughts()
    game.run()
    