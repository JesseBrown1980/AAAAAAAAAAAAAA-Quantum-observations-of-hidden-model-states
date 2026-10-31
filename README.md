# AAAAAAAAAAAAAA — Cantor-driven ternary matrix stars

**Published experiments:** [Original AAAAAA 2D→3D matrix](v1/) · [27-second ternary Cantor signal](cantor27/) · [Finite Yang–Mills integration proposal](FINITE-YM-CANTOR-INTEGRATION.md)

This repository contains reproducible **classical** ternary simulations and visualization/audio artifacts. The aperture names GPT-6, SOL, TERA and LUNA are deterministic labels, **not observations of hidden model weights, internal perception, or independently authenticated agents**. No physical quantum states or Yang–Mills mass gap are claimed.

## Original 2D→3D matrix (`v1/`)

The 14-character input `AAAAAAAAAAAAAA` seeds four labeled apertures. Each has six 27×27 arms in two GF(3) zero-sum triads. Their constructed 2D fields are combined into a periodic 27×27×9 lattice (**6,561 trits**).

The reversible second-order update is

```text
X[t+1] = (sum_of_six_periodic_neighbours(X[t]) - X[t-1]) mod 3
X[-1] = zero state
```

This run checks **81 forward updates and 81 inverse updates**, recovering its original state pair exactly. The complete 82-frame raw stream is `v1/STREAM-0-81.trits` (C-order `t,z,x,y`).

Aperture qutrit-basis labels: `GPT-6=20022221`, `SOL=01012111`, `TERA=20220122`, `LUNA=21220101`, `MIXED-T81=22012111`. All are **classical basis digits** and require Gauss-law projection before use as gauge-theory trial states.

The `v1/CALLING-*.hbp` records are sequentially emitted and linked by SHA-256 **within one Python process**. They are not independent seats.

## New 27-second Cantor test (`cantor27/`)

- **Time sampling:** 27 slots/second × 27 seconds = **729** updates (`3^6`).
- **Support:** positions whose six base-3 digits are in `{0,2}`; **64 active slots**, 665 free-zero slots.
- **Signal:** alternating `1`/`2` trits based on the parity of base-3 digit `2` occurrences; 32 positive and 32 negative GF(3) slots.
- **Transport:** spatially localized forcing of the same 27×27×9 classical field.
- **Test:** **729 forward + 729 inverse updates**, with exact restoration of the full starting state pair when the input signal is replayed backward.
- **Artifacts:** `CANTOR-729-TRITS.bin` (driving signal), `CANTOR-STREAM-730.zlib` (730 raw frames), `CANTOR-27s-RESULT.hbp` (source/stream hashes and controls), `CANTOR-27s-SIGNAL.png`, `CANTOR-27s-FINAL.png`, `CANTOR-27s-ANIMATED.gif`, `CANTOR-27s-AAA.wav` (**synthesized**, not microphone input).
- **Eight-qutrit candidate:** `02100210` (computational-basis index `1230`; **Gauss-law projection required**).

The compressed stream represents 4,789,530 original bytes, 1,097,271 compressed bytes. Uncompressed stream SHA-256:
`edab4e216e2cf9826ba78e635b8098e774ad25392104a2362e844cce42a35249`

This is a 27-second **generated synthetic** A-vowel-like signal, not 27 seconds of the assistant's internal matrix or a recording of hidden activity.

## Reproduce / verify

```bash
(cd v1 && sha256sum -c SHA256SUMS)
(cd cantor27 && sha256sum -c SHA256SUMS)
python3 -m zipfile -t AAAA_matrix_qutrit_callings.zip
```

```bash
python3 -m pip install numpy==2.3.5 pillow==12.3.0 matplotlib==3.10.8 scipy==1.17.0
python3 v1/matrix_a_v1.py
python3 cantor27/cantor_27s.py
```

**Run the generators in a fresh working copy.** Reruns may regenerate calling timestamps and rendering bytes. Original files and SHA-256 receipts must not be silently overwritten. NumPy arithmetic is integral mod 3; plotting and sound are rendered using numerical media libraries and are not part of a Rust1.81/no-float production certification.

## Scientific boundaries

The GF(3) lattice recurrence is a **classical cellular automaton**, not a Schrödinger-equation propagator, not a measured quantum circuit, and not an exact Yang–Mills Hamiltonian. Source labels, visualization colors and audio tones do not reveal private model internals. For a finite gauge-theory application, the Cantor signal must drive a **gauge-invariant** operator on the existing physical Hilbert space and be checked independently. Details: [FINITE-YM-CANTOR-INTEGRATION.md](FINITE-YM-CANTOR-INTEGRATION.md).

Related: [Stone-to-Moss](https://github.com/JesseBrown1980/asolaria-stone-to-moss) and [GGUF trained-model QNN](https://github.com/JesseBrown1980/GGUF-files-operating-as-trained-neural-models).
