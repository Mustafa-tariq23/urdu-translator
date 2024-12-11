document
  .getElementById("translateAudioButton")
  .addEventListener("click", async () => {
    const fileInput = document.getElementById("audioFile");
    const file = fileInput.files[0];

    if (!file) {
      alert("Please select an audio file.");
      return;
    }

    const loader = document.getElementById("loader");
    loader.style.display = "block";

    const formData = new FormData();
    formData.append("audio", file);

    try {
      const response = await fetch(
        "https://6d0e-34-82-109-95.ngrok-free.app/translate",
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) throw new Error("Failed to translate audio.");

      const data = await response.json();
      document.getElementById("transcription").innerText = data.transcription;
      document.getElementById("translation").innerText = data.translation;
    } catch (error) {
      console.error(error);
      alert("An error occurred while processing the audio.");
    } finally {
      // Hide the loader
      loader.style.display = "none";
    }
  });
