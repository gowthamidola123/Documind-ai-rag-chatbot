def get_answer(db, query, api_key=None, threshold=0.2):
    results = db.similarity_search(query)

    if not results:
        return "❌ No relevant content found.", []

    # Filter based on similarity score
    relevant = [doc for doc, score in results if score > threshold]

    if not relevant:
        return "❌ No relevant answer found in document.", []

    context = "\n".join(relevant[:2])

    # ---------------- API MODE ----------------
    if api_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Answer only from context."},
                    {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
                ]
            )

            return response.choices[0].message.content, relevant

        except Exception:
            pass

    # ---------------- SMART FALLBACK ----------------
    # Return most relevant chunk
    best_doc = relevant[0]

    return f"📄 Answer from document:\n\n{best_doc[:400]}", relevant