"""Neemt het verhaal op met een Piper-stem.
Per hoofdstuk één mp3 (zin voor zin opgenomen, met pauzes), plus timing.json met de starttijd van elke zin.
Per belangrijk woord een mp3 met de uitleg. Gebruik: python3 tools/gen_audio.py <pad-naar-model.onnx> <uitvoermap>"""
import json, re, sys, os, subprocess, numpy as np, wave
from piper import PiperVoice
from piper.config import SynthesisConfig
model, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
voice = PiperVoice.load(model)
cfg = SynthesisConfig(length_scale=1.12)      # iets rustiger dan normaal
SR = voice.config.sample_rate
base = os.path.dirname(os.path.abspath(__file__)) + '/..'
d = json.load(open(f'{base}/verhaal.json', encoding='utf8'))

def tts(text):
    pcm = b''.join(c.audio_int16_bytes for c in voice.synthesize(text, cfg))
    a = np.frombuffer(pcm, dtype=np.int16)
    # stilte aan begin/eind wegknippen
    idx = np.where(np.abs(a) > 300)[0]
    if len(idx): a = a[max(0, idx[0]-int(0.05*SR)):idx[-1]+int(0.08*SR)]
    return a

def split_sentences(p):
    # splitsen op . ! ? gevolgd door spatie, maar niet binnen aanhalingstekens die direct doorlopen
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z'\"‘“Oa-z])", p)
    return [x for x in parts if x.strip()]

def write_mp3(a, path):
    wav = path + '.wav'
    with wave.open(wav, 'wb') as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes(a.astype(np.int16).tobytes())
    subprocess.run(['ffmpeg','-y','-loglevel','error','-i',wav,'-ac','1','-ar','22050','-b:a','56k',path], check=True)
    os.remove(wav)

timing = []
for ci, h in enumerate(d['hoofdstukken']):
    chunks, sents, t = [], [], 0.0
    gap_s, gap_p = int(0.45*SR), int(0.9*SR)
    chunks.append(np.zeros(int(0.3*SR), dtype=np.int16)); t += 0.3
    for pi, p in enumerate(h['tekst']):
        for si, s in enumerate(split_sentences(p)):
            a = tts(s)
            sents.append({'p': pi, 's': si, 'text': s, 't': round(t, 2)})
            chunks.append(a); t += len(a)/SR
            chunks.append(np.zeros(gap_s, dtype=np.int16)); t += gap_s/SR
        chunks.append(np.zeros(gap_p-gap_s, dtype=np.int16)); t += (gap_p-gap_s)/SR
    audio = np.concatenate(chunks)
    write_mp3(audio, f'{out}/h{ci+1}.mp3')
    timing.append({'duur': round(len(audio)/SR, 2), 'zinnen': sents})
    print(f'hoofdstuk {ci+1}: {len(sents)} zinnen, {len(audio)/SR/60:.1f} min', flush=True)
    # vragen voorlezen
    for qi, q in enumerate(h['vragen']):
        write_mp3(tts(q['v']), f'{out}/v{ci+1}-{qi+1}.mp3')
for w in d['woorden']:
    slug = re.sub(r'[^a-z0-9]+', '-', w['w'].lower()).strip('-')
    write_mp3(tts(w['u']), f'{out}/w-{slug}.mp3')
for k, s in {'intro': f"{d['titel']}. {d['ondertitel']}.", 'goed': 'Goed zo!', 'fout': 'Helaas, probeer het nog eens.', 'einde': 'Dit was het verhaal. Goed geluisterd!'}.items():
    write_mp3(tts(s), f'{out}/{k}.mp3')
json.dump(timing, open(f'{out}/timing.json', 'w'), ensure_ascii=False)
print('klaar')
