from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class SimpleVectorStore:
    def __init__(self, texts):
        self.texts = texts
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.vectors = self.vectorizer.fit_transform(texts)

    def similarity_search(self, query, k=3):
        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.vectors).flatten()

        top_indices = similarities.argsort()[::-1][:k]

        results = []
        for idx in top_indices:
            results.append((self.texts[idx], similarities[idx]))

        return results


def create_vector_store(text):
    # Better chunking
    chunks = []
    paragraphs = text.split("\n")

    current = ""
    for para in paragraphs:
        if len(current) + len(para) < 500:
            current += " " + para
        else:
            chunks.append(current.strip())
            current = para

    if current:
        chunks.append(current.strip())

    return SimpleVectorStore(chunks)