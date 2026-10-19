import json
from .engine import *

def _key_to_json(key):
    """Encode the tuple-based repetition key without losing hidden state."""
    turn, pieces, shields = key
    return {
        'turn': turn,
        'pieces': [[list(sq), side, kind, kid, revealed] for sq, side, kind, kid, revealed in pieces],
        'shields': [[list(sq), n] for sq, n in shields],
    }

def _key_from_json(data):
    pieces=tuple((tuple(sq), side, kind, kid, revealed) for sq, side, kind, kid, revealed in data['pieces'])
    shields=tuple((tuple(sq), n) for sq, n in data['shields'])
    return (data['turn'], pieces, shields)

def save(state,path):
 d={'turn':state.turn,'phase':state.phase,'winner':state.winner,'shield_pending':[[list(k),v] for k,v in state.shield_pending.items()], 'history':[_key_to_json(x) for x in state.history], 'board':[]}
 for sq,p in state.board.items(): d['board'].append({'sq':list(sq),'side':p.side,'kind':p.kind.value,'kid':p.kid.value if p.kid else None,'revealed':p.revealed})
 with open(path,'w') as f: json.dump(d,f,indent=2)
def load(path):
 with open(path) as f:d=json.load(f)
 b={tuple(x['sq']):Piece(x['side'],K(x['kind']),Kid(x['kid']) if x['kid'] else None,x['revealed']) for x in d['board']}
 return State(b,d['turn'],d['phase'],d['winner'],{tuple(k):v for k,v in d['shield_pending']},[_key_from_json(x) for x in d.get('history',[])])
