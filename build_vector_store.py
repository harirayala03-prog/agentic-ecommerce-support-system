from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from policy_docs import DOCUMENTS

# This is the "embedding model" — it turns text into vectors of numbers.
# This one runs locally on your machine, free, no API key needed.
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Convert our plain dictionaries into LangChain's "Document" objects,
# which is the standard format its vector store tools expect.
documents = [
    Document(page_content=doc["content"], metadata={"id": doc["id"], "title": doc["title"]})
    for doc in DOCUMENTS
]

# This single line does the heavy lifting:
# 1. Sends each document's text through the embedding moodel
# 2. Stores the resulting vectors in a FAISS index, alongside the original text
vector_store = FAISS.from_documents(documents, embedding_model)

# Save the index to disk so we don't have to rebuild it every time we run our agent
vector_store.save_local("faiss_index")

print("Vector store built and saved to ./faiss_index")