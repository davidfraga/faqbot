

from sklearn.metrics.pairwise import cosine_similarity

class IntentRouter:
    def __init__(self, embedding_model):
        self.embeddings = embedding_model
        self.intencoes = {
            "saudacao": [
                "oi", "olá", "bom dia", "boa tarde", "boa noite",
                "e aí", "tudo bem?", "como vai?", "oie", "opa"
            ],
            "agradecimento": [
                "obrigado", "obrigada", "valeu", "vlw", "muito obrigado",
                "agradecido", "obg", "brigado"
            ],
            # A intenção "faq" é o nosso padrão, não precisa de exemplos.
        }

        # Pré-calcula os embeddings das intenções para não fazer isso toda vez
        self.embeddings_intencoes = self._precalcular_embeddings()
        print("Roteador de Intenção inicializado e embeddings pré-calculados.")

    def _precalcular_embeddings(self):
        embeddings_calculados = {}
        for intencao, exemplos in self.intencoes.items():
            embeddings_calculados[intencao] = self.embeddings.embed_documents(exemplos)
        return embeddings_calculados

    def run(self, query: str, limiar: float = 0.85) -> str:
        """
        Classifica a intenção da query do usuário.
        Retorna o nome da intenção (ex: 'saudacao') ou 'faq' como padrão.
        """
        if not query.strip():
            return "vazio"

        query_embedding = self.embeddings.embed_query(query)

        melhor_intencao = "faq"
        maior_similaridade = 0.85

        for intencao, exemplos_embeddings in self.embeddings_intencoes.items():
            # Calcula a similaridade da query com todos os exemplos da intenção
            similaridades = cosine_similarity([query_embedding], exemplos_embeddings)[0]

            # Pega a maior similaridade encontrada para esta intenção
            similaridade_max_intencao = max(similaridades)

            if similaridade_max_intencao > maior_similaridade:
                maior_similaridade = similaridade_max_intencao
                melhor_intencao = intencao

        # Se a maior similaridade encontrada ultrapassar o limiar, usamos essa intenção.
        # Caso contrário, consideramos que é uma pergunta para o FAQ.
        if maior_similaridade >= limiar:
            return melhor_intencao
        else:
            return "faq"