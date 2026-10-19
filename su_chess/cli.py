import argparse
from .engine import *
from .ai import choose
from .storage import save,load

def show(s):
 for r in range(10): print(' '.join(s.board.get((r,c),Piece(-1,None)).symbol() if (r,c) in s.board else '.' for c in range(10)))
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--load'); ap.add_argument('--ai',action='store_true'); ap.add_argument('--save',default='su_chess_save.json'); a=ap.parse_args()
 s=load(a.load) if a.load else make_setup()
 print('Su Chess experimental CLI. Coordinates are row,col. Type: row,col row,col | save | quit')
 while s.winner is None and s.phase!='draw':
  show(s); print('turn',s.turn,'legal',len(legal_moves(s)))
  if a.ai and s.turn==1:m=choose(s); print('AI:',m)
  else:
   raw=input('move> ').strip()
   if raw=='quit':break
   if raw=='save':save(s,a.save); print('saved'); continue
   try:
    x,y=raw.split(); src=tuple(map(int,x.split(','))); dst=tuple(map(int,y.split(','))); m=next(m for m in legal_moves(s) if m.src==src and m.dst==dst)
   except Exception as e: print('invalid move',e); continue
  s=apply(s,m)
 save(s,a.save); print('finished',s.winner or s.phase)
if __name__=='__main__':main()
