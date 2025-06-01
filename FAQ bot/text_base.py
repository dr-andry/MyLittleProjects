import numpy as np
from sentence_transformers import SentenceTransformer, util

import json 

import os
import pickle

def load_data(path: str) -> list[dict[str, str]]:
    data = {}

    with open("./data/test_data.json", "r", encoding="utf8") as f:
        data = json.load(f)

    return data


class TextBase:
    """
    Класс базы знаний
    
    Атрибуты:
    1. db_path = путь до базы знаний
    2. base = база знаний {
                                "Question" : [эмбеддинги вопросов],
                                "Answer" : [ответы (текст)]
                            }
    3. encoder = предобученная модель sentence transformer

    методы:
    1. add_qna - добавление в базу знаний новых вопросов и ответов
    Ждёт список словарей [{'question': '...', 'answer': '...'}, {'question': '...', 'answer': '...'}, ...]
    Преобразует вопросы в эмбеддинги и сохраняет в базу знаний эмбеддинги вопросов и ответы (текст)

    2. find_answer - поиск ответа в базе знаний
    Ждёт строку - вопрос. 
    Преобразует вопрос в эмбеддинг (т.е. вектор), находит косинусное расстояние между эмбеддингом вопроса всеми эмбеддингами из базы знаний
    Находит индекс максимальной схожести, возвращает ответ из списка ответов по индексу из списка максимальной похожести эмбеддингов вопросов

    """
    def __init__(self, db_path: str = "./base.pkl"):
        self.db_path = db_path # C:\\Работа\\FAQ Титан 2 - Ваня Сухоруков\\base.pkl
        self.base = self._load_db() if os.path.exists(db_path) else {"Question": [], "Answer": []}

        self.encoder = Encoder()

    def add_qna(self, qna_list: list[dict[str, str]]):
        """qna_list = [{'question': '...', 'answer': '...'}, {'question': '...', 'answer': '...'}, ...]"""
        questions = [elem['question'] for elem in qna_list]
        answeres = [elem['answer'] for elem in qna_list]

        questions_embeddings = self.encoder.encode(questions)
        # answeres_embeddings = self.encoder.encode(answeres)

        self.base['Question'].extend(questions_embeddings)
        self.base['Answer'].extend(answeres)

        self._save()

    def find_answer(self, question):
        question_embedding = self.encoder.encode(question)

        cos_sim = util.cos_sim(question_embedding, self.base['Question'])

        if cos_sim.max().item() < 0.6:
            return None
        
        return self.base["Answer"][np.argmax(cos_sim)]
        

    def _load_db(self):
        with open(self.db_path, 'rb') as f:
            return pickle.load(f)
        
    def _save(self):
        with open(self.db_path, 'wb') as f:
            pickle.dump(self.base, f)
        
class Encoder:
    """
    Класс энкодера текста - модель sentence transformer
    """
    def __init__(self, model_path='./model'):
        # C:\\Работа\\FAQ Титан 2 - Ваня Сухоруков\\model
        self.model = SentenceTransformer.load(model_path)

    def encode(self, text):
        return self.model.encode(text)
    

if __name__ == "__main__":

    db = TextBase()

    # data = load_data('./data/test_data.json')
    # db.add_qna(data)

    test = [
    "Выдающиеся учёные экологи?",
    "Какой вклад внёс Чарльз Дарвин в развитие экологии?",
    "Экология в 20 веке?",
    "Экология в 19 веке?"
    ]


    for text in test:
        res = db.find_answer(text)
        print(f'Q: {text}\nA: {res}')
    

