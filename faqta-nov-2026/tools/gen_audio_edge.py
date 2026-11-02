"""Neemt het verhaal op met een Microsoft-stem via edge-tts (gratis, online).
Per hoofdstuk één m4a (zin voor zin opgenomen, met pauzes) plus timing.json met de starttijd van elke zin.
Gebruik: python3 tools/gen_audio_edge.py nl-NL-ColetteNeural audio   (pip install edge-tts numpy; ffmpeg nodig)"""
import json, re, sys, os, subprocess, asyncio, numpy as np, wave, tempfile
import edge_tts
VOICE, OUT = sys.argv[1], sys.argv[2]
RATE = '-8%'; SR = 24000; PROXY = os.environ.get('HTTPS_PROXY')
os.makedirs(OUT, exist_ok=True)
base = os.path.dirname(os.path.abspath(__file__)) + '/..'
d = json.load(open(f'{base}/verhaal.json', encoding='utf8'))
tmp = tempfile.mkdtemp()
sem = asyncio.Semaphore(4)

async def tts(text, name):
    """Spreekt een tekst uit en geeft de audio terug als int16-array (met stilte aan begin/eind weggeknipt)."""
    mp3 = f'{tmp}/{name}.mp3'
    for attempt in range(4):
        try:
            async with sem:
                await edge_tts.Communicate(text, VOICE, rate=RATE, proxy=PROXY).save(mp3)
            break
        except Exception as e:
            if attempt == 3: raise
            await asyncio.sleep(2 * (attempt + 1))
    raw = subprocess.run(['ffmpeg','-loglevel','error','-i',mp3,'-f','s16le','-ac','1','-ar',str(SR),'-'], capture_output=True, check=True).stdout
    a = np.frombuffer(raw, dtype=np.int16)
    idx = np.where(np.abs(a) > 250)[0]
    if len(idx): a = a[max(0, idx[0]-int(0.05*SR)):idx[-1]+int(0.1*SR)]
    return a

def split_sentences(p):
    return [x for x in re.split(r"(?<=[.!?])\s+(?=[A-Z'\"‘“Oa-z])", p) if x.strip()]

def write(a, path):
    wav = path + '.wav'
    with wave.open(wav, 'wb') as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes(a.astype(np.int16).tobytes())
    subprocess.run(['ffmpeg','-y','-loglevel','error','-i',wav,'-c:a','aac','-b:a','64k','-movflags','+faststart',path], check=True)
    os.remove(wav)

async def main():
    timing = []
    for ci, h in enumerate(d['hoofdstukken']):
        jobs = []
        for pi, p in enumerate(h['tekst']):
            for si, s in enumerate(split_sentences(p)):
                jobs.append((pi, si, s))
        audios = await asyncio.gather(*[tts(s, f'h{ci}-{k}') for k, (_, _, s) in enumerate(jobs)])
        chunks, sents, t = [np.zeros(int(0.3*SR), dtype=np.int16)], [], 0.3
        gap_s, gap_p = int(0.4*SR), int(0.85*SR)
        for (pi, si, s), a in zip(jobs, audios):
            sents.append({'p': pi, 's': si, 'text': s, 't': round(t, 2)})
            chunks += [a, np.zeros(gap_s, dtype=np.int16)]; t += (len(a) + gap_s) / SR
            if si == max(x[1] for x in jobs if x[0] == pi):
                chunks.append(np.zeros(gap_p - gap_s, dtype=np.int16)); t += (gap_p - gap_s) / SR
        audio = np.concatenate(chunks)
        write(audio, f'{OUT}/h{ci+1}.m4a')
        timing.append({'duur': round(len(audio)/SR, 2), 'zinnen': sents})
        print(f'hoofdstuk {ci+1}: {len(sents)} zinnen, {len(audio)/SR/60:.1f} min', flush=True)
        qa = await asyncio.gather(*[tts(q['v'], f'v{ci}-{qi}') for qi, q in enumerate(h['vragen'])])
        for qi, a in enumerate(qa): write(a, f'{OUT}/v{ci+1}-{qi+1}.m4a')
    wa = await asyncio.gather(*[tts(w['u'], f'w{k}') for k, w in enumerate(d['woorden'])])
    for w, a in zip(d['woorden'], wa):
        write(a, f"{OUT}/w-{re.sub(r'[^a-z0-9]+','-',w['w'].lower()).strip('-')}.m4a")
    extra = {'intro': f"{d['titel']}. {d['ondertitel']}.", 'goed': 'Goed zo!', 'fout': 'Helaas, probeer het nog eens.', 'einde': 'Dit was het verhaal. Goed geluisterd!'}
    ea = await asyncio.gather(*[tts(s, k) for k, s in extra.items()])
    for k, a in zip(extra, ea): write(a, f'{OUT}/{k}.m4a')
    json.dump(timing, open(f'{OUT}/timing.json', 'w'), ensure_ascii=False)
    print('klaar')
asyncio.run(main())
