import numpy as np
def text_to_vector(text, dim=768):
    # deterministic vector via seeded rng for demo/testing
    seed = abs(hash(text)) % (2**32)
    rng = np.random.default_rng(seed)
    return rng.random(dim).astype('float32').tolist()