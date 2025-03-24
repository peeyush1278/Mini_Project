from flask import Flask, render_template, jsonify, request
import speech_recognition as sr
from deep_translator import GoogleTranslator
import gtts
import pygame
import os
import threading


print("Current Working Directory: ", os.getcwd())
app = Flask(__name__)

# Initialize Pygame mixer
pygame.mixer.init()

recognizer = sr.Recognizer()
running = True

def listen_and_translate(input_lang, output_lang):
    i=0
    global running
    with sr.Microphone() as source:
        print("Listening...")
        while running:
            try:
                voice = recognizer.listen(source)
                text = recognizer.recognize_google(voice, language=input_lang)
                print(f"You said: {text}")

                # Use deep-translator for translation
                translation = GoogleTranslator(source='auto', target=output_lang).translate(text)
                print(f"Translated text: {translation}")
                i+=1

                # Convert the translated text to audio
                converted_audio = gtts.gTTS(translation, lang=output_lang)
                input_lang,output_lang= output_lang,input_lang
                audio_file = f"translation{i}.mp3"
                converted_audio.save(audio_file)

                # Load and play the audio file using pygame
                pygame.mixer.music.load(audio_file)
                pygame.mixer.music.play()

                # Wait until the audio is finished playing
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)

                # Optional: Remove the audio file after playing
                os.remove(audio_file)

            except sr.UnknownValueError:
                print("Sorry, I could not understand the audio.")
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")
            except Exception as e:
                print(f"An error occurred: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start')
def start():
    global running
    input_lang = request.args.get('inputLang', default='hi')  # Get input language from query parameters
    output_lang = request.args.get('outputLang', default='kn')  # Get output language from query parameters
    running = True
    threading.Thread(target=listen_and_translate, args=(input_lang, output_lang)).start()
    return jsonify({"status": "started", "inputLang": input_lang, "outputLang": output_lang})

@app.route('/stop')
def stop():
    global running
    running = False
    return jsonify({"status": "stopped"})

if __name__ == '__main__':
    app.run(debug=True)
    