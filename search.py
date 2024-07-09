from haystack import Document
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
from haystack.document_stores.in_memory import InMemoryDocumentStore
from tqdm import tqdm


class EmbeddingFaiss():
    def __init__(self, explorer, wiki_index):
        self.explorer = explorer
        self.wiki_index = wiki_index
        
    def get_topk(self, argument, k=5):
        top_k = self.explorer.similarity_search(argument, k=k)
        documents = [doc.page_content for doc in top_k]
        return documents
    
    def get_search(self, argument):
        document = self.explorer.similarity_search(argument, k=1)[0].page_content
        document_content = " ".join(self.wiki_index[document])
        return document_content

class BM25():
    def __init__(self, wiki_index):
        self.wiki_index = wiki_index
        self.document_store = InMemoryDocumentStore()
        self.retriever = None
        self.update_documents()
        self.update_retriever()

    def update_documents(self):
        print("update document...")
        documents = []
        for key in tqdm(self.wiki_index.keys()):
            for document in list(set(self.wiki_index[key])):
                content = Document(content=document, meta={'title': key})
                documents.append(content)
            
        self.document_store.write_documents(documents)
    
    def update_retriever(self):
        self.retriever = InMemoryBM25Retriever(document_store=self.document_store)

    def get_topk(self, argument, k=5):
        results = self.retriever.run(query=argument, top_k=k)
        documents = [doc.meta['title'] for doc in results['documents']]
        return documents
    
    def get_search(self, argment):
        results = self.retriever.run(query=argment, top_k=1)
        document_content = " ".join(self.wiki_index[results['documents'][0].meta['title']])
        return document_content