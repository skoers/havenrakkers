# Ronja en de verdwenen melkwagen

Luisterverhaal voor groep 6 bij Faqta *Van boer tot piloot* (deel 1 tot en met 4). Alle belangrijke
woorden uit de samenvatting komen in het verhaal voor en worden in de dialoog uitgelegd: landbouw,
akkerbouw, glastuinbouw, veeteelt, piekseizoen, biologisch, industriële revolutie, kinderarbeid,
stoomtrein, industrie, technische industrie, transport, goederen, logistiek, luchtvaart, scheepvaart,
vracht, distributiecentrum, werkzaamheden, dienst, winst, donatie, ondernemer en Kamer van Koophandel.

## Wat de pagina doet
- Elf hoofdstukken, samen ongeveer een half uur. Ze spelen automatisch achter elkaar.
- De stem is vooraf opgenomen (Microsoft-stem "Colette" via edge-tts) en staat als m4a in `audio/`. Daardoor
  klinkt het op iPhone, iPad en computer hetzelfde, zonder stemmen te downloaden.
- De tekst loopt mee: de zin die klinkt licht op. Tik op een zin om daar te beginnen.
- Belangrijke woorden zijn blauw. Tik erop voor de uitleg van het blad, voorgelezen.
- Na elk hoofdstuk drie vragen. Zonder antwoord gaat het verhaal na 25 seconden vanzelf verder.
  De score wordt in de browser onthouden, net als waar je gebleven bent.
- Knop "Woorden" toont alle begrippen met uitleg.

## Tekst aanpassen
De tekst, vragen en uitleg staan in `verhaal.json`. Na een wijziging moet de audio opnieuw worden
opgenomen met `tools/gen_audio_edge.py` (vereist `pip install edge-tts numpy` en `ffmpeg`; het oude Piper-script `tools/gen_audio.py` vereist de Piper-stem
`nl_NL-pim-medium`, te downloaden uit de sherpa-onnx tts-models releases op GitHub):

    python3 tools/gen_audio_edge.py nl-NL-ColetteNeural audio
