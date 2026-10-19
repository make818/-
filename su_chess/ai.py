import random
from .engine import legal_moves,apply

def choose(state,seed=None):
 rng=random.Random(seed); moves=legal_moves(state)
 if not moves:return None
 wins=[]
 for m in moves:
  ns=apply(state,m)
  if ns.winner==state.turn:wins.append(m)
 if wins:return rng.choice(wins)
 captures=[m for m in moves if m.dst in state.board and state.board[m.dst].side!=state.turn]
 return rng.choice(captures or moves)
