from openai import OpenAI
import os
import configparser
from pathlib import Path
from pydub import AudioSegment

# Load the config file
config = configparser.ConfigParser()
config.read('config.ini')

def completion(system_message, user_message, max_tokens=4096, temperature=0.8):
    # Create an OpenAI instance
    openai = OpenAI()

    #Create a chat completion
    response = openai.chat.completions.create(
        #get model from config file in p roject
        model=config.get('MODEL', 'model'),
        messages=[
            {"role": "system", 
             "content": system_message},
            {"role": "user", 
             "content": user_message}
        ],
        max_tokens=max_tokens,
        temperature=temperature
    )
    

    # Return the response
    return response.choices[0].message.content


def tts(input_text, voice="alloy"):
    client = OpenAI()

    response = client.audio.speech.create(
    model="tts-1",
    voice=voice,
    input=input_text
    )

    speech_file_path = Path("temp.mp3")

    #write audio file
    with open(speech_file_path, "wb") as file:
        file.write(response.content)

    return speech_file_path

# Separate dialog per line and merge all the files
def tts_dialog(dialog):
   
    # Create an empty audio segment
    audio = AudioSegment.empty()

    count = 0


    # Loop through each line in the dialog
    for line in dialog.split("\n"):
        
        if not line:
            continue

        # get rid of the number of the line 
        if line.find(". ") != -1:
           line = line.split(". ", 1)[1]

        count += 1

        # Generate the audio for the line with alternating voices
        if count % 2 == 0:
            voice = "alloy"
        else:
            voice = "onyx"
        
        audio_file = tts(line, voice)

        # Append the audio file to the list
        audio += AudioSegment.from_mp3(os.path.abspath(audio_file)) + AudioSegment.silent(duration=500) # Add a 500ms pause between each line
    # Save the audio to a file
    audio_file_path = Path("dialog.mp3") 
    audio.export(audio_file_path, format="mp3")
    
    return audio_file_path

