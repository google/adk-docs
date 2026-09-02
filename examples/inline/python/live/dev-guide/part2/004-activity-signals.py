from google.genai import types

# Manual activity signal pattern (e.g., push-to-talk)
live_request_queue.send_activity_start()  # Signal: user started speaking

# Stream audio chunks while user holds the talk button
while user_is_holding_button:
    audio_blob = types.Blob(mime_type="audio/pcm;rate=16000", data=audio_chunk)
    live_request_queue.send_realtime(audio_blob)

live_request_queue.send_activity_end()  # Signal: user stopped speaking