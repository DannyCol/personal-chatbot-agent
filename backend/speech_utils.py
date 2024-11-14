"""speech_utils.py"""

from google.cloud import speech_v1
from google.cloud import texttospeech as tts_lib


async def recognize(
    spoken_content: bytes, sample_rate_hertz: int, mime_type: str
) -> str:
    """Converts audio file to text"""
    if "audio/webm" in mime_type:
        encoding = speech_v1.RecognitionConfig.AudioEncoding.WEBM_OPUS
    elif "audio/ogg" in mime_type:
        encoding = speech_v1.RecognitionConfig.AudioEncoding.OGG_OPUS
    else:
        raise Exception(f"Need to implement mime type: {mime_type}")

    audio = speech_v1.RecognitionAudio(content=spoken_content)

    client = speech_v1.SpeechAsyncClient()
    config = speech_v1.RecognitionConfig(
        encoding=encoding,
        sample_rate_hertz=sample_rate_hertz,
        language_code="en-US",
        model="default",
    )
    request = speech_v1.RecognizeRequest(
        config=config,
        audio=audio,
    )
    response = await client.recognize(request=request)
    text_from_speech = " ".join(
        [result.alternatives[0].transcript for result in response.results]
    )
    return text_from_speech


async def synthesize(text: str) -> bytes:
    """Converts text into an audio file (mp3)"""
    client = tts_lib.TextToSpeechAsyncClient()

    synthesis_input = tts_lib.SynthesisInput(text=text)
    response = await client.synthesize_speech(
        input=synthesis_input,
        voice=tts_lib.VoiceSelectionParams(
            language_code="en-US", name="en-US-Wavenet-F"
        ),
        audio_config=tts_lib.AudioConfig(audio_encoding=tts_lib.AudioEncoding.MP3),
    )
    return response.audio_content
