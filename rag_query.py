from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv

load_dotenv()

embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
model = ChatAnthropic(model="claude-sonnet-4-6")

# Load the index we built and saved earlier, instead of rebuilding it.
vector_store = FAISS.load_local(
    "faiss_index",
    embedding_model,
    allow_dangerous_deserialization=True
)

def answer_product_question(question: str) -> str:
    # This is the RETRIEVAL step: search for the most relevant chunks
    # to this specific question, based on meaning, not exact keywords.
    relevant_docs = vector_store.similarity_search(question, k=2)

    # Combine the retrieved chunks into one block of context text.
    context = "\n\n".join(doc.page_content for doc in relevant_docs)

    # This is the GENERATION step: ask the LLM to answer using
    # ONLY the retrieved context, not its own general knowledge.
    prompt = f"""You are a Product Knowledge specialist agent. Answer the
customer's question using ONLY the information in the context below. If the
context doesn't contain the answer, say you don't have that information.

Context:
{context}

Customer question: {question}

Write a short, friendly answer."""

    result = model.invoke(prompt)
    return result.content

# Quick test
answer = answer_product_question("If I get charged twice, what happens?")
print(answer)