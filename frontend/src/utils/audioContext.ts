declare let window: Window;

interface Window {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    webkitAudioContext?: any
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    webkitSpeechRecognition?: any
}

export const makeAudioContext = () => {
    return window.webkitAudioContext
      ? new window.webkitAudioContext()
      : typeof AudioContext !== 'undefined'
        ? new AudioContext()
        : undefined;
}
