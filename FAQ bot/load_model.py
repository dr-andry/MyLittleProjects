

if __name__ == "__main__":
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer("paraphrase-multilingual-mpnet-base-v2")
    model.save("./model")