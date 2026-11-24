import yt_dlp
import os


def download_audio(url_video, output_folder = 'audio_data'):

    # Create Folder:
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Exceptions: Download only the best audio & set ids for every video
    options = {
        'format': 'bestaudio[ext = m4a]',
        'outtmpl': f'{output_folder}/%(id)s.%(ext)s',
        'quiet': False
    }


    try:
        print(f'Extraction init from: {url_video}')
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([url_video])
        print("Audio Donwloaded")

    except Exception as e:
        print(f'Error{e}')


# Test
if __name__ == "__main__":
    # URL Test:
    url_test = input("Youtube video URL here: ").strip()
    download_audio(url_test)
