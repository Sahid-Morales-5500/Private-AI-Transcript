from src.extractor import download_audio
from src.transcriber import transcribe_audio
from src.embedding import split_text_into_chunks, configure_pinecone_and_upsert, load_transcript
from src.analyzer import query_pinecone, analyze_with_llm
from src.notion_publisher import create_notion_page
import glob


def main():

    audio_dir = 'data/audio_data'
    transcript_path = 'data/transcript.txt'
    report_path = 'data/report.txt'
    url = input("Youtube video URL: ")


    # Step 1: Extraction
    print("Step 1 - Extraction")
    download_audio(url, output_folder = audio_dir)


    # Step 2: Transcription
    audio_files = glob.glob(f'{audio_dir}/*')

    if not audio_files:
        return print("Error, Audio not found in ")

    text = transcribe_audio(audio_files[0])

    if text:
        with open(transcript_path, 'w', encoding = 'UTF8') as f:
            f.write(text)
    else:
        return print("Error")


    # Step 3: Vectorization
    raw_text = load_transcript(transcript_path)

    if raw_text:
        chunks = split_text_into_chunks(raw_text)
        configure_pinecone_and_upsert(chunks)


    # Step 4: Analysis
    print("AI Analysis")
    query = input('Write your question here: ')
    context = query_pinecone(query)

    if context:
        report = analyze_with_llm(context, query)

        with open(report_path, 'w', encoding = 'utf8') as f:
            f.write(report)

    else:
        return print("Error, Pinecone context not found")


    # Step 5: Publish to Notion
    create_notion_page(report)

    print("Pipeline completed")

if __name__ == '__main__':
    main()
