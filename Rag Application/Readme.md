# Retrieval-Augmented Generation (RAG) Pipeline

A modular, Python-based Retrieval-Augmented Generation (RAG) application designed to ingest custom documents, generate vector embeddings, and retrieve accurate, context-grounded answers from Large Language Models (LLMs).

---

## 📋 Table of Contents
- [Overview](#overview)
- [How It Works (The RAG Workflow)](#how-it-works-the-rag-workflow)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Environment Configuration](#environment-configuration)
- [Usage](#usage)
- [Running Tests](#running-tests)
- [Git Workflow](#git-workflow)
- [License](#license)

---

## 🔍 Overview

Standard Large Language Models rely solely on their pre-trained knowledge, which can lead to hallucinations or outdated answers when queried about private, domain-specific data. This project solves that problem by implementing a **RAG architecture** that connects an LLM directly to your own local knowledge base.

---

## ⚙️ How It Works (The RAG Workflow)

The pipeline executes in five distinct stages:

1. **Document Ingestion (Load):** Reads raw documents (PDFs, Markdown, text files, etc.) from the `data/` directory.
2. **Text Splitting (Chunking):** Breaks large documents into smaller, overlapping text chunks to fit within LLM token limits while preserving semantic context.
3. **Embedding & Indexing (Store):** Converts text chunks into numerical vector representations using an Embedding Model and indexes them inside a local Vector Database.
4. **Semantic Retrieval (Search):** Converts incoming user queries into vectors and performs a similarity search to fetch the most relevant document chunks.
5. **Augmented Generation (Answer):** Combines the user's question with the retrieved context into a structured prompt, sending it to the LLM to generate an accurate, grounded response.

---

## 📁 Project Structure

Based on the repository's `.gitignore` configuration (which ignores virtual environments, bytecode, local `.env` secrets, and `pytest` caches while tracking `.env.example`), the codebase is organized as follows:

```text
rag/
├── data/                   # Raw documents (PDFs, TXT, MD) to be indexed
├── src/                    # Core RAG pipeline source code
│   ├── ingest.py           # Document loading, chunking, and vector indexing
│   ├── retriever.py        # Semantic search and context retrieval logic
│   ├── generator.py        # Prompt construction and LLM response generation
│   └── main.py             # Application entry point (CLI / API / UI)
├── tests/                  # Automated unit and integration tests
│   └── test_rag.py         # Pytest test suite
├── .env.example            # Safe template for required environment variables
├── .gitignore              # Git ignore rules (.env, .venv/, venv/, __pycache__/, etc.)
├── requirements.txt        # Python package dependencies
└── README.md               # Project documentation
```

---

## 🛠 Prerequisites

Ensure you have the following installed on your machine before getting started:
- **Python 3.10 or higher**
- **pip** (Python package manager)
- **Git**
- An API key from your chosen LLM / Embedding provider (e.g., OpenAI, Google Gemini, Hugging Face, Cohere)

---

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/your-repo-name.git
cd rag
```

### 2. Create and Activate a Virtual Environment
Isolate your project dependencies using a virtual environment (`venv` or `.venv`, both configured to be ignored by Git):

**On Windows (Command Prompt / CMD):**
```cmd
python -m venv venv
venv\Scripts\activate
```

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On macOS / Linux / Git Bash:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Configuration

Sensitive API keys are kept out of version control using `.env` files.

1. Copy `.env.example` to create your local `.env` file:
   ```bash
   # Windows CMD
   copy .env.example .env

   # macOS / Linux / Git Bash
   cp .env.example .env
   ```

2. Open `.env` and add your credentials and pipeline settings:
   ```env
   # LLM & Embedding Provider Keys
   LLM_API_KEY=your_api_key_here
   EMBEDDING_MODEL=text-embedding-3-small
   LLM_MODEL=gpt-4o-mini

   # Vector Store & Chunking Settings
   VECTOR_DB_PATH=./vectorstore
   CHUNK_SIZE=1000
   CHUNK_OVERLAP=200
   ```

---

## 💻 Usage

### Step 1: Add Documents
Place the files you want to query inside the `data/` folder.

### Step 2: Run Document Ingestion
Process your documents and build the vector index:
```bash
python src/ingest.py
```

### Step 3: Query the System
Run the main application to start asking questions against your documents:
```bash
python src/main.py
```

---

## 🧪 Running Tests

This project uses `pytest` for testing. Run the test suite from the root directory:

```bash
pytest -v
```

---

## 🔄 Git Workflow

To push updates to your repository without exposing secrets or cache files:

```bash
git status
git add .
git commit -m "Update RAG pipeline"
git push origin main
```

---

## 📄 License

This project is licensed under the MIT License.
