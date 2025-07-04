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
            Leve em consideração as seguintes situações:
            - Se durante a conversa o usuário tiver mencionado seu nome, use esse nome ao iniciar sua resposta para torná-la mais pessoal.
            - Se o usuário fizer apenas uma saudação, responda naturalmente, informando que você está ali para tirar as dúvidas do usuário.
            - Se o usuário apenas agradecer, retribua o agradecimento.
            - Se o usuário se despedir, responda naturalmente, informando que está à disposição a qualquer momento caso apareça mais alguma dúvida.
            - Se NÃO souber a resposta ou estiver FORA DO CONTEXTO, peça desculpas, explicando que não tem conhecimento suficiente para responder essa dúvida.
            
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

