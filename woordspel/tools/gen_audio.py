import json, re, sys, wave, subprocess, os
from piper import PiperVoice
voice_name=sys.argv[1]; out=sys.argv[2]; os.makedirs(out,exist_ok=True)
model=[p for p in subprocess.run(['find','voices','-name',voice_name+'.onnx'],capture_output=True,text=True).stdout.split()][0]
v=PiperVoice.load(model)
html=open('/home/user/havenrakkers/woordspel/index.html',encoding='utf8').read()
words=re.findall(r"\{w:'([^']+)'",html)
PHRASES={
 'p_listen_tap':'Listen. Tap the picture.','p_which_word':'Which word is this?','p_type':'Type the word.','p_listen_type':'Listen. Type the word.',
 'good_1':'Good job!','good_2':'Super!','good_3':'Well done!','good_4':'Yes!','good_5':'Great!','good_6':'Wow!','good_7':'Nice!','good_8':'You did it!',
 'try_again':'Not that one. Try again!','letters':'Not yet. Look at the letters.','this_is':'This is','it_is':'It is','type_it':'Type it.',
 'hi':"Hi! Let's learn some words.",'level_2':'Level 2! You are learning so many words.','level_3':'Level 3! You are learning so many words.',
 'level_4':'Level 4! You are learning so many words.','level_5':'Level 5! You are learning so many words.',
 'end_win':'Hooray! You know so many words!','end_ok':'Well done! You are learning.','voice_test':'Hello! I am your voice. Cat. Apple. House.',
 'tap_pic':'Tap the picture.','type_word':'Type the word.','hi_name':'Hi!','say_name':'Type your name, or tap your name.',
}
items=[(w.replace(' ','_'),w+'.') for w in words]+list(PHRASES.items())
for key,text in items:
    wav=f'{out}/{key}.wav'
    with wave.open(wav,'wb') as wf: v.synthesize_wav(text,wf)
    subprocess.run(['ffmpeg','-y','-loglevel','error','-i',wav,'-af','silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,apad=pad_dur=0.15','-ac','1','-ar','22050','-b:a','48k',f'{out}/{key}.mp3'],check=True)
    os.remove(wav)
print(len(items),'bestanden')
