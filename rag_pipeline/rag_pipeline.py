from db.db import save_conversation


def run_rag_pipeline(question: str, qa_chain, parser):
    result = qa_chain.invoke({"input": question})
    parsed = parser.parse(result["answer"])
    response = parsed.answer
    out_of_context = not parsed.found_context

    save_conversation(user_message=question, response=response, out_of_context=out_of_context)

    return response, out_of_context
