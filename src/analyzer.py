import os
from google import genai
from pinecone import Pinecone
from dotenv import load_dotenv


# Load environment variables
load_dotenv()


# Key Configuration
ai_client = genai.Client()
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
INDEX_NAME = "transcription-index-v2"




def query_pinecone(query_text, top_k=5):
    # 1. Convert the user's query into a vector (using the correct model)
    response = ai_client.models.embed_content(
        model='gemini-embedding-001',
        contents=query_text
    )
    query_embedding = response.embeddings[0].values

    # 2. Search Pinecone for the most relevant chunks
    index = pc.Index(INDEX_NAME)
    search_results = index.query(
        vector = query_embedding,
        top_k = top_k,
        include_metadata = True
    )
    
    # 3. Extract text from the matched results
    context_chunks = [match['metadata']['text'] for match in search_results['matches']]
    return "\n\n---\n\n".join(context_chunks)




def analyze_with_llm(context, user_query):
    #4. Strict LLM Prompt Architecture
    strict_prompt = f"""
    You are an expert clinical data analyst. 
    Analyze the following transcribed text chunks and answer the user's query.
    
    STRICT ZERO-HALLUCINATION POLICY:
    - You must ONLY use the provided context below to formulate your answer.
    - If the answer is not explicitly contained in the context, you MUST state "Information not found in the transcription."
    - Do not make up, infer, or bring in outside knowledge.
    - Extract clear clinical themes and provide a professional summary.
    
    CONTEXT:
    {context}
    
    USER QUERY: {user_query}
    """

    response = ai_client.models.generate_content(
        model='gemini-3.5-flash',
        contents=strict_prompt
    )
    return response.text

if __name__ == "__main__":
    print("Initiating Step 4: AI Analysis & RAG...")
    
    # The query that will trigger the analysis
    query = "What are the main themes, symptoms, or key points discussed in this recording?"
    print(f"Querying Pinecone database for relevant context...")
    
    # Execute the vector search
    context_data = query_pinecone(query)
    
    if context_data:
        print("Context retrieved successfully! Generating strict AI report...")
        
        # Generate the report based ONLY on the transcription
        final_report = analyze_with_llm(context_data, query)
        
        print("\n" + "="*50)
        print("FINAL AI REPORT")
        print("="*50)
        print(final_report)
        print("="*50)
        
        # Save the report for Step 5 (Notion integration)
        with open("data/report.txt", "w", encoding="utf-8") as f:
            f.write(final_report)
        print("\nReport securely saved as 'data/report.txt'.")
    else:
        print("Error: No context retrieved from Pinecone.")