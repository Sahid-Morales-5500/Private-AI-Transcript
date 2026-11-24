import os
import time
import glob
from google import genai
from dotenv import load_dotenv


# Load hide env
load_dotenv()

# Key Config:
client = genai.Client()


def transcribe_audio(audio_path):
    if not os.path.exists(audio_path):
        print(f"Error, archive {audio_path} doesn't exist.")
        return None
    
    try:
        # Step 1
        print(f"Uploading {audio_path} to Gemini Servers")
        audio_file = client.files.upload(file=audio_path)

        # Step 2:
        print("Waiting for Google to process the file")
        while audio_file.state.name == 'PROCESSING':
            print('.', end= '', flush= True)
            time.sleep(2)
            audio_file = client.files.get(name = audio_file.name)
        
        print()

        if audio_file.state.name == 'FAILED':
            print("Error: File processing failed on Gemini servers.")
            return None

        # Step 3:
        print("Processing Audio")

        # Step 4:
        prompt = "You are a professional clinical transcriber. Transcribe everything said in this audio recording word for word. Do not summarize or add comments; simply provide an exact transcription in the original language."
        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents = [prompt, audio_file]
        )

        print('Transcription Successful')
        return response.text

    except Exception as e:
        print(f"Error during the transcription: {e}")
        return None
    

if __name__ == "__main__":
    
    audio_files= glob.glob("audio_data/*.m4a")
    if not audio_files:
        print("Error: No .m4a files found in audio_data folder.")
        exit()
        
    audio_file_path = audio_files[0]

    transcribed_text = transcribe_audio(audio_file_path)
        
    if transcribed_text:
        print('\n--- Text Transcribed ---')
        print(transcribed_text[:500] + "...\n")

        with open('data/transcript.txt', 'w', encoding='UTF-8') as f:
            f.write(transcribed_text)
        print('Transcribed text in "data/transcript.txt".')