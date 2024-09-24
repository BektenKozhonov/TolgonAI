from os import path
from pydub import AudioSegment

# files                                                                         
src = "D:\Projects\bot_voice_recognition\audio.mp3"
dst = "D:\Projects\bot_voice_recognitiontest.wav"

# convert wav to mp3                                                            
sound = AudioSegment.from_mp3(src)
sound.export(dst, format="wav")
