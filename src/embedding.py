from google import genai
from pinecone import Pinecone, ServerlessSpec
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
import os
import time


# Load hide env
load_dotenv()


# Key Config:
ai_client = genai.Client()
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))

INDEX_NAME = "transcription-index-v2"


def load_transcript(file_path):
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return None
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()




def split_text_into_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 500,       
        chunk_overlap = 50,
        length_function = len,
        is_separator_regex = False,
    )
    return text_splitter.create_documents([text])




def configure_pinecone_and_upsert(chunks):

    if INDEX_NAME not in pc.list_indexes().names():
        print(f"Creating Pinecone index '{INDEX_NAME}'...")
        pc.create_index(
            name = INDEX_NAME,
            dimension = 3072,
            metric = "cosine",
            spec = ServerlessSpec(cloud="aws", region="us-east-1")
        )

        while not pc.describe_index(INDEX_NAME).status['ready']:
            time.sleep(1)
        print("Index ready!")
    else:
        print(f"Index '{INDEX_NAME}' already exists.")



    index = pc.Index(INDEX_NAME)
    
    vectors_to_upsert = []
    print("Generating embeddings and preparing vectors...")

    
    for i, chunk in enumerate(chunks):
        text_content = chunk.page_content
        
        response = ai_client.models.embed_content(
            model = 'gemini-embedding-001',
            contents = text_content
        )
        
        embedding = response.embeddings[0].values
        
        vectors_to_upsert.append((
            f"chunk_{i}", 
            embedding, 
            {"text": text_content}
        ))

    
    print(f"Upserting {len(vectors_to_upsert)} vectors to Pinecone...")
    index.upsert(vectors=vectors_to_upsert)
    print("Vectors successfully uploaded to Pinecone!")



if __name__ == "__main__":
    transcript_path = "transcript.txt"
    raw_text = load_transcript(transcript_path)
    
    if raw_text:
        print(f"Original text length: {len(raw_text)} characters.")
        
        document_chunks = split_text_into_chunks(raw_text)
        print(f"Total chunks created: {len(document_chunks)}")
        
        configure_pinecone_and_upsert(document_chunks)