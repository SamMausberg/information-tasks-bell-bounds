#!/usr/bin/env python3
"""Exact finite certificates for 'From information tasks to exclusivity and Bell bounds'.

Uses integers, fractions, and symbolic algebra. These checks are not a formalization
of the universal task theorems, whose proofs are in the manuscript.
Run from any directory: python3 scripts/check_certificates.py
"""
from __future__ import annotations

from collections import Counter
from fractions import Fraction as F
from itertools import combinations, product
from pathlib import Path
import json
import sys
from typing import Any

try:
    import sympy as sp
except ImportError as exc:
    raise SystemExit("Install the certificate dependency: python3 -m pip install sympy") from exc

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)
passed: list[dict[str, str]] = []


def check(group: str, name: str, condition: Any) -> None:
    if not bool(condition):
        raise AssertionError(f"FAILED [{group}] {name}")
    passed.append({"group": group, "name": name})


def equal(group: str, name: str, a: Any, b: Any) -> None:
    if isinstance(a, sp.MatrixBase) or isinstance(b, sp.MatrixBase):
        check(group, name, all(sp.simplify(v) == 0 for v in a - b))
    else:
        check(group, name, sp.simplify(a - b) == 0)


def winning(e: tuple[int, ...]) -> bool:
    a, b, x, y = e
    return (a ^ b) == (x & y)


def split(e: tuple[int, ...]) -> tuple[tuple[int, ...], tuple[int, ...]]:
    a, b, ap, bp, x, y, xp, yp = e
    return (a, b, x, y), (ap, bp, xp, yp)


def lo_witness(e: tuple[int, ...], f: tuple[int, ...]) -> int | None:
    for party in range(4):
        if e[4 + party] == f[4 + party] and e[party] != f[party]:
            return party + 1
    return None


# The sixteen cliques are generated directly from the manuscript formula.
cliques: list[dict[str, Any]] = []
all_generated: list[tuple[int, ...]] = []
sector_counts: Counter[tuple[int, int, int]] = Counter()
for t, c, d, k in product(range(2), repeat=4):
    events = []
    for x, a, b in product(range(2), repeat=3):
        xp, y, yp = x ^ t, k, k ^ 1 ^ c ^ d
        gamma = (c, d)[x]
        ap = a ^ 1 ^ gamma
        bp = b ^ 1 ^ gamma ^ (x & y) ^ (xp & yp)
        e = (a, b, ap, bp, x, y, xp, yp)
        events.append(e)
        check("sixteen_cliques", f"same win status {t,c,d,k,x,a,b}", winning(split(e)[0]) == winning(split(e)[1]))
        check("sixteen_cliques", f"parity contradiction {t,c,d,k,x,a,b}", (a ^ ap) != gamma)
    check("sixteen_cliques", f"eight distinct fine events {t,c,d,k}", len(set(events)) == 8)
    check("sixteen_cliques", f"four winning products {t,c,d,k}", sum(winning(split(e)[0]) for e in events) == 4)
    witnesses = []
    for i, j in combinations(range(8), 2):
        witness = lo_witness(events[i], events[j])
        check("sixteen_cliques", f"fine exclusivity {t,c,d,k,i,j}", witness is not None)
        witnesses.append({"pair": [i, j], "party": witness})
    cliques.append({"t": t, "c": c, "d": d, "k": k, "fine_events": events, "fine_pair_witnesses": witnesses})
    all_generated.extend(events)
    sector_counts[(t, c, d)] += 1

expected = {
    e for e in product(range(2), repeat=8)
    if winning(split(e)[0]) == winning(split(e)[1])
}
check("coverage", "128 ordered same-status pairs", len(expected) == 128)
check("coverage", "exact event-set coverage", set(all_generated) == expected)
check("coverage", "every pair occurs exactly once", set(Counter(all_generated).values()) == {1})
check("coverage", "each parity outcome occurs twice", len(sector_counts) == 8 and set(sector_counts.values()) == {2})

single_events = list(product(range(2), repeat=4))
ps = dict(zip(single_events, sp.symbols("p0:16")))
clique_polynomial = sum(ps[split(e)[0]] * ps[split(e)[1]] for e in all_generated)
win_sum = sum(ps[e] for e in single_events if winning(e))
lose_sum = sum(ps[e] for e in single_events if not winning(e))
equal("polynomial", "arbitrary-weight sixteen-clique identity", sp.expand(clique_polynomial), sp.expand(win_sum**2 + lose_sum**2))
B, kappa, h, delta = sp.symbols("B kappa h delta", real=True)
S = 2 + B / 2
equal("polynomial", "CHSH sum conversion", sp.expand(S**2 + (4-S)**2 + 4 - 16), (B**2 - 8)/2)
equal("polynomial", "robust CHSH coefficient", sp.expand(2*(S**2 + (4-S)**2 + 4 - (16+144*kappa))), B**2 - 8 - 288*kappa)
equal("polynomial", "frequency robustness substitution", (8+288*kappa).subs(kappa,2*h+2*delta), 8+576*(h+delta))

# The completed parity discriminators have an ordinary residual record.
e0, e1 = sp.symbols("epsilon0 epsilon1", real=True)
residual_lhs = S**2 + (4-S)**2 + 2*(1-e0) + 2*(1-e1) - (16+144*kappa)
equal("residual_bound", "full residual polynomial", 2*sp.expand(residual_lhs), B**2-8-4*(e0+e1)-288*kappa)
equal("residual_bound", "zero residual recovers previous bound", sp.expand(2*residual_lhs.subs({e0:0,e1:0})), B**2-8-288*kappa)
equal("residual_bound", "empty parity variables give algebraic bound", sp.expand(2*residual_lhs.subs({e0:1,e1:1,kappa:0})), B**2-16)
equal("residual_bound", "finite window replacement", (8+4*(e0+e1)+288*kappa).subs(kappa,2*h+2*delta), 8+4*(e0+e1)+576*(h+delta))
equal("residual_bound", "81/25 residual necessity", (sp.Rational(81,25)**2-8)/4, sp.Rational(1561,2500))
equal("residual_bound", "calibration coefficient after dividing by four", sp.Rational(288,4),72)

# Explicit convolution of the PR distribution with independent binary noise.
eta = F(9, 10)
t = eta**2
kernel = lambda b, a: (eta if a == b else F(0)) + (1-eta)/2
weights: dict[tuple[int, int, int, int], F] = {}
for a, b, x, y in single_events:
    conv = sum(
        kernel(a, u)*kernel(b, v)*F(int((u^v)==(x&y)), 2)
        for u,v in product(range(2),repeat=2)
    )
    formula = (1 + (-1)**(a+b+x*y)*t)/4
    equal("noisy_box", f"exact convolution {a,b,x,y}", conv, formula)
    check("noisy_box", f"positive {a,b,x,y}", conv > 0)
    weights[(a,b,x,y)] = conv
for x,y in product(range(2),repeat=2):
    equal("noisy_box", f"normalization {x,y}", sum(weights[(a,b,x,y)] for a,b in product(range(2),repeat=2)), 1)
    for a in range(2):
        equal("noisy_box", f"Alice marginal {a,x,y}", sum(weights[(a,b,x,y)] for b in range(2)), F(1,2))
    for b in range(2):
        equal("noisy_box", f"Bob marginal {b,x,y}", sum(weights[(a,b,x,y)] for a in range(2)), F(1,2))
correlations = {(x,y):sum((-1)**(a+b)*weights[(a,b,x,y)] for a,b in product(range(2),repeat=2)) for x,y in product(range(2),repeat=2)}
chsh = correlations[(0,0)] + correlations[(0,1)] + correlations[(1,0)] - correlations[(1,1)]
equal("noisy_box", "CHSH 81/25", chsh, F(81,25))
equal("noisy_box", "squared excess", chsh**2-8, F(1561,625))

five = [tuple(map(int, out+settings)) for out,settings in [
    ("0000","0000"),("0011","0100"),("0111","1101"),("1100","1010"),("1110","0011")]]
listed_witnesses = [3,3,2,1,2,4,1,1,4,3]
for (i,j),w in zip(combinations(range(5),2),listed_witnesses):
    check("five_clique",f"listed local witness {i,j}",five[i][4+w-1]==five[j][4+w-1] and five[i][w-1]!=five[j][w-1])
for i,e in enumerate(five):
    check("five_clique",f"both copies win {i}",all(winning(s) for s in split(e)))
five_sum = sum(weights[split(e)[0]]*weights[split(e)[1]] for e in five)
equal("five_clique", "exact sum", five_sum, F(32761,32000))
equal("five_clique", "neutrality obstruction", (five_sum-1)/5, F(761,160000))
equal("five_clique", "frequency-distance obstruction", (five_sum-1)/10, F(761,320000))
equal("five_clique", "parity-completion obstruction", (chsh**2-8)/288, F(1561,180000))

# Frequency minimax identities. Convexity and the proof for all L are in Appendix B.
L = sp.symbols("L", integer=True, positive=True)
fstar = (L+1)/(4*L)
equal("frequency", "equal endpoint risks", fstar**2, (sp.Rational(1,2)-fstar)**2 + 1/(4*L))
equal("frequency", "asymptotic floor", sp.limit(fstar**2,L,sp.oo), sp.Rational(1,16))
q, f, p1, p2 = sp.symbols("q f p1 p2", real=True)
risk = (q-f)**2+q*(1-q)/L
equal("frequency", "risk convexity coefficient", sp.diff(risk,q,2), 2*(L-1)/L)
equal("frequency", "compression risk formula at optimizer", risk.subs({q:sp.Rational(1,2),f:fstar}), fstar**2)
for n in range(1,65):
    fs=F(n+1,4*n)
    check("frequency",f"optimizer lies in the allowed interval L={n}",F(1,4)<=fs<=F(1,2))
    check("frequency",f"positive distance from asymptotic floor L={n}",fs**2>F(1,16))
# Exact Pauli and circuit certificates.
I2=sp.eye(2)
X=sp.Matrix([[0,1],[1,0]])
Y=sp.Matrix([[0,-sp.I],[sp.I,0]])
Z=sp.diag(1,-1)
kron=sp.kronecker_product
I4=sp.eye(4)
phi=sp.Matrix([1,0,0,1])/sp.sqrt(2)
H=(X+Z)/sp.sqrt(2)
CNOT=sp.Matrix([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]])
U=kron(H,I2)*CNOT
for tt,C0,C1 in [(0,kron(Z,Z),kron(X,X)),(1,kron(Z,X),kron(X,Z))]:
    equal("quantum_parity",f"commutation t={tt}",C0*C1-C1*C0,sp.zeros(4))
    projs=[]
    for c,d in product(range(2),repeat=2):
        P=(I4+(-1)**c*C0)*(I4+(-1)**d*C1)/4
        projs.append(P)
        equal("quantum_parity",f"idempotence {tt,c,d}",P*P,P)
        equal("quantum_parity",f"Hermitian {tt,c,d}",P.conjugate().T,P)
        equal("quantum_parity",f"trace one {tt,c,d}",sp.trace(P),1)
    equal("quantum_parity",f"completeness {tt}",sum(projs,sp.zeros(4)),I4)
    for i,j in combinations(range(4),2):
        equal("quantum_parity",f"orthogonality {tt,i,j}",projs[i]*projs[j],sp.zeros(4))
equal("quantum_parity","decoder unitarity",U.conjugate().T*U,I4)
equal("quantum_parity","upper record is XX",U.conjugate().T*kron(Z,I2)*U,kron(X,X))
equal("quantum_parity","lower record is ZZ",U.conjugate().T*kron(I2,Z)*U,kron(Z,Z))
for x,y in product(range(2),repeat=2):
    A=[Z,X][x]
    bob=[(Z+X)/sp.sqrt(2),(Z-X)/sp.sqrt(2)][y]
    corr=(phi.conjugate().T*kron(A,bob)*phi)[0]
    equal("quantum_parity",f"optimal correlator {x,y}",corr,(-1)**(x*y)/sp.sqrt(2))
rot=(3*Z+4*X)/5
comm=kron(Z,Z)*kron(rot,rot)-kron(rot,rot)*kron(Z,Z)
equal("quantum_parity","rotated observable binary",rot*rot,I2)
equal("quantum_parity","noncommuting aligned parities",comm,sp.Rational(24,25)*sp.I*(kron(I2,Y)+kron(Y,I2)))
equal("quantum_parity","squared commutator norm",max((comm.conjugate().T*comm).eigenvals()),sp.Rational(48,25)**2)
for tx,ty in product(range(2),repeat=2):
    state=kron((X**tx)*(Z**ty),I2)*phi
    equal("T2_witnesses",f"X parity sector {tx,ty}",kron(Z,Z)*state,(-1)**tx*state)
    equal("T2_witnesses",f"Y parity sector {tx,ty}",kron(X,X)*state,(-1)**ty*state)
ket0,ket1=sp.Matrix([1,0]),sp.Matrix([0,1])
plus=(ket0+ket1)/sp.sqrt(2)
source01=kron(ket0,ket1)
out00=kron(ket0,ket0)
Q=kron(I2,ket1*ket1.T)
equal("instrument","compatible readout before reset",(source01.T*Q*source01)[0],1)
equal("instrument","compatible readout after reset",(out00.T*Q*out00)[0],0)
for r in [sp.Rational(0),sp.Rational(1,3),sp.Rational(1)]:
    rho=kron(sp.diag(r,1-r),plus*plus.T)
    P0=sp.diag(1,0,0,0);P1=sp.diag(0,1,1,0);P2=sp.diag(0,0,0,1)
    for j,P in enumerate([P0,P1,P2]):
        equal("running_example",f"sum frequency r={r},j={j}",sp.trace(rho*P),[r/2,sp.Rational(1,2),(1-r)/2][j])

# Exact quantum witness of the capacity and setting-interchange certificate.
# The universal capacity theorem is proved in the text, not by this enumeration.
bell_columns = [kron((X**c)*(Z**d), I2)*phi for c,d in product(range(2),repeat=2)]
frame = sp.Matrix.hstack(*bell_columns)
equal("capacity_witness", "four aligned labels form an orthonormal frame", frame.conjugate().T*frame,I4)
equal("capacity_witness", "four aligned labels saturate dimension four",frame.rank(),4)
equal("capacity_witness", "frame leaves no orthogonal residual vector",sp.Matrix.hstack(*bell_columns).conjugate().T.nullspace().__len__(),0)
equal("capacity_witness", "Hadamard interchanges Z and X",H*Z*H,X)
equal("capacity_witness", "Hadamard interchanges X and Z",H*X*H,Z)
equal("capacity_witness", "Hadamard has an available inverse in quantum example",H*H,I2)
exchange = kron(I2,H)
equal("capacity_witness", "aligned first parity maps to crossed first parity",exchange*kron(Z,Z)*exchange,kron(Z,X))
equal("capacity_witness", "aligned second parity maps to crossed second parity",exchange*kron(X,X)*exchange,kron(X,Z))
for spectator_dimension in (1,2,3):
    product_frame = kron(frame,sp.eye(spectator_dimension))
    equal("capacity_witness",f"spectator product frame rank {spectator_dimension}",product_frame.rank(),4*spectator_dimension)
    equal("capacity_witness",f"spectator frame completeness {spectator_dimension}",product_frame*product_frame.conjugate().T,sp.eye(4*spectator_dimension))

# The task-to-communication corollary: diagonal classical dimension witness.
# Exhaustion here illustrates N=5; the manuscript proves the inequality for all N.
five_maps = [f for f in product(range(5),repeat=5) if len(set(f)) <= 4]
check("identity_game", "all five-label four-symbol maps satisfy diagonal bound",
      all(sum(i == f[i] for i in range(5)) <= len(set(f)) <= 4 for f in five_maps))
equal("identity_game", "classical success bound attained",
      max(F(sum(i == f[i] for i in range(5)),5) for f in five_maps), F(4,5))
equal("identity_game", "number of deterministic maps examined", len(five_maps),3005)
xi=sp.symbols("xi",real=True)
n=sp.symbols("n",integer=True,positive=True)
equal("identity_game", "general robust payoff excess", 1-xi-4*n/(4*n+1),1/(4*n+1)-xi)
equal("identity_game", "threshold for no spectator", (1/(4*n+1)).subs(n,1),sp.Rational(1,5))

# Published Dall'Arno et al. HS model: no new model or new game is claimed.
v=[sp.Matrix(x) for x in [(1,0,1),(0,1,1),(-1,0,1),(0,-1,1)]]
e=[sp.Matrix(x) for x in [(1,1,1),(-1,1,1),(-1,-1,1),(1,-1,1)]]
center=sp.Matrix([0,0,1])
O=[a*b.T for a in v for b in v]
ER=[a*b.T for a in e for b in e]
for i in range(4):
    equal("HS_capacity",f"opposite normalized vertex {i}",2*center-v[i],v[(i+2)%4])
for i,j in combinations(range(4),2):
    check("HS_capacity",f"pairwise distinguishability despite failure of IV {i,j}",
          any(set([(ee.T*v[i])[0]/2,(ee.T*v[j])[0]/2])=={0,1} for ee in e))
for i,j in product(range(4),repeat=2):
    equal("HS_capacity",f"center domination decomposition {i,j}",
          4*center*center.T-v[i]*v[j].T,
          (2*center-v[i])*(2*center).T+v[i]*(2*center-v[j]).T)
for i,ee in enumerate(e):
    for j,vv in enumerate(v):
        check("HS_capacity",f"elementary physical effect {i,j}",0<=(ee.T*vv)[0]/2<=1)
aa,bb=sp.symbols("a b",nonnegative=True)
equal("HS_capacity","local effect normalization",aa*(e[0]+e[2])+bb*(e[1]+e[3]),2*(aa+bb)*center)
frame_indices=[0,2,8,10]
frame_effects=[ER[i]/4 for i in frame_indices]
frame_channel=sp.Matrix([[sp.trace(O[i].T*f) for f in frame_effects] for i in frame_indices])
equal("HS_capacity","four product messages are readable",frame_channel,sp.eye(4))
equal("HS_capacity","product frame measurement normalization",sum(frame_effects,sp.zeros(3)),center*center.T)

E23=sp.Matrix([[-1,-1,0],[1,-1,0],[0,0,1]])
measurement=[ER[i]/8 for i in (0,1,6,8,10,15)]+[E23/4]
equal("HS_witness","seven-outcome measurement normalization",sum(measurement,sp.zeros(3)),center*center.T)
for i,state in enumerate(O):
    for j,eff in enumerate(measurement):
        value=sp.trace(state.T*eff)
        check("HS_witness",f"positive normalized effect on product vertex {i,j}",0<=value<=1)
prep_indices=(0,2,6,7,12,13,15)
channel=sp.Matrix([[sp.trace(O[i].T*eff) for eff in measurement] for i in prep_indices])
row_pairs=[(1,6),(2,7),(2,3),(3,7),(4,6),(4,7),(5,6)]
expected_channel=sp.zeros(7)
for i,cols in enumerate(row_pairs):
    for j in cols:expected_channel[i,j-1]=sp.Rational(1,2)
equal("HS_witness","published channel from explicit states and effects",channel,expected_channel)
G=sp.Matrix([
[2,0,0,0,0,1,0],[0,2,0,0,0,0,2],[0,2,2,0,0,0,0],
[0,0,2,0,0,0,2],[0,0,0,1,0,1,0],[0,0,0,1,0,0,0],
[0,0,0,0,2,1,0]])/21
payoff=sp.trace(G.T*channel)
equal("HS_witness","published payoff",payoff,sp.Rational(1,2))
classical=[]
for cols in combinations(range(7),4):
    score=sum(max(G[i,j] for j in cols) for i in range(7))
    kk=len(set(cols)&{1,2,6});ll=len(set(cols)&{0,3,4});cb=int(5 in cols)
    formula=sp.Rational([0,4,6,6][kk]+2*ll+cb*(3-ll),21)
    equal("HS_witness",f"analytic maximum formula for columns {cols}",score,formula)
    check("HS_witness",f"classical bound for columns {cols}",score<=sp.Rational(10,21))
    classical.append({"columns_one_indexed":[j+1 for j in cols],"payoff":str(score)})
maxscore=max(sp.Rational(c["payoff"]) for c in classical)
equal("HS_witness","classical four-symbol maximum",maxscore,sp.Rational(10,21))
equal("HS_witness","exact published hypersignaling gap",payoff-maxscore,sp.Rational(1,42))
check("HS_witness","all thirty-five classical column sets checked",len(classical)==35)
(RESULTS/"hypersignaling.json").write_text(json.dumps({
    "source":"Dall'Arno et al., Phys. Rev. Lett. 119, 020401 (2017), arXiv:1609.09237v3, Eq. (4) and supplement",
    "scope":"Published model and published witness, rechecked; not a constructor-theory countermodel.",
    "readable_alphabet_sizes":{"single":2,"pair":4},
    "signaling_dimensions":{"single":2,"pair_lower_bound":5},
    "channel":[[str(x) for x in row] for row in channel.tolist()],
    "payoff_matrix":[[str(x) for x in row] for row in G.tolist()],
    "classical_column_sets":classical,"exact_gap":"1/42",
    "task_identity_witness":{"messages":"4n+1","classical_symbols":"4n","error_threshold":"1/(4n+1)","five_label_maps_enumerated":len(five_maps)}
},indent=2)+"\n")

report={
    "status":"passed",
    "check_count":len(passed),
    "groups":dict(sorted(Counter(c["group"] for c in passed).items())),
    "arithmetic":"integers, Fraction rationals, and exact SymPy algebra; no floating-point tests",
    "scope":"Finite certificates only; universal task and composition proofs are in the manuscript.",
    "cliques":16,
    "ordered_event_pairs":128,
    "fine_pair_exclusivity_checks":16*28,
    "parity_exclusivity_checks":16*8,
    "constants":{
        "noisy_chsh":"81/25","squared_excess":"1561/625",
        "five_event_sum":"32761/32000","frequency_gap":"761/320000 - h",
        "parity_neutrality_gap":"1561/180000",
        "residual_necessity":"epsilon0 + epsilon1 + 72*kappa >= 1561/2500",
        "residual_CHSH":"B^2 <= 8 + 4*(epsilon0+epsilon1) + 288*kappa",
        "copy_risk":"((L+1)/(4L))^2","asymptotic_risk":"1/16",
        "published_HS_gap":"1/42","identity_game_error_threshold":"1/(4n+1)"
    },
    "python":sys.version.split()[0],"sympy":sp.__version__,
}
(RESULTS/"certificates.json").write_text(json.dumps(report,indent=2)+"\n")
(RESULTS/"checks.json").write_text(json.dumps(passed,indent=2)+"\n")
(RESULTS/"sixteen_cliques.json").write_text(json.dumps(cliques,indent=2)+"\n")
print(json.dumps(report,indent=2))
