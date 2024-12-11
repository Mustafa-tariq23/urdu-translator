let mediaRecorder, audioChunks;

document.getElementById('startRecording').addEventListener('click', async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];

    mediaRecorder.ondataavailable = (event) => audioChunks.push(event.data);

    mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        const audioURL = URL.createObjectURL(audioBlob);
        document.getElementById('audioPlayer').src = audioURL;
        document.getElementById('audioPlayer').style.display = 'block';
        document.getElementById('translateRecording').style.display = 'block';
    };

    mediaRecorder.start();
    document.getElementById('startRecording').style.display = 'none';
    document.getElementById('stopRecording').style.display = 'inline-block';
});

document.getElementById('stopRecording').addEventListener('click', () => {
    mediaRecorder.stop();
    document.getElementById('startRecording').style.display = 'inline-block';
    document.getElementById('stopRecording').style.display = 'none';
});

document.getElementById('translateRecording').addEventListener('click', async () => {
    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
    const formData = new FormData();
    formData.append("audio", audioBlob, "recording.wav");

    try {
        const response = await fetch('https://6d0e-34-82-109-95.ngrok-free.app/translate', {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) throw new Error("Failed to translate recording.");

        const data = await response.json();
        document.getElementById('transcription').innerText = data.transcription;
        document.getElementById('translation').innerText = data.translation;
    } catch (error) {
        console.error(error);
        alert("An error occurred while processing the recording.");
    }
});
