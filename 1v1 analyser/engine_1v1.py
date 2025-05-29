# engine_1v1.py  – complete ABBA draft engine for 1-v-1
# ====================================================

# ---------- tree structure ----------
class Node:
    def __init__(self, picks=None, first_ok=True, second_ok=True):
        self.picks = picks if picks else []      # strictly increasing ints
        self.first_ok  = first_ok                # valid if we draft first
        self.second_ok = second_ok               # valid if we draft second
        self.children  = []

    def copy(self):
        return Node(self.picks.copy(), self.first_ok, self.second_ok)

# ---------- recursive generator ----------
def _grow(node, max_pick):
    if len(node.picks) == max_pick:
        return
    depth     = len(node.picks) + 1          # 1-based index
    our_taken = depth - 1

    # ----- branch: we have first pick -----
    if node.first_ok:
        opp_before = our_taken if depth % 2 else our_taken + 1
        max_val = opp_before + 1 + our_taken
        start   = node.picks[-1] if node.picks else 0
        for v in range(start + 1, max_val + 1):
            c = node.copy()
            c.second_ok = False
            c.picks.append(v)
            node.children.append(c)
            _grow(c, max_pick)

    # ----- branch: we have second pick -----
    if node.second_ok:
        opp_before = our_taken + 1 if depth % 2 else our_taken
        max_val = opp_before + 1 + our_taken
        start   = node.picks[-1] if node.picks else 0
        for v in range(start + 1, max_val + 1):
            c = node.copy()
            c.first_ok = False
            c.picks.append(v)
            node.children.append(c)
            _grow(c, max_pick)

def _leaves(root):
    out, stack = [], [root]
    while stack:
        n = stack.pop()
        if n.children:
            stack.extend(n.children)
        else:
            out.append(n)
    return out

# ---------- public enumeration ----------
def enumerate_combos(max_pick, included=None, excluded=None):
    inc = set(included) if included else set()
    exc = set(excluded) if excluded else set()

    root = Node()
    _grow(root, max_pick)
    leaves = _leaves(root)

    table = {}     # seq-tuple -> (first_ok, second_ok, count)
    for n in leaves:
        if inc and not inc.issubset(n.picks): continue
        if exc and exc.intersection(n.picks): continue
        key = tuple(n.picks)
        if key not in table:
            table[key] = [n.first_ok, n.second_ok, 1]
        else:
            t = table[key]
            t[0] |= n.first_ok
            t[1] |= n.second_ok
            t[2] += 1
    return table

# ---------- helper ----------
def side_for(depth):            # depth is 1-based pick position
    if depth == 1:          return "first"
    return "second" if depth % 4 in (2, 3) else "first"

# ---------- single function Streamlit will call ----------
def run_analysis(max_pick, included, excluded, prefix_len):
    combos = enumerate_combos(max_pick, included, excluded)
    if not combos:
        return "No valid combinations", []

    # group by prefix
    groups = {}
    for seq, (f, s, _) in combos.items():
        if len(seq) < prefix_len:   continue
        pref = seq[:prefix_len]
        g = groups.setdefault(pref, [0,0,0])   # first, second, total
        if f: g[0] += 1
        if s: g[1] += 1
        g[2] += 1

    total = sum(v[2] for v in groups.values())
    rows  = []
    for pref, (f_cnt, s_cnt, tot) in sorted(groups.items()):
        rows.append({
            "Prefix":   pref,
            "Count":    tot,
            "Percent":  f"{tot/total*100:.1f}",
            "Possible": "both" if f_cnt and s_cnt else
                         "first" if f_cnt else "second"
        })
    header = f"{len(combos)} unique final combos after filters"
    return header, rows