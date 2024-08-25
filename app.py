import streamlit as st
import speech_recognition as sr
import pyttsx3
import requests
import threading

# Initialize the recognizer and the text-to-speech engine
recognizer = sr.Recognizer()
tts_engine = pyttsx3.init()
txt = []

# Configure text-to-speech engine properties (optional)
tts_engine.setProperty('rate', 150)  # Speed of speech
tts_engine.setProperty('volume', 1)  # Volume level (0.0 to 1.0)

# Ollama API settings
OLLAMA_API_URL = "http://localhost:11434/api/generate"  # Replace with your endpoint

def listen():
    """Listen for a voice command and return the recognized text."""
    with sr.Microphone() as source:
        st.write("Listening...")
        audio = recognizer.listen(source)
    try:
        command = recognizer.recognize_google(audio)
        st.write(f"User said: {command}")
        return command
    except sr.UnknownValueError:
        st.write("Sorry, I did not understand that.")
        return None
    except sr.RequestError:
        st.write("Could not request results from the speech recognition service.")
        return None

def speak(text):
    """Speak the given text in a separate thread."""
    def _speak():
        tts_engine.say(text)
        tts_engine.runAndWait()
    threading.Thread(target=_speak).start()

def get_response_from_ollama(prompt):
    hist = ' '.join(txt)
    string = 'This is our previous conversation:' + (hist) + '  , The present question is:' + (prompt)
    
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "model": "phi3",
        "prompt": prompt
    }
    
    response = requests.post(OLLAMA_API_URL, json=data, headers=headers, stream=True)
    
    # Initialize an empty string to store the full response
    full_response = ""

    for line in response.iter_lines():
        if line:
            # Decode the line and load it as a JSON object
            line_json = line.decode('utf-8')
            try:
                response_json = requests.models.complexjson.loads(line_json)
                # Append each 'response' part to the full_response string
                full_response += response_json.get('response', '')
            except requests.exceptions.JSONDecodeError:
                st.write("Failed to decode line:", line_json)
    
    string2 = 'For this question :' + prompt + ', your answer was ' + full_response
    txt.append(string2)
    return full_response

def main():
    st.title("Voice Assistant")

    # Create a button to start listening
    if st.button('Start Listening'):
        command = listen()
        if command:
            if "stop" in command.lower():
                st.write("Stopping the assistant.")
                speak("Goodbye!")
            else:
                response = get_response_from_ollama(command)
                if response:
                    st.write(f"Assistant: {response}")
                    speak(response)

if __name__ == "__main__":
    main()
