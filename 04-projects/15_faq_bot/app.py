"""
Day 15: FAQ Bot with Streamlit UI
Upload a PDF, ask questions, get answers with RAG.
"""

import streamlit as st
from google import genai
from google.genai import types
import chromadb
from PyPDF2 import PdfReader
import os
from dotenv import load_dotenv

# Load environment
load_dotenv(dotenv_path='../../.env')
API_KEY = os.environ.get("GEMINI_API_KEY2")
client = genai.Client(api_key=API_KEY)

# Initialize ChromaDB
@st.cache_resource
def get_chroma_client():
    return chromadb.Client()

chroma_client = get_chroma_client()

# Chunking function
def chunk_text(text, chunk_size=2000, overlap=200):
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end - overlap
    return chunks

# Page config
st.set_page_config(page_title="FAQ Bot", page_icon="🤖", layout="wide")
st.title("🤖 FAQ Bot")
st.caption("Upload a PDF, ask questions, get AI-powered answers")

# Sidebar for PDF upload and stats
with st.sidebar:
    st.header("📄 Document")
    uploaded_file = st.file_uploader("Upload PDF", type="pdf")
    
    st.divider()
    st.header("📊 Token Stats")
    
    if "total_input_tokens" not in st.session_state:
        st.session_state.total_input_tokens = 0
    if "total_output_tokens" not in st.session_state:
        st.session_state.total_output_tokens = 0
    
    col1, col2 = st.columns(2)
    col1.metric("Input Tokens", st.session_state.total_input_tokens)
    col2.metric("Output Tokens", st.session_state.total_output_tokens)
    
    st.metric("Total Tokens", st.session_state.total_input_tokens + st.session_state.total_output_tokens)
    
    if st.button("Reset Stats"):
        st.session_state.total_input_tokens = 0
        st.session_state.total_output_tokens = 0
        st.rerun()

# Process PDF when uploaded
if uploaded_file:
    # Check if this is a new file
    if "current_file" not in st.session_state or st.session_state.current_file != uploaded_file.name:
        with st.spinner("Processing PDF..."):
            # Read PDF
            reader = PdfReader(uploaded_file)
            full_text = ""
            for page in reader.pages:
                full_text += page.extract_text() + "\n"
            
            # Chunk the text
            chunks = chunk_text(full_text)
            
            # Create new collection
            collection_name = f"doc_{hash(uploaded_file.name) % 10000}"
            
            # Delete existing collection if exists
            try:
                chroma_client.delete_collection(collection_name)
            except:
                pass
            
            collection = chroma_client.create_collection(name=collection_name)
            
            # Index chunks
            for i, chunk in enumerate(chunks):
                embedding = client.models.embed_content(
                    model="gemini-embedding-001",
                    contents=chunk
                ).embeddings[0].values
                
                collection.add(
                    documents=[chunk],
                    embeddings=[embedding],
                    ids=[f"chunk_{i}"]
                )
            
            # Save to session state
            st.session_state.current_file = uploaded_file.name
            st.session_state.collection_name = collection_name
            st.session_state.num_chunks = len(chunks)
            # Reset chat history for new document
            st.session_state.messages = []
            st.session_state.chat_history = []  # For LLM context
        
        st.success(f"✅ Indexed {len(chunks)} chunks from {len(reader.pages)} pages")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []  # For UI display
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # For LLM context (types.Content format)

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # Show sources for assistant messages
        if message["role"] == "assistant" and "sources" in message:
            with st.expander("📄 Sources Used", expanded=False):
                for i, source in enumerate(message["sources"]):
                    st.markdown(f"**Chunk {i+1}:**")
                    st.text(source[:500] + "..." if len(source) > 500 else source)
                    if i < len(message["sources"]) - 1:
                        st.divider()

# Chat input
if uploaded_file and "collection_name" in st.session_state:
    if prompt := st.chat_input("Ask a question about the document..."):
        # Add user message to UI
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get collection
        collection = chroma_client.get_collection(st.session_state.collection_name)
        
        # Embed query
        query_emb = client.models.embed_content(
            model="gemini-embedding-001",
            contents=prompt
        ).embeddings[0].values
        
        # Search for relevant chunks
        results = collection.query(
            query_embeddings=[query_emb],
            n_results=3
        )
        context = "\n\n".join(results['documents'][0])
        
        # System instruction with context
        system_instruction = f"""You are a helpful assistant answering questions about a document.
Answer based ONLY on the context below. If the answer isn't in the context, say "I couldn't find that in the document."

Document Context:
{context}"""
        
        # Add current user message to chat history for LLM
        st.session_state.chat_history.append(
            types.Content(
                role="user",
                parts=[types.Part(text=prompt)]
            )
        )
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Generate response with full conversation history
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=st.session_state.chat_history,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction
                    )
                )
                answer = response.text
                
                # Get token usage from response
                if hasattr(response, 'usage_metadata') and response.usage_metadata:
                    st.session_state.total_input_tokens += response.usage_metadata.prompt_token_count
                    st.session_state.total_output_tokens += response.usage_metadata.candidates_token_count
                
                st.markdown(answer)
        
        # Add assistant response to chat history for LLM
        st.session_state.chat_history.append(
            types.Content(
                role="model",
                parts=[types.Part(text=answer)]
            )
        )
        
        # Add assistant message to UI with sources
        st.session_state.messages.append({
            "role": "assistant", 
            "content": answer,
            "sources": results['documents'][0]
        })
        
        # Keep only last 10 exchanges in chat history to manage context window
        if len(st.session_state.chat_history) > 20:
            st.session_state.chat_history = st.session_state.chat_history[-20:]
        
        st.rerun()

elif not uploaded_file:
    st.info("👆 Upload a PDF document to get started")