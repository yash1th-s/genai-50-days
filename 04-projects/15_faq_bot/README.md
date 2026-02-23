# Day 15: FAQ Bot

A Streamlit app that lets you upload a PDF and ask questions about it using RAG.

## Features

- 📄 **PDF Upload** — Upload any PDF document
- ✂️ **Auto Chunking** — Splits document into searchable pieces
- 🔍 **Semantic Search** — Finds relevant chunks using embeddings
- 💬 **Chat Interface** — Conversational Q&A with memory
- 📊 **Token Counter** — Track API usage in real-time

## Run

```bash
cd 03-projects/15_faq_bot
pip install -r requirements.txt
streamlit run app.py
```

## How It Works

1. Upload a PDF
2. App extracts text and chunks it (500 chars, 50 overlap)
3. Each chunk is embedded and stored in ChromaDB
4. Ask questions → semantic search finds relevant chunks
5. LLM generates answer based on retrieved context

## Tech Stack

- **Streamlit** — UI
- **Gemini** — Embeddings + LLM
- **ChromaDB** — Vector storage
- **PyPDF2** — PDF parsing