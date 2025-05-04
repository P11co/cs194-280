import os, pickle, ollama

EMBEDDING_MODEL = 'hf.co/CompendiumLabs/bge-base-en-v1.5-gguf'
LANGUAGE_MODEL = 'hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF'

def load_vectordb():
    VECTOR_DB = []
    if os.path.exists("./data/vector_db.pkl"):
        with open("./data/vector_db.pkl", "rb") as f:
            VECTOR_DB = pickle.load(f)
        print(f"Loaded {len(VECTOR_DB)} embeddings from disk.")
    else:
        print("NO SUCH VECTORDB FILE... no retrieval occured!")
    return VECTOR_DB

def cosine_similarity(a, b):
    dot_product = sum([x * y for x, y in zip(a, b)])
    norm_a = sum([x ** 2 for x in a]) ** 0.5
    norm_b = sum([x ** 2 for x in b]) ** 0.5
    return dot_product / (norm_a * norm_b)

def retrieve(query, vectordb, top_n=3):
    VECTOR_DB = vectordb
    query_embedding = ollama.embed(model=EMBEDDING_MODEL, input=query)['embeddings'][0]
    # temporary list to store (chunk, similarity) pairs
    similarities = []
    for chunk, embedding in VECTOR_DB:
        similarity = cosine_similarity(query_embedding, embedding)
        similarities.append((chunk, similarity))
    # sort by similarity in descending order, because higher similarity means more relevant chunks
    similarities.sort(key=lambda x: x[1], reverse=True)
    # finally, return the top N most relevant chunks
    return similarities[:top_n]

# fetching context only
def fetch_rag_context(input_query, vectordb, top_n=3):
    retrieved_knowledge = retrieve(input_query, vectordb, top_n=top_n)

    retrieved_context = ""
    for chunk, similarity in retrieved_knowledge:
        retrieved_context += f'\n - (similarity: {similarity:.2f}) {chunk}'
    return retrieved_context

# fetches context and an LLM summarizes it 
def rag_query(input_query, vectordb, top_n=3):
    retrieved_knowledge = retrieve(input_query, vectordb, top_n=top_n)

    instruction_prompt = f"""You are a helpful chatbot.
    Use only the following pieces of context to answer the question. Don't make up any new information:
    """
    context_blob = '\n'.join([f' - {chunk}' for chunk, similarity in retrieved_knowledge])
    instruction_prompt += context_blob
    # print(instruction_prompt)

    response = ollama.chat(
    model=LANGUAGE_MODEL,
    messages=[
        {'role': 'system', 'content': instruction_prompt},
        {'role': 'user', 'content': input_query},
    ]
    )
    
    return response.message.content