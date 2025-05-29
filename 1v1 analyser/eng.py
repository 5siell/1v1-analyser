# engine_1v1.py  – all logic for 1-v-1 ABBA drafts
# =================================================

# ----------  tree data structure ----------
class Node:
    def __init__(self, picks=None, first_ok=True, second_ok=True):
        self.picks = picks if picks else []          # strictly increasing ints
        self.first_ok  = first_ok    # valid when we pick first
        self.second_ok = second_ok   # valid when we pick second
        self.children  = []

    def copy(self):
        return Node(self.picks.copy(), self.first_ok, self.second_ok)

# ----------  generate all legal sequences ----------
def _gen(node, max_pick):
    if len(node.picks) == max_pick:
        return
    depth      = len(node.picks) + 1          # 1-based index of the pick we’re choosing now
    our_picks  = depth - 1
    # ---------- side "first" ----------
    if node.first_ok:
        opp_before = our_picks if depth % 2 else our_picks + 1
        max_val = opp_before + 1 + our_picks
        start   = node.picks[-1] if node.picks else 0
        for v in range(start+1, max_val+1):
            c = node.copy()
            c.second_ok = False
            c.picks.append(v)
            node.children.append(c)
            _gen(c, max_pick)
    # ---------- side "second" ----------
    if node.second_ok:
        opp_before = our_picks + 1 if depth % 2 else our_picks
        max_val = opp_before + 1 + our_picks
        start   = node.picks[-1] if node.picks else 0
        for v in range(start+1, max_val+1):
            c = node.copy()
            c.first_ok = False
            c.picks.append(v)
            node.children.append(c)
            _gen(c, max_pick)

def _leaves(root):
    out = []
    stk = [root]
    while stk:
        n = stk.pop()
        if n.children:
            stk.extend(n.children)
        else:
            out.append(n)
    return out

# ----------  public helper ----------
def enumerate_combos(max_pick, included, excluded):
    """Return dict{ tuple(prefix) : flags & counts } for fast grouping."""
    root = Node()
    _gen(root, max_pick)
    leaves = _leaves(root)

    inc = set(included)
    exc = set(excluded)

    table = {}          # prefix-tuple -> (first_ok, second_ok, count)
    for n in leaves:
        if inc and not inc.issubset(n.picks):            continue
        if exc and exc.intersection(n.picks):            continue
        key = tuple(n.picks)
        if key not in table:
            table[key] = [n.first_ok, n.second_ok, 1]
        else:
            p = table[key]
            p[0] |= n.first_ok
            p[1] |= n.second_ok
            p[2] += 1
    return table           # dict of unique final combos
# ----------  utility ----------
def side_for_pick(idx):    # idx is 1-based position in sequence
    if idx == 1:                    return "first"
    mod = idx % 4
    return "second" if mod in (2,3) else "first"

# ----------  function Streamlit will call ----------
def run_analysis(max_pick, included, excluded, prefix_len):
    combos = enumerate_combos(max_pick, included, excluded)
    if not combos:
        return "No combos", []

    # group by prefix length
    groups = {}
    for seq, (f_ok, s_ok, _) in combos.items():
        if len(seq) < prefix_len:  continue
        pref = seq[:prefix_len]
        if pref not in groups:
            groups[pref] = [0,0,0]      # first, second, total
        g = groups[pref]
        if f_ok: g[0] += 1
        if s_ok: g[1] += 1
        g[2] += 1

    total_final = sum(v[2] for v in groups.values())
    rows = []
    for pref, (f_cnt, s_cnt, tot) in sorted(groups.items()):
        side = side_for_pick(prefix_len)
        rows.append({
            "Prefix": pref,
            "Total":  tot,
            "Percent": f"{tot/total_final*100:.1f}",
            "Possible as": "both" if f_cnt and s_cnt else
                           "first" if f_cnt            else "second"
        })
    header = f"{len(combos)} unique final combos after filters"
    return header, rows
