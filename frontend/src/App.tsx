import { useContext, useRef } from 'react';
import hark from 'hark';
import { UserContext } from './contexts';
import { User } from 'firebase/auth';
import { sendHealthCheck, sendMessage, playAudio } from './utils/interactions';
import { CircularBuffer } from './utils/circularBuffer';
// import { makeAudioContext } from './utils/audioContext';

const ChatbotMessenger = () => {
  /* A voice activated chatbot messanger */
  const user: User | null = useContext(UserContext);
  const isInitialized = useRef(false);

  const init = async () => {
    if (isInitialized.current) return;
    isInitialized.current = true;

    try {
      const stream: MediaStream = await navigator.mediaDevices.getUserMedia({audio: true});
      const microphone = new MediaRecorder(stream);
      // length in ms of each recording chunk
      const interval = 50;
      const audioBlobCache = new CircularBuffer<Blob>(4);
      const audioBlobBuffer: Blob[] = [];
      let startedSpeaking = false;
      let useAudioCache = true;

      const restartAudioRecorder = async () => {
        audioBlobCache.clear();
        audioBlobBuffer.length = 0;
        useAudioCache = true;
        microphone.start();
        await speechEvents.resume();
      };

      microphone.ondataavailable = (e: BlobEvent) => {
        // save audio recording data
        if (startedSpeaking) {
          startedSpeaking = false;
          audioBlobBuffer.concat([...audioBlobCache]);
          useAudioCache = false;
        
        }
        if (useAudioCache) {
          audioBlobCache.push(e.data);
        } else {
          // accumulate microphone recording
          audioBlobBuffer.push(e.data);
        }
      };

      microphone.onstop = async () => {
        // create audio message and send it
        const audioBlob = new Blob(audioBlobBuffer, { type: audioBlobBuffer[0].type });

        const token = await user.getIdToken();
        // TODO: change to real value later
        const sampleRate: number = 48000;
        // const sampleRate: number = makeAudioContext().sampleRate;
        const response = await sendMessage(token, null, audioBlob, sampleRate);
        // attempt to play the received audio message
        const arrayBuffer = await response.arrayBuffer();
        try {
          playAudio(arrayBuffer, restartAudioRecorder);
        } catch (error) {
          console.error('Error playing audio:', error);
        }
      }

      // hark is used to detect speech / louder noises
      const speechEvents = hark(stream, {interval : interval});

      // speaking event listener        
      speechEvents.on('speaking', () => {
        if (microphone.state === "recording") {
          startedSpeaking = true;
        }
      });
      // stopped speaking event listener
      speechEvents.on('stopped_speaking', () => {
        if (microphone.state === "recording") {
          microphone.stop();
          speechEvents.suspend();
        }
      });
      // triggers every `interval` milliseconds
      speechEvents.on("volume_change", () => {
        if (microphone.state === "recording") {
          // raises the `ondatavailable` event
          microphone.requestData();
        }
      });
      await restartAudioRecorder();
    } catch (error) {
      console.error('Error downloading or playing sound:', error);
    }
  }

  return (
    <>
      <h1>Audio Recorder</h1>
      <button onClick={async () => sendHealthCheck(await user.getIdToken())}> Test API! </button>
      <button onClick={async () => init()}> Initialize audio! </button>
    </>
  );
};

export default ChatbotMessenger;
