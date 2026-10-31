# Proposed finite Yang–Mills integration: Cantor-driven response control

**PROPOSAL ONLY — no finite Yang–Mills source or claims modified.** Source artifact: `cantor27/CANTOR-729-TRITS.bin`, with immutable hash in `cantor27/SHA256SUMS`. It has 729 trits indexed by `t=0,...,728`; 64 trits are 1 or 2 and 665 are 0. The alphabet is GF(3), so the trit 2 represents -1 **only if** the target physics experiment defines a signed coupling map.

## Define an actual physical experiment

Begin with the existing gauge-invariant finite-volume Hamiltonian (in its reduced Gauss-invariant orbit basis):

```text
H0(r) = E + r M
H_t(r,lambda) = H0(r) + lambda f(c_t) W
```

where `W` is a **preselected gauge-invariant Wilson-loop or other physical observable** and `f(0)=0`, `f(1)=+1`, `f(2)=-1` (or another mapping registered before any measurements). If `W` does not commute with Gauss generators `G_v`, reject the driven Hamiltonian. Do not confuse this with the separate GF(3) cellular automaton `X[t+1]=L(X[t])-X[t-1]+F_t mod 3`.

For a **unitary quantum** test, use an actual time-evolution method, e.g.

```text
U_t = exp(-i Δt H_t / ħ)
psi_729 = U_728 ... U_1 U_0 psi_0
```

and test `U_t† U_t = I` to specified certified precision or implement a separate exact algebraic finite-circuit scheme. The **inverse experiment** uses the reverse ordered `U_t†`, not the automaton's inverse recurrence. A matrix-jump optimization may only be used if its composition law is proven for the exact driven operator sequence.

## Proposed independent acceptance gates

1. Freeze the input SHA-256, source commit, 729-slot index order, `f` mapping, `r`, `lambda`, `Δt`, `W`, sector, state and numerical bounds before execution.
2. On the 243-state Z3 physical sector, independently verify Gauss invariance, Hermiticity under the correct orbit weights, and that the driven evolution preserves norm (within a rigorously stated tolerance).
3. Verify the untouched spectrum of the **static** `H0(r)` with the existing exact `sturmfast` results, including 9 flat states below 16 where the preregistered thresholds apply. Never label the time-driven response as a static spectral gap.
4. Independently replay the same 729 slots with another implementation. Compare expectation values `<W>`, transition probabilities and final-state overlap within predeclared bounds; log mismatches or timeouts as such.
5. Null controls: all-zero drive, drive permutation (same pulse counts but different order), pulse-sign inversion, and independently seeded pulse positions. Check for accidental time-order dependence, symmetry breaking or trivial cancellation.
6. Register all resulting PASS/FAIL outcomes as new HBP/HBI + SHA receipts; do not change existing sealed Z1–Z6 or original finite Yang–Mills certifiers.

## What this cannot establish

A response at a finite number of 27-second sample slots does **not** prove a positive mass gap uniform in lattice size or in the continuum limit. The 27 seconds are an arbitrary signal duration and are not an experimentally calibrated field-theory time. The classical eight-trit candidate `02100210` is not automatically Gauss-invariant and cannot be directly equated to a trained qutrit state.

The most defensible initial result would be **a deterministic sparse-drive stress test of the existing finite matrix solver and gauge-invariant propagator**.
