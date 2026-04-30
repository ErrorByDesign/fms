import { pipeline } from 'https://jsdelivr.net';

let transcriber;

// Load the model immediately
async function loadModel() {
    transcriber = await pipeline('automatic-speech-recognition', 'Xenova/whisper-tiny', {
        progress_callback: (p) => {
            if (p.status === 'progress') {
                self.postMessage({ type: 'progress', data: Math.round(p.progress) });
            }
        }
    });
    self.postMessage({ type: 'ready' });
}

loadModel();

self.onmessage = async (event) => {
    const { audio } = event.data;
    const result = await transcriber(audio);
    self.postMessage({ type: 'result', data: result.text });
};
