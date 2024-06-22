import os
import azure.cognitiveservices.speech as speech_sdk

from dotenv import load_dotenv

def synthesis_callback(evt):
    """
    Callback function to handle speech synthesis events.
    """
    if evt.result.reason == speech_sdk.ResultReason.SynthesizingAudio:
        audio_data = evt.result.audio_data
        with open("output.wav", "ab") as f:
            f.write(audio_data)
    elif evt.result.reason == speech_sdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech synthesis completed.")

load_dotenv()

speech_config=speech_sdk.SpeechConfig(subscription=os.getenv("COGNITIVE_SVC_KEY"),region=os.getenv("COGNITIVE_SVC_REGION"))


###Speech Recognizer configuration
def speech_to_text() -> str:
    audio_config = speech_sdk.AudioConfig(use_default_microphone=True)
    speech_recognizer = speech_sdk.SpeechRecognizer(speech_config=speech_config,audio_config=audio_config)
    print("Speak Now...")

    speech = speech_recognizer.recognize_once_async().get()
    recog_text = None
    if(speech.reason == speech_sdk.ResultReason.RecognizedSpeech):
        recog_text=speech.text
        print(recog_text)
    return recog_text 


##Speech Synthesis - Text to Speech
# To vhange Speech synthesis language or dialect en-US-AvaMultilingualNeural, es-ES-ElviraNeural
speech_config.speech_synthesis_voice_name = "en-US-RyanMultilingualNeural"

#pull_stream = speech_sdk.audio.PullAudioOutputStream()
#stream_config = speech_sdk.audio.AudioOutputConfig(use_default_speaker=True)
speech_synthesizer = speech_sdk.SpeechSynthesizer(speech_config)

speech_synthesizer.synthesis_started.connect(lambda evt: print("Synthesis started"))
speech_synthesizer.synthesizing.connect(synthesis_callback)
speech_synthesizer.synthesis_completed.connect(lambda evt: print("Synthesis completed"))

test_text="Welcome to Expert Discussion Panel"
speak = speech_synthesizer.speak_text_async(test_text).get()

if(speak.reason != speech_sdk.ResultReason.SynthesizingAudioCompleted):
    print(speak._cancellation_details.error_details)

