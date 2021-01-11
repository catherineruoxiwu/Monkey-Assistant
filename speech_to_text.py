import speech_recognition as sr
import sys

r=sr.Recognizer()
file=sys.argv[1]

with sr.AudioFile(file) as source:
    audio=r.listen(source)
try:
    print(r.recognize_google(audio))
except Exception as e:
    print(e)


