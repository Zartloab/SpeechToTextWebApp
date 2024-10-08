import logging
import azure.cognitiveservices.speech as speechsdk
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/translate-speech/', methods=['POST'])
def translate_speech():
    logging.info('Request received for speech translation.')
    
    # Retrieve input_language and output_language from the request body (JSON)
    data = request.get_json()
    
    if not data or 'input_language' not in data or 'output_language' not in data:
        return jsonify({
            "error": "Please provide both 'input_language' and 'output_language' in the request body."
        }), 400

    input_language = data['input_language']
    output_language = data['output_language']
    
    # Azure Speech SDK configuration with subscription key and region
    speech_translation_config = speechsdk.translation.SpeechTranslationConfig(
        subscription="SUBSCRIPTION_KEY", 
        region="REGION"
    )
    
    # Set the recognition language to the user-selected input language
    speech_translation_config.speech_recognition_language = input_language
    
    # Set the target language dynamically based on user-selected output language
    speech_translation_config.add_target_language(output_language)

    # Use the default microphone for audio input
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    translation_recognizer = speechsdk.translation.TranslationRecognizer(
        translation_config=speech_translation_config, 
        audio_config=audio_config
    )

    logging.info("Speak into your microphone.")
    
    # Start the recognition process
    translation_recognition_result = translation_recognizer.recognize_once_async().get()

    # Process the result and handle the response
    if translation_recognition_result.reason == speechsdk.ResultReason.TranslatedSpeech:
        # Ensure dynamic output of translated language
        return jsonify({
            "recognized": translation_recognition_result.text,
            "translation": translation_recognition_result.translations.get(output_language, "Translation not available for the selected language")
        })
    elif translation_recognition_result.reason == speechsdk.ResultReason.NoMatch:
        logging.error("No speech could be recognized.")
        return jsonify({"error": "No speech could be recognized."}), 400
    elif translation_recognition_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = translation_recognition_result.cancellation_details
        logging.error(f"Speech Recognition canceled: {cancellation_details.reason}")
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            logging.error(f"Error details: {cancellation_details.error_details}")
        return jsonify({
            "error": f"Speech Recognition canceled: {cancellation_details.reason}"
        }), 500

# Run the app if it's executed directly
if __name__ == '__main__':
    app.run(debug=True)
