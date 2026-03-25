from sentence_transformers import SentenceTransformer
from database import save_document, search_chunks

model = SentenceTransformer('all-MiniLM-L6-v2')

def embed(text):
    return model.encode(text)

def chunk_text(text, chunk_size=200):
    result = []
    for start in range(0, len(text), chunk_size):
        result.append(text[start: start + chunk_size])
    return result

def index_document(doc_name, filepath):
    f = open(filepath).read()
    chunked_text = chunk_text(f)
    for chunk in chunked_text:
        text_embedding = embed(chunk)
        save_document(doc_name, chunk, text_embedding.tolist())
    

def search(query, top_k=3):
    query_embedding = embed(query)
    chunks = search_chunks(query_embedding.tolist(), top_k)
    return chunks