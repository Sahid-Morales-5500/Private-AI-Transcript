# Private AI Transcript - Audio & Video Report Generator

[![Python](https://img.shields.io/badge/PYTHON-3.10+-yellow?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Gemini](https://img.shields.io/badge/GOOGLE-GEMINI-8E75B2?style=for-the-badge&logo=googlegemini&logoColor=white)](https://ai.google.dev/)
[![Pinecone](https://img.shields.io/badge/PINECONE-VECTOR_DB-black?style=for-the-badge)](https://www.pinecone.io/)
[![LangChain](https://img.shields.io/badge/LANGCHAIN-TEXT_SPLITTERS-green?style=for-the-badge)](https://python.langchain.com/)
[![Notion](https://img.shields.io/badge/NOTION-API-white?style=for-the-badge&logo=notion&logoColor=black)](https://developers.notion.com/)

---

## What does this AI do and how?

### What the AI does:
This is your own personal AI assistant for audio and video. You give it a YouTube link, it transcribes the full video, and then you can ask any question about it. The answer is saved as a report directly in your Notion workspace.

It works with videos in any language. For example, it can read a video in Spanish and answer your questions in English.

**Note:** The audio and text are processed by Google Gemini, Pinecone, and Notion using **your own API keys**. Nothing is shared with anyone else, but the data does go to those services.

### How the AI works:
The program runs a 5-step pipeline:

1. **Extraction:** Downloads the audio of the video with `yt-dlp`.
2. **Transcription:** Gemini transcribes the audio word for word, in the original language.
3. **Vectorization:** The transcript is split into small pieces (500 characters). Each piece is converted into a vector with Gemini embeddings and stored in Pinecone.
4. **Analysis (RAG):** The program asks you for a question. It searches Pinecone for the 5 most relevant pieces and sends only those to Gemini with a **strict grounding prompt**: the AI can only answer with information from the transcript. If the answer is not there, it says *"Information not found in the transcription."*
5. **Publishing:** The final report is created as a new page in your Notion database.

```
YouTube link ──► yt-dlp ──► Gemini (transcription) ──► Pinecone (vectors) ──► Gemini (answer) ──► Notion page
```

---

## What results does it give?

<!-- Add a screenshot of your Notion page here:
![Notion report](images/notion_report.png)
-->

**Example:** A 5-minute video in Spanish about the history of Robin (DC Comics).

* **Question:** *"Who were the first and the last Robin?"*
* **Report (in English):** Identifies Dick Grayson as the first Robin and Damian Wayne as the most recent one, and lists all five Robins mentioned in the video in chronological order, with short quotes from the original Spanish transcript as evidence.

---

## What is its utility?
* **Meeting and class notes:** Turn long recordings into a short report you can search later in Notion.
* **Content research:** Ask specific questions about long videos or podcasts without watching them completely.
* **Multilingual summaries:** Understand videos in another language and get the answer in yours.
* **Reliable answers:** The strict grounding prompt reduces invented answers, because the AI must use only what was said in the recording.

---

## How is the project composed?
The project is modularized into a main orchestrator and a `src/` folder with one file for each step of the pipeline.

* **`src/` (The pipeline folder):**
  * `extractor.py`: Downloads the best quality audio from a YouTube link.
  * `transcriber.py`: Uploads the audio to Gemini and returns the full transcription.
  * `embedding.py`: Splits the transcript into chunks, creates the Pinecone index (if it doesn't exist), and uploads the vectors.
  * `analyzer.py`: Searches the most relevant chunks for your question and generates the grounded answer with Gemini.
  * `notion_publisher.py`: Creates a new page in your Notion database with the report (respecting Notion's 2,000-character and 100-block limits).
* **`main.py`:** The main orchestrator that runs the entire pipeline sequentially.
* **`data/`:** Created automatically. Stores the audio, the transcript, and the report on your computer (not uploaded to GitHub).

---

## How to download and use the program:

**1. Clone the repository:**
```bash
git clone https://github.com/Sahid-Morales-5500/Private-AI-Transcript.git
cd Private-AI-Transcript
```

**2. Install the dependencies:**
```bash
pip install pipenv
pipenv install
pipenv shell
```

**3. Get your API keys:**
* **Gemini:** [Google AI Studio](https://aistudio.google.com/apikey)
* **Pinecone:** [Pinecone Console](https://app.pinecone.io/)
* **Notion:** Create an integration at [notion.so/my-integrations](https://www.notion.so/my-integrations), then create a database whose title column is named **`Reports`** and share it with your integration.

**4. Create your `.env` file:**

Create a file named `.env` in the main folder and add your keys:
```
GEMINI_API_KEY=your_gemini_key
PINECONE_API_KEY=your_pinecone_key
NOTION_TOKEN=your_notion_integration_token
NOTION_DATABASE_ID=your_notion_database_id
```

**5. Run the program:**
```bash
python main.py
```
The program will ask you for a **YouTube video URL** and then for **your question**. When it finishes, it prints the link to your new Notion page.

---

## What are its current limitations?
* **One video at a time:** The program uses the first audio file in `data/audio_data/`. Delete the old audio before processing a new video.
* **Shared index:** All videos are stored in the same Pinecone index, so a new video can mix with chunks from a previous one.
* **Long reports:** Notion pages are limited to 100 blocks per request, so very long reports may be cut.
* **YouTube only:** Local audio files are not supported yet.
