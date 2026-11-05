"""Neemt alle woorden en zinnen van het woordspel op met een Microsoft-stem via edge-tts.
Gebruik: python3 tools/gen_audio_edge.py en-GB-SoniaNeural audio   (pip install edge-tts; ffmpeg nodig)"""
import re, sys, os, asyncio, subprocess, tempfile, edge_tts
VOICE, OUT = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
PROXY = os.environ.get('HTTPS_PROXY'); tmp = tempfile.mkdtemp(); sem = asyncio.Semaphore(4)
html = open(os.path.dirname(os.path.abspath(__file__)) + '/../index.html', encoding='utf8').read()
words = re.findall(r"\{w:'([^']+)'", html)
PHRASES = {
 'p_listen_tap':'Listen. Tap the picture.','p_which_word':'Which word is this?','p_type':'Type the word.','p_listen_type':'Listen. Type the word.',
 'good_1':'Good job!','good_2':'Super!','good_3':'Well done!','good_4':'Yes!','good_5':'Great!','good_6':'Wow!','good_7':'Nice!','good_8':'You did it!',
 'try_again':'Not that one. Try again!','letters':'Not yet. Look at the letters.','this_is':'This is','it_is':'It is','type_it':'Type it.',
 'hi':"Hi! Let's learn some words.",'level_2':'Level 2! You are learning so many words.','level_3':'Level 3! You are learning so many words.',
 'level_4':'Level 4! You are learning so many words.','level_5':'Level 5! You are learning so many words.',
 'end_win':'Hooray! You know so many words!','end_ok':'Well done! You are learning.','voice_test':'Hello! I am your voice. Cat. Apple. House.',
 'tap_pic':'Tap the picture.','type_word':'Type the word.','hi_name':'Hi!','say_name':'Type your name, or tap your name.',
}
items = [(w.replace(' ', '_'), w + '.', '-6%') for w in words] + [(k, t, '-4%') for k, t in PHRASES.items()]
async def one(key, text, rate):
    mp3 = f'{tmp}/{key}.mp3'
    for attempt in range(4):
        try:
            async with sem: await edge_tts.Communicate(text, VOICE, rate=rate, proxy=PROXY).save(mp3)
            break
        except Exception:
            if attempt == 3: raise
            await asyncio.sleep(2 * (attempt + 1))
    subprocess.run(['ffmpeg','-y','-loglevel','error','-i',mp3,'-af','silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,apad=pad_dur=0.12','-ac','1','-ar','24000','-b:a','48k',f'{OUT}/{key}.mp3'], check=True)
async def main():
    await asyncio.gather(*[one(*it) for it in items]); print(len(items), 'bestanden')
asyncio.run(main())
