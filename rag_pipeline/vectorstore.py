import os
import pickle
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.docstore.document import Document

from db.utils import load_title_description_pairs, save_new_entries_to_mongo
from models.models import ChatStructure

FAISS_INDEX_NAME = "faiss_index"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

def build_vectorstore():
    if ChatStructure.objects.count()==0:
        mapped_keys = load_title_description_pairs("contexto.md")
        save_new_entries_to_mongo(mapped_keys)
    docs = [
        Document(page_content=f"{entry.title}\n{entry.description}", metadata={"title": entry.title})
        for entry in ChatStructure.objects.all()
    ]

    if not docs:  # Verifica se a lista está vazia
        raise ValueError("[ERROR] Nenhum documento encontrado no ChatStructure para criar o índice FAISS.")

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vectorstore: FAISS = FAISS.from_documents(docs, embeddings)

    vectorstore.save_local(os.getcwd(),FAISS_INDEX_NAME)

    return vectorstore

def load_vectorstore():
    vectorstore = FAISS.load_local(folder_path=os.getcwd(), index_name=FAISS_INDEX_NAME,
                     embeddings=HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL), allow_dangerous_deserialization=True)
    return vectorstore

def get_or_build_vectorstore():
    if os.path.exists(f"{FAISS_INDEX_NAME}.pkl"):
        return load_vectorstore()
    return build_vectorstore()

