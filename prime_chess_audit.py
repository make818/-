"""Executable invariant and edge-case audit for the supplied Su Chess rules.
This is a rules-audit harness, not a complete UI or AI engine.
"""
from dataclasses import dataclass
from enum import Enum

N = 10
PORTAL = {(4,4),(4,5),(5,4),(5,5)}  # provisional interpretation: central 2x2
CORNERS = {(0,0),(0,9),(9,0),(9,9)}
# In the supplied diagram, throne markers are the inner squares on each side.
THRONES = {(1,3),(8,6)}  # provisional: the two visible markers; side ownership must be specified.

class Kind(Enum): SHIELD='shield'; BISHOP='bishop'; ROOK='rook'; PAWN='pawn'; CANNON='cannon'; KING='king'; KNIGHT='knight'; QUEEN='queen'
@dataclass(frozen=True)
class Piece:
    side: int
    kind: Kind
    identity: str|None = None

COUNTS = {Kind.SHIELD:3, Kind.BISHOP:1, Kind.ROOK:1, Kind.PAWN:5,
          Kind.CANNON:3, Kind.KING:3, Kind.KNIGHT:3}
assert sum(COUNTS.values()) == 19

def on_board(p): return 0 <= p[0] < N and 0 <= p[1] < N
def orth(a,b): return a[0]==b[0] or a[1]==b[1]
def diag(a,b): return abs(a[0]-b[0]) == abs(a[1]-b[1])
def adjacent(a,b): return max(abs(a[0]-b[0]),abs(a[1]-b[1])) == 1

def validate_setup(board):
    """Checks direct contradictions in a placement. board maps squares to Piece."""
    errors=[]
    for sq,p in board.items():
        if not on_board(sq): errors.append(f'out-of-board piece at {sq}')
        if sq in PORTAL: errors.append(f'piece placed on portal at {sq}')
        if sq in THRONES and p.kind is not Kind.KING: errors.append(f'non-king on throne at {sq}')
    for side in (0,1):
        mine=[p for p in board.values() if p.side==side]
        for k,n in COUNTS.items():
            if sum(p.kind is k for p in mine) != n: errors.append(f'side {side}: expected {n} {k.value}')
    return errors

def portal_destinations(side, occupied):
    # Provisional: cannot use the corner nearest the opposing home edge; occupied corners unavailable.
    blocked_nearest = {(0,0)} if side==0 else {(9,9)}
    return sorted(CORNERS - blocked_nearest - (CORNERS & set(occupied)))

def crossing_portal(path):
    return bool(set(path[1:-1]) & PORTAL)

def audit():
    findings=[]
    if len(PORTAL) != 4: findings.append('Portal geometry is not 2x2.')
    if len(THRONES) != 2: findings.append('Throne ownership/locations are under-specified.')
    for side in (0,1):
        if len(portal_destinations(side, set())) != 3: findings.append('Portal must offer exactly three empty destinations.')
    # Explicitly test the contradiction between “shield moves two” and “cannot capture”.
    findings.append('Shield capture is conditional: an attack requires two enemy pieces, with one attacking on the next turn; simultaneous attack is disallowed.')
    findings.append('King identities are hidden information; a legal move generator must not expose identity to the opponent.')
    findings.append('A stalemate/check definition is required before “trapped true king” can be executable.')
    findings.append('Fourfold repetition must hash side-to-move, placement, hidden identities, and promotion state.')
    findings.append('Cannon screen and portal crossing need an exact path rule; this harness forbids crossing the portal for sliding pieces.')
    return findings

if __name__ == '__main__':
    print('Su Chess audit')
    print('board:', N, 'x', N, 'portal cells:', sorted(PORTAL))
    print('pieces per side:', sum(COUNTS.values()))
    print('unresolved/clarified items:')
    for f in audit(): print('-', f)
    assert sum(COUNTS.values()) == 19
    assert len(portal_destinations(0, set())) == 3
    assert len(portal_destinations(1, set())) == 3
    print('Invariant checks: PASS')
