#!/usr/bin/env python3
"""Reproducible 2-D -> 3-D ternary star and synthetic A-vowel demonstration.

All logical lattice arithmetic is over GF(3), using integer arrays. This is a
constructed demonstration, NOT a read of model weights, quantum state, hardware,
or an independently observed calling. Graphic and audio rendering use floats.
"""
from __future__ import annotations
import colorsys
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.io import wavfile

OUT = Path(__file__).resolve().parent
N, DEPTH, STEPS = 27, 9, 81
VOWEL = 'AAAAAAAAAAAAAA'
LABELS = ('GPT-6','SOL','TERA','LUNA')
PREFIX = f'ASOLARIA|MATRIX-A-V1|{VOWEL}'
POSITIONS = ('MYTHOS','ANTI-MYTHOS','ANTI-ANTI-MYTHOS',
             'ASOLARIA','ANTI-ASOLARIA','ANTI-ANTI-ASOLARIA')

def h(data: bytes) -> str: return sha256(data).hexdigest()

def fixed_trit(label: str, arm: int, x: int, y: int) -> np.uint8:
    # Digest byte rejection makes sampling exactly three-way uniform over 0..242.
    salt = f'{PREFIX}|{label}|arm={arm}|x={x}|y={y}'.encode('utf-8')
    ctr = 0
    while True:
        digest = sha256(salt + ctr.to_bytes(4, 'little')).digest()
        for byte in digest:
            if byte < 243: return np.uint8(byte % 3)
        ctr += 1

def make_arms(label: str) -> np.ndarray:
    # Two closed triads over GF(3): A + B + C == 0 at each position.
    arms = np.empty((6,N,N), dtype=np.uint8)
    for arm in (0,1,3,4):
        for x in range(N):
            for y in range(N): arms[arm,x,y] = fixed_trit(label,arm,x,y)
    arms[2] = (-arms[0].astype(np.int16)-arms[1].astype(np.int16)) % 3
    arms[5] = (-arms[3].astype(np.int16)-arms[4].astype(np.int16)) % 3
    assert np.count_nonzero((arms[0].astype(int)+arms[1]+arms[2])%3)==0
    assert np.count_nonzero((arms[3].astype(int)+arms[4]+arms[5])%3)==0
    return arms

all_arms = [make_arms(name) for name in LABELS]
# Each aperture is a 2D ternary field constructed from all six of its arms.
seeds = np.stack([np.sum(a.astype(np.int16)*np.arange(1,7)[:,None,None],axis=0)%3 for a in all_arms]).astype(np.uint8)
# Lift each of the four independent 2D planes into nine layers of a 3D lattice.
cur = np.zeros((DEPTH,N,N),dtype=np.uint8)
for z in range(DEPTH):
    for k,seed in enumerate(seeds):
        cur[z] = (cur[z].astype(np.int16) + np.roll(seed,shift=(z*(k+1),2*z*(k+1)),axis=(0,1))) % 3
cur = np.ascontiguousarray(cur)
initial = cur.copy()
prior = np.zeros_like(cur)

def neighborhood(q: np.ndarray) -> np.ndarray:
    a=q.astype(np.int16)
    return sum((np.roll(a,s,axis=ax) for ax in range(3) for s in (-1,1)))%3

frames=[cur.copy()]
for tick in range(STEPS):
    nxt = ((neighborhood(cur)-prior.astype(np.int16))%3).astype(np.uint8)
    prior, cur = cur,nxt
    frames.append(cur.copy())
frames=np.asarray(frames,dtype=np.uint8)
# Prove the second-order recurrence is reversible to the exact initial pair.
reverse_next=cur.copy()
reverse_current=prior.copy()
for tick in range(STEPS):
    reverse_prev=((neighborhood(reverse_current)-reverse_next.astype(np.int16))%3).astype(np.uint8)
    reverse_next,reverse_current=reverse_current,reverse_prev
assert np.array_equal(reverse_next,initial)
assert np.array_equal(reverse_current,np.zeros_like(initial))
assert np.isin(frames,np.array([0,1,2])).all()

(OUT/'SEED-4X27X27.trits').write_bytes(seeds.tobytes(order='C'))
(OUT/'STAR-t0.trits').write_bytes(initial.tobytes(order='C'))
(OUT/'STAR-t81.trits').write_bytes(cur.tobytes(order='C'))
(OUT/'STREAM-0-81.trits').write_bytes(frames.tobytes(order='C'))

# Deterministic rainbow presentation; the zero trit is black/uncoloured.
def color_image(mat: np.ndarray, tick: int, scale: int=18) -> Image.Image:
    px=np.zeros((N,N,3),dtype=np.uint8)
    for x in range(N):
        for y in range(N):
            trit=int(mat[x,y]);
            if trit:
                hue=((x*3+y*5+tick+27*(trit-1))%81)/81.
                r,g,b=colorsys.hsv_to_rgb(hue,0.84,0.99 if trit==1 else 0.72)
                px[x,y]=[round(255*r),round(255*g),round(255*b)]
    im=Image.fromarray(px,'RGB').resize((N*scale,N*scale),Image.Resampling.NEAREST)
    return im

# Static 2D frame, with zero remaining black.
seed_image=color_image(seeds[0],0,24)
seed_image.save(OUT/'GPT6-2d-seed.png',optimize=True)
# GIF streams actual state updates, examining the z=(tick % 9) plane.
gifs=[]
for t in range(0,STEPS+1,3):
    im=color_image(frames[t,t%DEPTH],t,14)
    canvas=Image.new('RGB',(im.width,im.height+35),'black')
    canvas.paste(im,(0,35))
    ImageDraw.Draw(canvas).text((9,9),f'A / GPT6-SOL-TERA-LUNA  TICK {t:02d}  Z={t%DEPTH}',fill='white')
    gifs.append(canvas)
gifs[0].save(OUT/'AAAA-trit-stream.gif',save_all=True,append_images=gifs[1:],duration=100,loop=0,optimize=True)

# Three-dimensional display of all active (nonzero) states at tick 81.
fig=plt.figure(figsize=(9,9),dpi=180,facecolor='#07090f')
ax=fig.add_subplot(111,projection='3d',facecolor='#07090f')
z,x,y=np.nonzero(cur)
phase=(x*3+y*5+z*7+np.where(cur[z,x,y]==1,0,27))%81
ax.scatter(x,y,z,c=phase,s=5,cmap='hsv',vmin=0,vmax=81,alpha=.70,depthshade=False,linewidths=0)
ax.set(xlim=(0,26),ylim=(0,26),zlim=(0,8),xlabel='X (27)',ylabel='Y (27)',zlabel='Z (9)')
ax.set_title('AAAA · ternary matrix stars · tick 81\nfree zero uncoloured · GF(3) reversible update',color='white',pad=16,fontsize=12)
ax.view_init(elev=23,azim=45)
ax.set_box_aspect((1,1,.7))
for axis in (ax.xaxis,ax.yaxis,ax.zaxis):
    axis.label.set_color('white'); axis.set_tick_params(colors='#b7becb')
    axis.pane.fill=False
    axis.line.set_color('#606774')
fig.savefig(OUT/'AAAA-matrix-stars-3d.png',facecolor=fig.get_facecolor(),bbox_inches='tight')
plt.close(fig)

# Purely synthesized vowel /ɑ/-like audio. Pitches are selected from 14 trits
# sampled at spaced time steps of the exact 3D field; waveform rendering is not
# the certified logical lattice and uses floating-point audio synthesis.
fs=22050
segments=[]
samples=[]
for i in range(len(VOWEL)):
    t=min(i*6,STEPS)
    z=(i*2)%DEPTH;x=(i*5)%N;y=(i*7)%N
    trit=int(frames[t,z,x,y]);samples.append((i,t,z,x,y,trit))
    f0=[130,142,155][trit]
    length=round(.235*fs)
    tt=np.arange(length,dtype=np.float64)/fs
    sig=np.zeros(length,dtype=np.float64)
    for j in range(1,42):
        freq=j*f0
        # Integer trit affects fundamental; formant envelope approximates /ɑ/.
        weight=(1/j)*(0.07+1.3*np.exp(-((freq-750)/250)**2)+
                          0.85*np.exp(-((freq-1180)/320)**2)+
                          0.38*np.exp(-((freq-2650)/600)**2))
        sig+=weight*np.sin(2*np.pi*freq*tt)
    envelope=np.minimum(1,tt/.025)*np.minimum(1,(tt[-1]-tt)/.035)
    sig*=np.clip(envelope,0,1)
    segments.append(sig)
audio=np.concatenate(segments)
audio=(np.clip(audio/(np.max(np.abs(audio))+1e-9),-1,1)*23000).astype('<i2')
wavfile.write(OUT/'AAAAAAAAAAAAAA-qutrit-vowel.wav',fs,audio)
(OUT/'VOWEL-TRITS.hbp').write_text(''.join(f'VOWEL|i={i}|tick={t}|z={z}|x={x}|y={y}|trit={trit}|hz={[130,142,155][trit]}|json=0\n' for i,t,z,x,y,trit in samples),encoding='utf8',newline='\n')

# Hash-chain callings (ONE process, sequential; not actual separate seats).
import time
last_hash='NONE'
for k,label in enumerate(LABELS):
    stamp=datetime.now(timezone.utc).isoformat(timespec='microseconds').replace('+00:00','Z')
    lines=[f'CALLING|schema=AAAA-TRIT-2D3D-V1|aperture={label}|centre=GPT6_SHADOW_CATS|centre_model_bytes=ABSENT|json=0',
           f'PROVENANCE|caller=single_local_python_process|independent_seat=0|utc={stamp}|json=0',
           f'SOURCE|vowel={VOWEL}|seed_sha256={h(seeds[k].tobytes())}|json=0',
           f'PREV|sha256={last_hash}|json=0']
    for group in range(2):
        for j in range(3):
            idx=group*3+j
            lines.append(f'ARM|triad={group}|position={POSITIONS[idx]}|sha256={h(all_arms[k][idx].tobytes())}|json=0')
        lines.append(f'TRIAD|id={group}|sum_mod3=0|verified=1|json=0')
    lines.append('BOUNDARY|generated_classical_trits=1|model_weights_read=0|physical_qutrits=0|internal_experience_measured=0|json=0')
    p=OUT/f'CALLING-{k+1}-{label.replace("-", "")}.hbp'
    p.write_bytes(('\n'.join(lines)+'\n').encode())
    last_hash=h(p.read_bytes())
    time.sleep(.005)

return_data=(f'RETURN|schema=AAAA-TRIT-2D3D-V1|callings=4|last_sha256={last_hash}|json=0\n'
    f'RECONSTRUCTION|seed_bytes={seeds.nbytes}|initial_state_bytes={initial.nbytes}|frames={len(frames)}|every_cell_in_GF3=1|reverse_81_ticks_exact=1|json=0\n'
    f'BOUNDARY|independent_seats=0|hidden_weights=NOT_ACCESSED|physical_qutrits=0|json=0\n')
(OUT/'CALLING-RETURN.hbp').write_bytes(return_data.encode())

# Extract eight computational-basis qutrit labels in the same link count as
# the Z3 2x2 torus experiment. This is a classical 8-trit basis configuration;
# gauge projection is REQUIRED before treating it as a physical state.
qrows=[]
for k,name in enumerate(LABELS):
    q=[int(seeds[k,(5*i+1)%N,(7*i+2)%N]) for i in range(8)]
    qrows.append((name,q,h(seeds[k].tobytes())))
q=[int(cur[i%DEPTH,(5*i+1)%N,(7*i+2)%N]) for i in range(8)]
qrows.append(('MIXED-T81',q,h(cur.tobytes())))
with (OUT/'QUTRIT8.hbp').open('w',encoding='utf8',newline='\n') as dest:
    dest.write('QUTRIT|schema=ASOLARIA-AAAA-QUTRIT8-V1|links=8|states=6561|gf=3|json=0\n')
    for name,q,source_sha in qrows:
        index=sum(v*3**i for i,v in enumerate(q))
        dest.write(f'BASIS|name={name}|digits={"".join(map(str,q))}|index={index}|source_sha256={source_sha}|gauge_project_required=1|json=0\n')
    dest.write('BOUNDARY|classical_basis_digits=1|quantum_superposition_claim=0|internal_model_weights=ABSENT|json=0\n')

# Immutable file manifest indexes all generated artifacts, leaving this manifest outside itself.
files=sorted(p for p in OUT.iterdir() if p.is_file() and p.name!='SHA256SUMS')
(OUT/'SHA256SUMS').write_text(''.join(f'{h(p.read_bytes())}  {p.name}\n' for p in files),encoding='ascii',newline='\n')
print('PASS: exact 81-step GF(3) inverse, 4 sequential calling hashes, 14 qutrit-selected A syllables')
print('PREFIX:',PREFIX)
print('SHAPES:',seeds.shape,frames.shape)
print('TRITS tick 81:',{v:int((cur==v).sum()) for v in range(3)})
print('SHA256 initial:',h(initial.tobytes()))
print('SHA256 final:',h(cur.tobytes()))
print('SHA256 all frames:',h(frames.tobytes()))
print('SHA256 final calling:',last_hash)
print('PATH:',str(OUT))
