import speech_recognition as sr 
from time import ctime
import playsound
import os
import random
from gtts import gTTS

r = sr.Recognizer()

def record_audio(ask=False):
    with sr.Microphone() as source:
        if ask:
            bot_speak(ask)
        audio = r.listen(source)
        voice_data = r.recognize_google(audio)
        voice_data = ''
        try:
            voice_data = r.recognize_google(audio)
            #print(voice_data)
        except sr.UnknownValueError:
            bot_speak('Sorry, I did not get that')
        except sr.RequestError:
            bot_speak('Sorry, my speech service is down')
        return voice_data

def bot_speak(audio_string):
    tts = gTTS(text=audio_string, lang='en')
    r = random.randint(1, 10000000)
    audio_file = 'audio-' + str(r) + '.mp3'
    tts.save(audio_file)
    playsound.playsound(audio_file)
    print(audio_string)
    os.remove(audio_file)

def respond(voice_data):
    if 'physics' in voice_data:
        bot_speak('no youre fucked')

bot_speak('hi im monkey')


voice_data = record_audio()
respond(voice_data)
#print(voice_data)


 