import os
from langchain.chains import ConversationalRetrievalChain
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from db.vectorstore import get_or_build_vectorstore
from langchain.chains import create_retrieval_chain
from langchain.chat_models import init_chat_model
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_groq import ChatGroq
from decouple import config

class FormattedLLMAnswer(BaseModel):
    answer: str = Field(description="Texto da resposta.")
    found_context: bool = Field(description="Se o contexto foi suficiente para responder.")

class ChatSettings:
    def __init__(self, session_id="default_session"):
        # TODO: history messages
        """
        message_history = MongoDBChatMessageHistory(
            connection_string="mongodb://mongodb:27017",
            session_id=session_id,
        )

        # Definir uma memória de buffer que use esse histórico
        memory = ConversationBufferMemory(chat_memory=message_history, return_messages=True)
        """
        os.environ["GROQ_API_KEY"] = config("GROQ_API_KEY")

        self._set_prompt()

        self.llm = init_chat_model("llama3-8b-8192", model_provider="groq", temperature=0)

        self._build()


    def _build(self):
        vector_store = get_or_build_vectorstore()
        self.intent_router = vector_store.embeddings
        retriever = vector_store.as_retriever(search_kwargs={"k": 3})

        # Instantiate chain
        combine_docs_chain = create_stuff_documents_chain(self.llm, self.prompt)
        self.qa_chain = create_retrieval_chain(retriever, combine_docs_chain)

    def _set_prompt(self):
        prompt_template = """
                        Sua única função é atuar como um assistente de FAQ preciso. Sua tarefa é responder à pergunta do usuário BASEANDO-SE ESTRITA E UNICAMENTE no CONTEXTO fornecido.

                        Se durante a conversa o usuário tiver mencionado seu nome, use esse nome ao iniciar sua resposta para torná-la mais pessoal.

                        NÃO USE nenhum conhecimento prévio ou externo. Sua base de conhecimento está limitada ao que está no CONTEXTO 

                        CONTEXTO:
                        {context}

                        PERGUNTA:
                        {input}

                        INSTRUÇÕES DE FORMATAÇÃO:
                        Siga estritamente as instruções de formatação abaixo para a sua resposta.
                        {format_instructions}
                        """

        self.parser = PydanticOutputParser(pydantic_object=FormattedLLMAnswer)
        self.prompt = ChatPromptTemplate.from_template(
            template=prompt_template,
            partial_variables={"format_instructions": self.parser.get_format_instructions()},
        )

    def update_settings(self):
        self._build()

        """
        combine_docs_chain = load_qa_chain(
            llm=ChatGroq(temperature=0, model="llama-3.1-8b-instant",groq_api_key=config("GROQ_API_KEY")),  # Use seu modelo LLM aqui
            chain_type="stuff",  # Escolha o tipo apropriado: "stuff", "map_reduce", etc.
            prompt=prompt
        )
        
        

        self.qa_chain = ConversationalRetrievalChain(
            retriever=retriever, memory=memory, combine_docs_chain=combine_docs_chain
        )
        """

# OLD VERSION
'''
import os
import time

from decouple import config
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from pydantic import BaseModel, Field
from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain

from intent_router import IntentRouter
from db.vectorstore import get_or_build_vectorstore


class FormattedLLMAnswer(BaseModel):
    """Estrutura de dados para a resposta do bot com rastreamento de contexto."""

    answer: str = Field(description="A resposta em texto a ser enviada para o usuário.")
    found_context: bool = Field(
        description="Indica se o contexto fornecido foi suficiente para responder à pergunta. Defina como 'False' se o contexto estiver vazio ou não contiver a resposta."
    )


class ChatSettings():

    def __init__(self, session_id: str = "default_session"):
        time1 = time.time()
        os.environ["GROQ_API_KEY"] = config("GROQ_API_KEY")

        prompt_template = """
        Sua única função é atuar como um assistente de FAQ preciso. Sua tarefa é responder à pergunta do usuário BASEANDO-SE ESTRITA E UNICAMENTE no CONTEXTO fornecido.
        
        Se durante a conversa o usuário tiver mencionado seu nome, use esse nome ao iniciar sua resposta para torná-la mais pessoal.
        
        NÃO USE nenhum conhecimento prévio ou externo. Sua base de conhecimento está limitada ao que está no CONTEXTO ou na CONVERSA ANTERIOR.
        
        CONVERSA ANTERIOR:
        {chat_history}
        
        CONTEXTO:
        {context}
        
        PERGUNTA:
        {question}
        
        INSTRUÇÕES DE FORMATAÇÃO:
        Siga estritamente as instruções de formatação abaixo para a sua resposta.
        {format_instructions}
        """

        self.parser = PydanticOutputParser(pydantic_object=FormattedLLMAnswer)
        prompt = ChatPromptTemplate.from_template(
            template=prompt_template,
            partial_variables={"format_instructions": self.parser.get_format_instructions()},
        )
        print(f"Time: {time.time() - time1}")

        db=get_or_build_vectorstore()
        self.intent_router = IntentRouter(embedding_model=db.embeddings)
        print(f"Time: {time.time() - time1}")
        # 6. Configurar retriever (top 3 documentos)
        retriever = db.as_retriever(search_kwargs={"k": 3})
        print(f"Time: {time.time() - time1}")
        # 7. Definir o modelo Groq com LangChain
        llm = ChatGroq(temperature=0, model="llama-3.1-8b-instant")
        print(f"Time: {time.time() - time1}")

        # Criar histórico baseado em session_id
        message_history = MongoDBChatMessageHistory(
            connection_string=config("MONGO_URL", default="mongodb://localhost:27017"),
            session_id=session_id,
            database_name="chat_db",
            collection_name="chat_history",
            history_size=10,
        )

        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            chat_memory=message_history,
            output_key="answer",
        )

        self.qa_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=retriever,
            memory=memory,
            return_source_documents=True,
            combine_docs_chain_kwargs={"prompt": prompt},
        )

        print(f"Time: {time.time()-time1}")

'''