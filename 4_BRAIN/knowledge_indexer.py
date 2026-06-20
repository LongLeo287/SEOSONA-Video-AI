import os
import glob
try:
    import chromadb
    from chromadb.config import Settings
except ImportError:
    print("[Indexer] ChromaDB not installed. Skipping vector index.")
    chromadb = None

KNOWLEDGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '2_KNOWLEDGE', 'repos'))
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '3_MEMORY', 'chroma_db'))

class KnowledgeIndexer:
    def __init__(self):
        self.collection = None
        if chromadb:
            os.makedirs(DB_PATH, exist_ok=True)
            self.client = chromadb.PersistentClient(path=DB_PATH)
            self.collection = self.client.get_or_create_collection(name="seosona_repos")
            
    def index_all(self):
        if not self.collection:
            print("[Indexer] Cannot index, ChromaDB missing.")
            return

        files = glob.glob(os.path.join(KNOWLEDGE_DIR, "*.md"))
        print(f"[Indexer] Found {len(files)} knowledge files. Indexing...")
        
        docs = []
        metadatas = []
        ids = []
        
        for idx, file_path in enumerate(files):
            filename = os.path.basename(file_path)
            repo_name = filename.replace('.md', '')
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Chunking slightly if too large, but for now just use the whole md
            docs.append(content)
            metadatas.append({"source": filename, "repo": repo_name})
            ids.append(f"repo_{repo_name}")
            
            # Batch insert every 100 to save memory
            if len(docs) >= 100:
                self.collection.upsert(documents=docs, metadatas=metadatas, ids=ids)
                docs, metadatas, ids = [], [], []

        if docs:
            self.collection.upsert(documents=docs, metadatas=metadatas, ids=ids)
            
        print(f"[Indexer] Successfully indexed {len(files)} repositories into ChromaDB.")

    def query(self, text, n_results=3):
        if not self.collection:
            return []
        
        results = self.collection.query(query_texts=[text], n_results=n_results)
        if not results['documents']:
            return []
            
        return [
            {"repo": meta["repo"], "content": doc}
            for meta, doc in zip(results['metadatas'][0], results['documents'][0])
        ]

if __name__ == "__main__":
    indexer = KnowledgeIndexer()
    indexer.index_all()
