import unittest
from su_chess.engine import *
class Rules(unittest.TestCase):
 def test_setup(self): self.assertEqual(validate_setup(make_setup().board),[])
 def test_portal_three_destinations(self):
  s=State({(3,4):Piece(0,K.KNIGHT),(9,9):Piece(1,K.KING,Kid.TRUE)}); self.assertEqual(len([m for m in legal_moves(s) if m.portal_dst]),3)
 def test_bomb_loss(self):
  s=State({(0,0):Piece(0,K.ROOK),(0,1):Piece(1,K.KING,Kid.BOMB)}); m=next(m for m in legal_moves(s) if m.dst==(0,1)); self.assertEqual(apply(s,m).winner,1)
 def test_hunter_promotion(self):
  s=State({(0,0):Piece(0,K.ROOK),(0,1):Piece(1,K.KING,Kid.HUNTER)}); m=next(m for m in legal_moves(s) if m.dst==(0,1)); self.assertEqual(apply(s,m).board[(0,1)].kind,K.QUEEN)
 def test_shield_two_stage_attack(self):
  s=State({(0,0):Piece(0,K.ROOK),(0,3):Piece(1,K.SHIELD),(2,2):Piece(0,K.KNIGHT),(1,1):Piece(1,K.KNIGHT),(9,0):Piece(0,K.KING,Kid.TRUE),(9,9):Piece(1,K.KING,Kid.TRUE)},0)
  m=next(m for m in legal_moves(s) if m.src==(0,0) and m.dst==(0,1)); s=apply(s,m); self.assertIn((0,3),s.shield_pending)
  s=apply(s,next(m for m in legal_moves(s) if m.src==(1,1) and m.dst==(3,2)))
  cap=next(m for m in legal_moves(s) if m.src==(2,2) and m.dst==(0,3)); s=apply(s,cap); self.assertEqual(s.board[(0,3)].side,0)
 def test_true_king_takes_opponent_throne(self):
  s=State({(7,5):Piece(0,K.KING,Kid.TRUE),(8,6):Piece(1,K.KING,Kid.TRUE)},0)
  m=next(m for m in legal_moves(s) if m.src==(7,5) and m.dst==(8,6))
  self.assertEqual(apply(s,m).winner,0)
 def test_no_capture_deadlock_draw(self):
  s=State({(0,0):Piece(0,K.KING,Kid.TRUE),(9,9):Piece(1,K.KING,Kid.TRUE)},0)
  self.assertEqual(terminal_reason(s),'no-captures-draw')
 def test_repetition(self):
  s=State({(0,1):Piece(0,K.KNIGHT),(0,2):Piece(1,K.KNIGHT),(9,0):Piece(0,K.KING,Kid.TRUE),(9,9):Piece(1,K.KING,Kid.TRUE),(5,5):Piece(0,K.BISHOP),(6,6):Piece(1,K.PAWN)},0); s.history=[position_key(s)]; seq=[((0,1),(2,2)),((0,2),(2,3)),((2,2),(0,1)),((2,3),(0,2))]
  for i in range(12):
   a,b=seq[i%4]; s=apply(s,next(m for m in legal_moves(s) if m.src==a and m.dst==b))
  self.assertEqual(s.phase,'draw')
if __name__=='__main__':unittest.main()
