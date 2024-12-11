document.getElementById('translateText').addEventListener('click', async () => {
    const text = document.getElementById('textInput').value;

    if (!text.trim()) {
        alert("Please enter text.");
        return;
    }

    try {
        const response = await fetch('https://6d0e-34-82-109-95.ngrok-free.app/translate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text }), // Changed from { prompt } to { text }
        });

        if (!response.ok) throw new Error("Failed to translate text.");

        const data = await response.json();
        if (data.translation) {
            document.getElementById('translation').innerText = data.translation;
        } else if (data.error) {
            document.getElementById('translation').innerText = "Error: " + data.error;
        } else {
            document.getElementById('translation').innerText = "Translation failed.";
        }
    } catch (error) {
        console.error(error);
        alert("An error occurred while processing the text.");
    }
});
