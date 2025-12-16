# RAG Implementation Guide for Universal Translation Agent

## 🎯 RAG Implementation Overview

This guide provides step-by-step instructions to implement RAG (Retrieval-Augmented Generation) in your universal translation agent for superior accuracy and context awareness.

## 🏗️ RAG Architecture Components

### 1. Vector Database Setup

#### Option A: Pinecone (Recommended for Production)
```python
# requirements.txt additions
pinecone-client==2.2.4
openai==1.3.0
langchain==0.1.0
sentence-transformers==2.2.2

# Setup Pinecone
import pinecone
from pinecone import Pinecone

class VectorDatabase:
    def __init__(self):
        self.pc = Pinecone(api_key="your-pinecone-api-key")
        self.index_name = "translation-knowledge"
        
        # Create index if it doesn't exist
        if self.index_name not in self.pc.list_indexes().names():
            self.pc.create_index(
                name=self.index_name,
                dimension=1536,  # OpenAI embedding dimension
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )
        
        self.index = self.pc.Index(self.index_name)
    
    async def upsert_documents(self, documents: List[Document]):
        vectors = []
        for doc in documents:
            embedding = await self.generate_embedding(doc.content)
            vectors.append({
                "id": doc.id,
                "values": embedding,
                "metadata": {
                    "content": doc.content,
                    "language": doc.language,
                    "domain": doc.domain,
                    "source": doc.source,
                    "quality_score": doc.quality_score
                }
            })
        
        self.index.upsert(vectors=vectors)
    
    async def search_similar(self, query: str, language: str, domain: str, top_k: int = 5):
        query_embedding = await self.generate_embedding(query)
        
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            filter={
                "language": {"$eq": language},
                "domain": {"$eq": domain}
            }
        )
        
        return [
            {
                "content": match.metadata["content"],
                "score": match.score,
                "metadata": match.metadata
            }
            for match in results.matches
        ]
```

#### Option B: Chroma (Open Source Alternative)
```python
import chromadb
from chromadb.config import Settings

class ChromaVectorDB:
    def __init__(self):
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory="./chroma_db"
        ))
        
        self.collection = self.client.get_or_create_collection(
            name="translation_knowledge",
            metadata={"hnsw:space": "cosine"}
        )
    
    async def add_documents(self, documents: List[Document]):
        embeddings = [await self.generate_embedding(doc.content) for doc in documents]
        
        self.collection.add(
            embeddings=embeddings,
            documents=[doc.content for doc in documents],
            metadatas=[{
                "language": doc.language,
                "domain": doc.domain,
                "source": doc.source,
                "quality_score": doc.quality_score
            } for doc in documents],
            ids=[doc.id for doc in documents]
        )
    
    async def query_similar(self, query: str, language: str, domain: str, n_results: int = 5):
        query_embedding = await self.generate_embedding(query)
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where={
                "$and": [
                    {"language": {"$eq": language}},
                    {"domain": {"$eq": domain}}
                ]
            }
        )
        
        return results
```

### 2. Embedding Generation Service

```python
from openai import OpenAI
from sentence_transformers import SentenceTransformer
import asyncio

class EmbeddingService:
    def __init__(self):
        self.openai_client = OpenAI()
        # Multilingual embedding model
        self.sentence_transformer = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    
    async def generate_embedding(self, text: str, method: str = "openai") -> List[float]:
        if method == "openai":
            response = await self.openai_client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            return response.data[0].embedding
        
        elif method == "sentence_transformer":
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                None, 
                self.sentence_transformer.encode, 
                text
            )
            return embedding.tolist()
    
    async def batch_generate_embeddings(self, texts: List[str], method: str = "openai") -> List[List[float]]:
        if method == "openai":
            response = await self.openai_client.embeddings.create(
                model="text-embedding-ada-002",
                input=texts
            )
            return [data.embedding for data in response.data]
        
        elif method == "sentence_transformer":
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                None,
                self.sentence_transformer.encode,
                texts
            )
            return embeddings.tolist()
```

### 3. Knowledge Base Ingestion Pipeline

```python
import asyncio
from pathlib import Path
import json
from typing import List, Dict, Any

class KnowledgeIngestionPipeline:
    def __init__(self, vector_db: VectorDatabase, embedding_service: EmbeddingService):
        self.vector_db = vector_db
        self.embedding_service = embedding_service
    
    async def ingest_documents(self, documents_path: str, domain: str, language: str):
        """Ingest documents from various sources"""
        documents = []
        
        # Process different file types
        for file_path in Path(documents_path).glob("**/*"):
            if file_path.suffix == ".txt":
                content = await self.process_text_file(file_path)
            elif file_path.suffix == ".json":
                content = await self.process_json_file(file_path)
            elif file_path.suffix == ".csv":
                content = await self.process_csv_file(file_path)
            else:
                continue
            
            # Create document chunks
            chunks = self.chunk_document(content, max_chunk_size=1000)
            
            for i, chunk in enumerate(chunks):
                doc = Document(
                    id=f"{file_path.stem}_{i}",
                    content=chunk,
                    language=language,
                    domain=domain,
                    source=str(file_path),
                    quality_score=1.0
                )
                documents.append(doc)
        
        # Batch process embeddings and store
        await self.vector_db.upsert_documents(documents)
        
        return len(documents)
    
    def chunk_document(self, content: str, max_chunk_size: int = 1000) -> List[str]:
        """Split document into chunks for better retrieval"""
        sentences = content.split('. ')
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk + sentence) < max_chunk_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    async def ingest_translation_pairs(self, translation_pairs: List[Dict]):
        """Ingest existing translation pairs for translation memory"""
        documents = []
        
        for pair in translation_pairs:
            # Create bidirectional entries
            doc1 = Document(
                id=f"tm_{pair['id']}_forward",
                content=f"{pair['source_text']} -> {pair['target_text']}",
                language=f"{pair['source_lang']}_{pair['target_lang']}",
                domain=pair.get('domain', 'general'),
                source="translation_memory",
                quality_score=pair.get('quality_score', 0.8)
            )
            
            doc2 = Document(
                id=f"tm_{pair['id']}_reverse",
                content=f"{pair['target_text']} -> {pair['source_text']}",
                language=f"{pair['target_lang']}_{pair['source_lang']}",
                domain=pair.get('domain', 'general'),
                source="translation_memory",
                quality_score=pair.get('quality_score', 0.8)
            )
            
            documents.extend([doc1, doc2])
        
        await self.vector_db.upsert_documents(documents)
        return len(documents)
```

### 4. RAG-Enhanced Translation Service

```python
from typing import Optional, List, Dict, Any
import asyncio

class RAGTranslationService:
    def __init__(self, vector_db: VectorDatabase, llm_client: OpenAI):
        self.vector_db = vector_db
        self.llm_client = llm_client
        self.embedding_service = EmbeddingService()
    
    async def translate_with_rag(
        self, 
        text: str, 
        source_lang: str, 
        target_lang: str, 
        domain: str = "general",
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        
        # 1. Retrieve relevant context from knowledge base
        relevant_docs = await self.retrieve_context(text, source_lang, target_lang, domain)
        
        # 2. Check translation memory for exact/fuzzy matches
        tm_matches = await self.check_translation_memory(text, source_lang, target_lang)
        
        # 3. Build enhanced prompt with context
        enhanced_prompt = await self.build_rag_prompt(
            text, source_lang, target_lang, relevant_docs, tm_matches, context
        )
        
        # 4. Generate translation with LLM
        translation = await self.generate_translation(enhanced_prompt)
        
        # 5. Validate and score the translation
        quality_score = await self.score_translation(text, translation, source_lang, target_lang)
        
        # 6. Store in translation memory for future use
        await self.store_translation(text, translation, source_lang, target_lang, domain, quality_score)
        
        return {
            "original_text": text,
            "translated_text": translation,
            "source_language": source_lang,
            "target_language": target_lang,
            "domain": domain,
            "quality_score": quality_score,
            "context_used": len(relevant_docs),
            "translation_memory_matches": len(tm_matches)
        }
    
    async def retrieve_context(self, text: str, source_lang: str, target_lang: str, domain: str) -> List[Dict]:
        """Retrieve relevant context from knowledge base"""
        # Search for similar content in both source and target languages
        source_context = await self.vector_db.search_similar(text, source_lang, domain, top_k=3)
        target_context = await self.vector_db.search_similar(text, target_lang, domain, top_k=2)
        
        # Combine and deduplicate
        all_context = source_context + target_context
        return sorted(all_context, key=lambda x: x['score'], reverse=True)[:5]
    
    async def check_translation_memory(self, text: str, source_lang: str, target_lang: str) -> List[Dict]:
        """Check for existing translations in memory"""
        query = f"{text}"
        lang_pair = f"{source_lang}_{target_lang}"
        
        matches = await self.vector_db.search_similar(query, lang_pair, "translation_memory", top_k=3)
        
        # Filter for high-quality matches
        return [match for match in matches if match['score'] > 0.8]
    
    async def build_rag_prompt(
        self, 
        text: str, 
        source_lang: str, 
        target_lang: str, 
        relevant_docs: List[Dict],
        tm_matches: List[Dict],
        context: Optional[str] = None
    ) -> str:
        """Build enhanced prompt with retrieved context"""
        
        prompt = f"""You are an expert translator with access to relevant context and examples.

Translate the following {source_lang} text to {target_lang}:
"{text}"

"""
        
        if context:
            prompt += f"Additional context: {context}\n\n"
        
        if relevant_docs:
            prompt += "Relevant context from knowledge base:\n"
            for i, doc in enumerate(relevant_docs[:3]):
                prompt += f"{i+1}. {doc['content'][:200]}...\n"
            prompt += "\n"
        
        if tm_matches:
            prompt += "Similar translations from memory:\n"
            for i, match in enumerate(tm_matches[:2]):
                prompt += f"{i+1}. {match['content']}\n"
            prompt += "\n"
        
        prompt += f"""Requirements:
1. Maintain the original meaning and tone
2. Use appropriate {target_lang} terminology for the domain
3. Consider cultural context and appropriateness
4. Ensure grammatical correctness
5. Preserve any technical terms accurately

Translation:"""
        
        return prompt
    
    async def generate_translation(self, prompt: str) -> str:
        """Generate translation using LLM with enhanced prompt"""
        response = await self.llm_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are a professional translator with expertise in multiple languages and domains."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.3  # Lower temperature for more consistent translations
        )
        
        return response.choices[0].message.content.strip()
    
    async def score_translation(self, original: str, translation: str, source_lang: str, target_lang: str) -> float:
        """Score translation quality using multiple metrics"""
        # This is a simplified version - in production, you'd use more sophisticated metrics
        
        # Length ratio check (translations shouldn't be too different in length)
        length_ratio = len(translation) / len(original) if len(original) > 0 else 1
        length_score = 1.0 if 0.5 <= length_ratio <= 2.0 else 0.8
        
        # Basic completeness check
        completeness_score = 1.0 if translation and len(translation.strip()) > 0 else 0.0
        
        # You could add more sophisticated scoring here:
        # - BLEU score comparison with reference translations
        # - Semantic similarity using embeddings
        # - Grammar checking
        # - Domain-specific terminology validation
        
        return (length_score + completeness_score) / 2
    
    async def store_translation(
        self, 
        original: str, 
        translation: str, 
        source_lang: str, 
        target_lang: str, 
        domain: str, 
        quality_score: float
    ):
        """Store translation in memory for future retrieval"""
        doc = Document(
            id=f"user_translation_{hash(original + translation)}",
            content=f"{original} -> {translation}",
            language=f"{source_lang}_{target_lang}",
            domain=domain,
            source="user_translation",
            quality_score=quality_score
        )
        
        await self.vector_db.upsert_documents([doc])
```

## 🚀 Quick Start Implementation

### 1. Install Dependencies
```bash
pip install pinecone-client openai langchain sentence-transformers chromadb
```

### 2. Set Up Environment Variables
```bash
export PINECONE_API_KEY="your-pinecone-key"
export OPENAI_API_KEY="your-openai-key"
export PINECONE_ENVIRONMENT="us-east-1"
```

### 3. Initialize RAG System
```python
# Initialize components
vector_db = VectorDatabase()
embedding_service = EmbeddingService()
llm_client = OpenAI()

# Create RAG translation service
rag_translator = RAGTranslationService(vector_db, llm_client)

# Ingest initial knowledge base
ingestion_pipeline = KnowledgeIngestionPipeline(vector_db, embedding_service)
await ingestion_pipeline.ingest_documents("./knowledge_base", "business", "en")
```

### 4. Use RAG Translation
```python
# Translate with RAG enhancement
result = await rag_translator.translate_with_rag(
    text="வணக்கம், இந்த திட்டத்தின் முன்னேற்றம் எப்படி இருக்கிறது?",
    source_lang="ta",
    target_lang="en",
    domain="business",
    context="Project status meeting"
)

print(f"Translation: {result['translated_text']}")
print(f"Quality Score: {result['quality_score']}")
```

This RAG implementation provides:
- **Context-aware translations** using relevant knowledge
- **Translation memory** for consistency
- **Continuous learning** from user interactions
- **Domain expertise** through specialized knowledge bases
- **Quality scoring** and validation

The system will continuously improve as more translations are processed and stored in the knowledge base.

Would you like me to create specific implementation guides for any particular component or update the other documents to reflect this RAG-enhanced approach?
