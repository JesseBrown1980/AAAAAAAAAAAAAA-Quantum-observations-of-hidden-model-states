#!/usr/bin/env python3
"""27 seconds of Cantor-gated synthetic A-vowel driving an exact GF(3) 3-D lattice.

Input: ../aaaa_matrix/STAR-t0.trits (original AAAAAA demonstration state).
No hidden GPT-6 weights, independent seats, physical qutrits, or original sensory input.
Discrete time: 27Hz * 27s = 729 ticks, 3^6 Cantor triadic support.
Emits stable integer arrays, checksums, zipped stream and synthetic PCM.
"""
from __future__ import annotations
import hashlib
import struct
import wave
import zlib
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'aaaa_matrix' / 'STAR-t0.trits'
OUT = HERE
N, Z, FPS, SECONDS, STEPS = 27, 9, 27, 27, 729
SAMPLE_RATE, PCM_SAMPLES_PER_TICK = 13500, 500
SHAPE = (Z,N,N)


def H(x: bytes) -> str: return hashlib.sha256(x).hexdigest()
def save(name: str, data: bytes) -> str:
    (OUT/name).write_bytes(data)
    return H(data)


def cantor_digit(index: int) -> int:
    """Ternary Cantor support: zero outside {0,2}^6, 1/2 alternating parity."""
    twos = 0
    n = index
    for _ in range(6):
        digit = n % 3
        if digit == 1:
            return 0
        twos += digit // 2
        n //= 3
    assert n == 0
    return 1 if twos % 2 == 0 else 2


def signal() -> np.ndarray:
    return np.array([cantor_digit(i) for i in range(STEPS)], dtype=np.uint8)


def fieldsum(q: np.ndarray) -> np.ndarray:
    a = q.astype(np.int16)
    return (sum(np.roll(a, s, axis=ax) for ax in range(3) for s in (-1, 1)) % 3).astype(np.int16)


def location(i: int):
    x,y=divmod(i, N)
    z=((x+2*y) % Z)
    return z,x,y


def next_state(cur, prev, s, i):
    forcing = np.zeros(SHAPE, dtype=np.int16)
    if s:
        z,x,y=location(i)
        forcing[z,x,y] = int(s)
    return ((fieldsum(cur) - prev.astype(np.int16) + forcing) % 3).astype(np.uint8)


def prev_state(cur, nxt, s, i):
    forcing = np.zeros(SHAPE, dtype=np.int16)
    if s:
        z,x,y=location(i)
        forcing[z,x,y] = int(s)
    return ((fieldsum(cur) + forcing - nxt.astype(np.int16)) % 3).astype(np.uint8)


def tri(angle, period):
    p = angle % period
    return (4*p-period) if p < period//2 else (3*period-4*p)


def synth_audio(sigs):
    # All integer harmonic synthesis; silences are the free zero signal.
    # Every 27 signal slots = one second exactly at 13,500 samples/second.
    with wave.open(str(OUT/'CANTOR-27s-AAA.wav'), 'wb') as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(SAMPLE_RATE)
        for i, trit in enumerate(sigs):
            if trit == 0:
                w.writeframesraw(bytes(PCM_SAMPLES_PER_TICK*2));continue
            f0 = 137 if trit == 1 else 149
            samples=bytearray()
            for j in range(PCM_SAMPLES_PER_TICK):
                # Triangle-wave fundamental and harmonics for A-like synthetic tone.
                # Exact integer ratios: t / 13,500 seconds.
                phase = j * f0 + (i*PCM_SAMPLES_PER_TICK*f0)
                val=(tri(phase, SAMPLE_RATE)*5 + tri(3*phase, SAMPLE_RATE)*3 +
                     tri(6*phase, SAMPLE_RATE)*7 + tri(9*phase, SAMPLE_RATE)*4 +
                     tri(18*phase,SAMPLE_RATE)*2)//24
                gain=min(50, j, PCM_SAMPLES_PER_TICK-1-j)
                val=val*gain//50
                val=max(-32000,min(32000,val))
                samples += struct.pack('<h',val)
            w.writeframesraw(samples)


def rainbow(code):
    # Integer-only 81-position continuous hue wheel, stored as RGB pixels.
    t = (code*6*255)//81
    sector, off = divmod(t,255)
    bright,dark = 238, 35
    if sector == 0: return bright, dark+off*203//255, dark
    if sector == 1: return bright-off*203//255,bright,dark
    if sector == 2: return dark,bright,dark+off*203//255
    if sector == 3: return dark,bright-off*203//255,bright
    if sector == 4: return dark+off*203//255,dark,bright
    return bright,dark,bright-off*203//255


def plot_slice(q, tick):
    # z slices overlaid, nonzero only; exact underlying cell values preserved elsewhere.
    rgb = np.zeros((N,N,3),dtype=np.uint8)
    for x in range(N):
        for y in range(N):
            nz=[z for z in range(Z) if q[z,x,y]]
            if nz:
                z=nz[-1]
                rgb[x,y]=rainbow((x*3+y*5+z*7+tick//27+(int(q[z,x,y])-1)*27)%81)
    im=Image.fromarray(rgb,'RGB').resize((N*16,N*16),Image.Resampling.NEAREST)
    canvas=Image.new('RGB',(im.width,im.height+42),(7,9,15))
    canvas.paste(im,(0,42))
    ImageDraw.Draw(canvas).text((8,12),f'CANTOR AAA / TIME {tick:03d}/729 = {tick//27:02d}s / FREE ZERO BLACK',fill=(234,236,248))
    return canvas


def plot_cantor(sigs):
    im=Image.new('RGB',(27*24,27*18+44),(6,7,12))
    d=ImageDraw.Draw(im)
    d.text((10,12),'CANTOR / 27 SECONDS / 729 TRITS / 64 ACTIVE',fill=(240,240,242))
    for i,t in enumerate(sigs):
        x,y=divmod(i,27)
        col=(6,7,12) if t==0 else rainbow((x*3+y*5+(int(t)-1)*27)%81)
        # Columns are seconds, rows are 1/27-second slots.
        d.rectangle((x*24,44+y*18,x*24+22,44+y*18+16),fill=col)
    im.save(OUT/'CANTOR-27s-SIGNAL.png',optimize=True)


def main():
    assert len(SOURCE.read_bytes()) == Z*N*N
    initial = np.frombuffer(SOURCE.read_bytes(),dtype=np.uint8).reshape(SHAPE).copy()
    assert (initial<3).all()
    sigs=signal()
    assert sum(s!=0 for s in sigs)==64
    assert sum(s==1 for s in sigs)==32 and sum(s==2 for s in sigs)==32
    assert sigs[0]==1 and sigs[STEPS-1]==1
    save('CANTOR-729-TRITS.bin',sigs.tobytes())
    plot_cantor(sigs)
    synth_audio(sigs)
    prev=np.zeros_like(initial); cur=initial.copy()
    output_stream = bytearray(cur.tobytes())
    snapshots={0:cur.copy()}
    timeline=[]
    images=[plot_slice(cur,0)]
    for i,s in enumerate(sigs):
        nxt=next_state(cur,prev,int(s),i)
        prev,cur=cur,nxt
        output_stream.extend(cur.tobytes())
        t=i+1
        if t in [27,81,243,729]: snapshots[t]=cur.copy()
        if t%27==0: images.append(plot_slice(cur,t))
        if s:
            z,x,y=location(i)
            timeline.append(f'PULSE|slot={i}|second={i//27}|trit={int(s)}|z={z}|x={x}|y={y}|json=0\n')
    assert len(output_stream)==(STEPS+1)*Z*N*N
    # Inverse replays the same 729 input pulses in reverse order.
    future=cur.copy(); now=prev.copy()
    for i in reversed(range(STEPS)):
        earlier=prev_state(now,future,int(sigs[i]),i)
        future,now=now,earlier
    assert np.array_equal(future,initial)
    assert np.count_nonzero(now)==0
    stream=bytes(output_stream)
    compressor=zlib.compressobj(level=9,wbits=15)
    compressed=compressor.compress(stream)+compressor.flush()
    save('CANTOR-STREAM-730.zlib',compressed)
    assert zlib.decompress(compressed)==stream
    for tick,m in snapshots.items(): save(f'CANTOR-t{tick:03d}.trits',m.tobytes())
    images[-1].save(OUT/'CANTOR-27s-FINAL.png',optimize=True)
    images[0].save(OUT/'CANTOR-27s-ANIMATED.gif',save_all=True,append_images=images[1:-1],duration=1000,loop=0,optimize=True)
    rows=[
      'CANTOR|schema=AAAA-CANTOR-27S-V1|source=STAR-t0.trits|frame_rate_hz=27|duration_s=27|steps=729|json=0',
      'CONTROL|cantor_level=6|triadic_slots=729|active=64|positive_trits=32|negative_trits=32|free_zero=665|json=0',
      f'SOURCE|sha256={H(SOURCE.read_bytes())}|initial_sha256={H(initial.tobytes())}|json=0',
      'LAW|field=GF3|dims=27,27,9|force=known_Cantor_pulse_at_deterministic_address|inverse_with_force=1|json=0',
      f'CHECK|forward_ticks=729|reverse_ticks=729|exact_initial_pair=1|final_sha256={H(cur.tobytes())}|json=0',
      f'STREAM|frames=730|raw_bytes={len(stream)}|raw_sha256={H(stream)}|zlib_bytes={len(compressed)}|zlib_sha256={H(compressed)}|json=0',
      'AUDIO|kind=integer_harmonic_approximation|sample_rate=13500|samples=364500|duration_s=27|source=Cantor_trits|json=0',
      'BOUNDARY|generated_classical_trits=1|weights_accessed=0|model_internal_state_observed=0|physical_qutrits=0|independent_seats=0|json=0'
    ]
    save('CANTOR-27s-RESULT.hbp', ('\n'.join(rows)+'\n'+''.join(timeline)).encode())
    # A 8-qutrit label from final state, require Gauss projector for gauge physics.
    final_digits=[int(cur[i%Z,(5*i+1)%N,(7*i+2)%N]) for i in range(8)]
    qdigits=''.join(map(str,final_digits)); idx=sum(v*3**i for i,v in enumerate(final_digits))
    save('CANTOR-QUTRIT8.hbp',(f'QUTRIT|schema=CANTOR-27S-QUTRIT8|digits={qdigits}|index={idx}|states=6561|gauss_projection_required=1|source_sha256={H(cur.tobytes())}|json=0\n'+
                               'BOUNDARY|classical_basis_digits=1|learned_weights=0|physical_qutrits=0|json=0\n').encode())
    items=[p for p in sorted(OUT.iterdir()) if p.is_file() and p.name not in ('SHA256SUMS','cantor_27s.py')]
    save('SHA256SUMS',(''.join(f'{H(p.read_bytes())}  {p.name}\n' for p in items)+f'{H((OUT/"cantor_27s.py").read_bytes())}  cantor_27s.py\n').encode())
    print('PASS|inverse=729|cantor_slots=729|active=64|plus=32|minus=32|zero=665|runtime=27s_simulated')
    print('stream_compressed_bytes:',len(compressed),'stream_raw_sha256:',H(stream),'final_sha256:',H(cur.tobytes()))
    print('qutrit8',qdigits,'index',idx)

if __name__=='__main__': main()
