from __future__ import annotations
from dataclasses import dataclass, replace
from enum import Enum
from typing import Optional

N=10
PORTAL=frozenset({(4,4),(4,5),(5,4),(5,5)})
CORNERS=frozenset({(0,0),(0,9),(9,0),(9,9)})
THRONE={0:(1,3),1:(8,6)}
# One corner nearest the opponent's marked approach is forbidden for each side.
FORBIDDEN_CORNER={0:(9,9),1:(0,0)}
HOME_ROWS={0:frozenset({1,2}),1:frozenset({7,8})}
class K(Enum): SHIELD='S'; BISHOP='B'; ROOK='R'; PAWN='P'; CANNON='C'; KING='K'; KNIGHT='N'; QUEEN='Q'
class Kid(Enum): TRUE='blue'; HUNTER='yellow'; BOMB='red'
@dataclass(frozen=True)
class Piece:
 side:int; kind:K; kid:Optional[Kid]=None; revealed:bool=False
 def symbol(self): return self.kind.value
@dataclass(frozen=True)
class Move:
 src:tuple[int,int]; dst:tuple[int,int]; via:tuple[tuple[int,int],...]=(); portal_dst:Optional[tuple[int,int]]=None
@dataclass
class State:
 board:dict[tuple[int,int],Piece]
 turn:int=0
 phase:str='play'
 winner:Optional[int]=None
 shield_pending:dict[tuple[int,int],int]=None
 history:list= None
 def __post_init__(self):
  if self.shield_pending is None:self.shield_pending={}
  if self.history is None:self.history=[]

def inside(p): return 0<=p[0]<N and 0<=p[1]<N
def sign(x): return (x>0)-(x<0)
def line(a,b,step):
 r,c=a
 while True:
  r+=step[0];c+=step[1]
  if (r,c)==b:return True
  if not inside((r,c)):return False

def occupied_path(s,a,b,step):
 r,c=a
 while True:
  r+=step[0];c+=step[1]
  if (r,c)==b:return True
  if (r,c) in s.board:return False
  if not inside((r,c)):return False

def dirs(kind):
 if kind in (K.ROOK,K.CANNON): return ((1,0),(-1,0),(0,1),(0,-1))
 if kind==K.BISHOP:return ((1,1),(1,-1),(-1,1),(-1,-1))
 if kind==K.QUEEN:return dirs(K.ROOK)+dirs(K.BISHOP)
 if kind==K.KING or kind==K.SHIELD:return tuple((a,b) for a in (-1,0,1) for b in (-1,0,1) if a or b)
 return ()

def portal_options(side,board):
 return tuple(sorted(CORNERS-{FORBIDDEN_CORNER[side]}-{p for p in board if p in CORNERS}))
def can_capture(attacker,target):
 if attacker.kind==K.SHIELD:return False
 if attacker.kid==Kid.HUNTER:return False
 if attacker.kind==K.KING:return True
 if attacker.kid==Kid.BOMB:return target.kind!=K.KING
 if attacker.kind==K.QUEEN:return True
 return True

def pseudo_moves(s,src):
 p=s.board[src]; out=[]
 def add(dst,via=()):
  if not inside(dst) or dst in PORTAL or dst==src:return
  q=s.board.get(dst)
  if q and q.side==p.side:return
  if q and not can_capture(p,q) and not (q.kind==K.SHIELD and s.shield_pending.get(dst,0)>=1):return
  # kings cannot capture any king unless true king; Hunter/Bomb restrictions handled above
  if p.kind==K.KING and q and q.kind==K.KING and p.kid!=Kid.TRUE:return
  if p.kind==K.PAWN and dst[1]-src[1] not in (-1,1):return
  # Pawn diagonal always captures; non-capture diagonal is its move by this design.
  if p.kind in (K.KING,K.SHIELD) and dst in PORTAL:return
  if dst in CORNERS and dst==FORBIDDEN_CORNER[p.side]: return
  if dst in PORTAL:return
  out.append(Move(src,dst,via))
 # normal pieces
 if p.kind in (K.KING,K.SHIELD):
  steps=1 if p.kind==K.KING else 2
  for d in dirs(p.kind):
   for n in range(1,steps+1):
    dst=(src[0]+d[0]*n,src[1]+d[1]*n)
    if not inside(dst):break
    if dst in PORTAL:break
    if n==2 and (src[0]+d[0],src[1]+d[1]) in s.board:break
    add(dst)
    if dst in s.board:break
 elif p.kind==K.PAWN:
  for dr in (-1,1):
   for dc in (-1,1):add((src[0]+dr,src[1]+dc))
 elif p.kind==K.KNIGHT:
  for dr,dc in ((2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)):add((src[0]+dr,src[1]+dc))
 elif p.kind in (K.BISHOP,K.ROOK,K.QUEEN):
  for d in dirs(p.kind):
   r,c=src
   while True:
    dst=(r+d[0],c+d[1])
    if not inside(dst) or dst in PORTAL:break
    q=s.board.get(dst)
    if q:
     if q.side!=p.side and can_capture(p,q):add(dst)
     break
    add(dst);r,c=dst
 elif p.kind==K.CANNON:
  for d in dirs(K.CANNON):
   r,c=src; seen=False
   while True:
    dst=(r+d[0],c+d[1])
    if not inside(dst) or dst in PORTAL:break
    q=s.board.get(dst)
    if not seen:
     if q:seen=True
     else:add(dst)
    else:
     if q:
      if q.side!=p.side and can_capture(p,q):add(dst)
      break
    r,c=dst
 return out

def portal_moves(s,src):
 p=s.board[src]
 if p.kind==K.KING:return []
 entries=[]
 # A portal entry is a legal one-move landing on any central portal square.
 if p.kind==K.PAWN:
  entries=[q for q in PORTAL if abs(q[0]-src[0])==1 and abs(q[1]-src[1])==1]
 elif p.kind==K.KNIGHT:
  entries=[q for q in PORTAL if (abs(q[0]-src[0]),abs(q[1]-src[1])) in ((1,2),(2,1))]
 elif p.kind==K.SHIELD:
  entries=[q for q in PORTAL if max(abs(q[0]-src[0]),abs(q[1]-src[1])) in (1,2)]
 else:
  for q in PORTAL:
   dr,dc=q[0]-src[0],q[1]-src[1]
   ok=(p.kind in (K.ROOK,K.CANNON) and (dr==0 or dc==0)) or (p.kind==K.BISHOP and abs(dr)==abs(dc)) or (p.kind==K.QUEEN and (dr==0 or dc==0 or abs(dr)==abs(dc)))
   if ok:
    step=(sign(dr),sign(dc)); cur=(src[0]+step[0],src[1]+step[1]); blocked=False
    while cur!=q:
     if cur in s.board: blocked=True
     cur=(cur[0]+step[0],cur[1]+step[1])
    if not blocked: entries.append(q)
 out=[]
 for q in entries:
  for dst in portal_options(p.side,s.board): out.append(Move(src,dst,(q,),dst))
 return out

def legal_moves(s):
 if s.winner is not None or s.phase=='draw':return []
 out=[]
 for src,p in s.board.items():
  if p.side!=s.turn:continue
  out.extend(pseudo_moves(s,src)); out.extend(portal_moves(s,src))
 return out

def _shield_attacked(state, sq, shield_side):
    # Determine whether an enemy has an unobstructed ordinary attack on the shield.
    for src,p in state.board.items():
        if p.side==shield_side: continue
        tmp=dict(state.board); del tmp[sq]
        probe=State(tmp,state.turn,state.phase,state.winner,dict(state.shield_pending),[])
        if any(x.dst==sq for x in pseudo_moves(probe,src)): return True
    return False

def apply(s,m):
 p=s.board[m.src]; b=dict(s.board); del b[m.src]
 if m.portal_dst is not None:
  # Destination is the selected corner; the portal entry square is never occupied.
  target=b.pop(m.dst,None)
 else:
  target=b.pop(m.dst,None)
 winner=None
 if target and target.kind==K.KING and target.kid==Kid.TRUE: winner=p.side
 if target and target.kind==K.KING and target.kid==Kid.BOMB: winner=target.side
 if target and target.kind==K.KING and target.kid==Kid.HUNTER:
  if p.kind==K.KING and p.kid==Kid.TRUE: pass
  else:
   b[m.src]=p; # attacker is destroyed, hunter becomes queen
   b[m.dst]=replace(target,kind=K.QUEEN,kid=None,revealed=True)
   winner=None
   s2=State(b,s.turn^1,'play',winner,dict(s.shield_pending),list(s.history)); s2.history.append(position_key(s2))
   if sum(k==s2.history[-1] for k in s2.history)>=4 and winner is None: s2.phase='draw'
   return s2
 # shield sequential attack: first ordinary attack records pending; next move can capture it
 if target and target.kind==K.SHIELD: pass
 b[m.dst]=p
 # A true King occupying the opponent's throne wins; equivalently, the throne owner loses.
 if p.kind==K.KING and p.kid==Kid.TRUE and m.dst==THRONE[p.side^1]:winner=p.side
 # A shield threat lasts through the opponent's next turn only.
 pending={sq:max(0,n-1) for sq,n in s.shield_pending.items() if n>1}
 s2=State(b,s.turn^1,'play',winner,pending,list(s.history))
 for sq,q in s2.board.items():
  if q.kind==K.SHIELD and _shield_attacked(s2,sq,q.side): s2.shield_pending[sq]=1
 s2.history.append(position_key(s2))
 if sum(k==s2.history[-1] for k in s2.history)>=4 and winner is None: s2.phase='draw'
 if winner is None and terminal_reason(s2)=='no-captures-draw': s2.phase='draw'
 return s2

def position_key(s):
 return (s.turn,tuple(sorted((sq,p.side,p.kind.value,p.kid.value if p.kid else None,p.revealed) for sq,p in s.board.items())),tuple(sorted(s.shield_pending.items())))

def _capture_moves(state):
    out=[]
    for m in legal_moves(state):
        q=state.board.get(m.dst)
        if q is not None and q.side != state.turn: out.append(m)
    return out

def terminal_reason(s):
 if s.phase=='draw':return 'fourfold-repetition'
 if s.winner is not None:return 'win'
 # A side may have any legal movement even when its True King is surrounded.
 # A deadlock is a draw only when neither side has a legal capture.
 if not _capture_moves(s):
  other=State(dict(s.board),s.turn^1,s.phase,s.winner,dict(s.shield_pending),list(s.history))
  if not _capture_moves(other): return 'no-captures-draw'
 if len(s.history)>=4 and s.history[-1]==s.history[-2]==s.history[-3]==s.history[-4]:return 'fourfold-repetition'
 return None

EXPECTED={K.SHIELD:3,K.BISHOP:1,K.ROOK:1,K.PAWN:5,K.CANNON:3,K.KING:3,K.KNIGHT:3}
def validate_setup(board, phase='play'):
    errors=[]
    if len(board)!=len(set(board)): errors.append('duplicate square')
    for sq,p in board.items():
        if not inside(sq): errors.append(f'outside board: {sq}')
        if sq in PORTAL: errors.append(f'piece on portal: {sq}')
        if sq in THRONE and p.kind!=K.KING: errors.append(f'non-king on throne: {sq}')
    for side in (0,1):
        ps=[p for p in board.values() if p.side==side]
        for kind,n in EXPECTED.items():
            if sum(p.kind==kind for p in ps)!=n: errors.append(f'side {side}: expected {n} {kind.value}')
        kids=[p.kid for p in ps if p.kind==K.KING]
        if set(kids)!={Kid.TRUE,Kid.HUNTER,Kid.BOMB}: errors.append(f'side {side}: invalid King identities')
        if phase=='setup' and any(sq[0] not in HOME_ROWS[side] for sq,p in board.items() if p.side==side): errors.append(f'side {side}: setup rank violation')
    return errors

def make_setup(seed=1):
    import random
    rng=random.Random(seed); board={}
    for side in (0,1):
        cells=[(r,c) for r in HOME_ROWS[side] for c in range(N) if (r,c) not in PORTAL]
        rng.shuffle(cells); pieces=[]
        for kind,n in EXPECTED.items():
            for i in range(n): pieces.append(Piece(side,kind,([Kid.TRUE,Kid.HUNTER,Kid.BOMB][i] if kind==K.KING else None)))
        for sq,p in zip(cells,pieces): board[sq]=p
    return State(board,turn=1,history=[])

def public_state(s, viewer):
    """Redacts unrevealed opponent King identities."""
    b={}
    for sq,p in s.board.items():
        if p.side!=viewer and p.kind==K.KING and not p.revealed: b[sq]=replace(p,kid=None)
        else:b[sq]=p
    return State(b,s.turn,s.phase,s.winner,dict(s.shield_pending),list(s.history))
