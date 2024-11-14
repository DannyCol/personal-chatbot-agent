import { makeAudioContext } from "./audioContext";

export const sendHealthCheck = async (token: string) => {
    const response = await fetch('/api/health/', {
        headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        Authorization: `Bearer ${token}`,
        },
        method: 'GET',
    });

    if (response.ok) {
        return 'healthy';
    }
    return 'unhealthy';
};

export const sendMessage = async (
    token: string,
    userText?: string,
    audioBlob? : Blob,
    sampleRate?: number,
) => {
    // Send audio data and sample_rate_hertz to the API
    const formData = new FormData();
    if (userText) {
        formData.append('user_text', userText);
    } else {
        formData.append('user_text', null);
        formData.append('audio_file', audioBlob, audioBlob.type);
        formData.append('sample_rate_hertz', sampleRate.toString());
    }
    // attempt a conversation interation
    try {
    // send user's request
    const response = await fetch('/api/converse/', {
        headers: {
        Authorization: `Bearer ${token}`,
        },
        method: 'POST',
        body: formData,
    });
    // validation
    if (!response.ok) {
        throw new Error('Response not ok') 
    }
    if (response.headers.get('Content-Type') !== 'audio/mpeg') {
        throw new Error('Invalid content type. Expected MP3 file.');
    }
    return response;
    } catch (error) {
        console.log("Error making request: ", error);
    }
}

export const playAudio = async (buffer: ArrayBuffer, callback?: () => void | Promise<void>) => {
    const ctx: AudioContext = makeAudioContext();
    
    const audioBuffer = await new Promise<AudioBuffer>((resolve, reject) => {
        if (ctx.decodeAudioData.length === 1)
        ctx.decodeAudioData(buffer).then(resolve).catch(reject);
        else ctx.decodeAudioData(buffer, resolve, reject);
    });

    const source = ctx.createBufferSource();
    const node = ctx.createGain();
    source.buffer = audioBuffer;
    source.connect(node);
    node.connect(ctx.destination);

    // callback to restart voice activation
    source.onended = async () => {
        source.disconnect();
        if (callback) {
            if (callback.constructor.name === 'AsyncFunction') {
                await callback();
            }
            else {
                callback();
            }
        }
    };
    // play the sound
    source.start(0);
}