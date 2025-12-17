from celery import shared_task
from sentence_transformers import SentenceTransformer
from django.db import transaction
from .models import DocEmbedding

# We will import models inside tasks when needed to avoid import-time issues

@shared_task
def upsert_embedding(module: str, record_id: int, title: str, text: str):
    model_name = 'sentence-transformers/all-MiniLM-L6-v2'
    model = SentenceTransformer(model_name)
    chunks = _chunk_text(text)
    vecs = model.encode(chunks, convert_to_numpy=True).tolist()
    with transaction.atomic():
        # remove old
        DocEmbedding.objects.filter(module=module, record_id=record_id).delete()
        # insert new
        for ch, emb in zip(chunks, vecs):
            DocEmbedding.objects.create(module=module, record_id=record_id, title=title, chunk=ch, embedding=emb)


def _chunk_text(text: str, max_tokens: int = 256):
    words = text.split()
    chunks, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) >= max_tokens:
            chunks.append(' '.join(cur))
            cur = []
    if cur:
        chunks.append(' '.join(cur))
    return chunks

