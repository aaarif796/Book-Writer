import os, faiss, numpy as np
from app.utils.config import settings
from app.utils.logger import logger

class FAISSHandler:
    def __init__(self, dim=768):
        self.dim = dim
        self.path = settings.FAISS_PATH
        os.makedirs(os.path.dirname(self.path) or '.', exist_ok=True)
        if os.path.exists(self.path):
            try:
                self.index = faiss.read_index(self.path)
            except Exception as e:
                logger.exception('Failed reading faiss index: %s', e)
                self.index = faiss.IndexFlatL2(self.dim)
        else:
            self.index = faiss.IndexFlatL2(self.dim)

    def add_vector(self, vector):
        arr = np.array([vector]).astype('float32')
        self.index.add(arr)
        faiss.write_index(self.index, self.path)

    def search(self, vector, k=3):
        arr = np.array([vector]).astype('float32')
        d, i = self.index.search(arr, k)
        return d.tolist(), i.tolist()