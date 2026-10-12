#!/usr/bin/python
#
# This file is part of django-feedly project.
#
# Copyright (C) 2011-2026 William Oliveira de Lagos <william.lagos@icloud.com>
#
# Feedly is free software: you can redistribute it and/or modify
# it under the terms of the Lesser GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Feedly is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

import hashlib
import logging
import math
import os
from typing import Any, Dict, List, Optional, Union

from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from .models import ContentEmbedding

logger = logging.getLogger(__name__)


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """
    Calculate the cosine similarity between two float vectors.
    Returns a float between -1.0 and 1.0 (typically 0.0 to 1.0 for embeddings).
    """
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0

    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    return dot / (norm_a * norm_b)


class GeminiEmbeddingService:
    """
    Service for generating vector embeddings using Google Gemini API (`google-genai` SDK)
    and conducting semantic similarity lookups.
    """

    DEFAULT_MODEL = "gemini-embedding-001"
    FALLBACK_DIMENSIONS = 64

    def __init__(
        self,
        api_key: Optional[str] = None,
        default_model: Optional[str] = None,
    ):
        self.api_key = (
            api_key
            or getattr(settings, "GEMINI_API_KEY", None)
            or os.environ.get("GEMINI_API_KEY")
        )
        self.default_model = default_model or self.DEFAULT_MODEL
        self.client = None

        if self.api_key:
            try:
                from google import genai

                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.warning(
                    "Failed to initialize Google GenAI Client with provided key: %s", e
                )

    def _generate_fallback_vector(
        self, text: str, dimensions: int = FALLBACK_DIMENSIONS
    ) -> List[float]:
        """
        Generate a deterministic, normalized pseudo-embedding based on text tokens and hashing.
        Used when GEMINI_API_KEY is not configured (offline / testing).
        """
        if not text:
            return [0.0] * dimensions

        tokens = text.lower().split()
        vector = [0.0] * dimensions

        for idx, token in enumerate(tokens):
            h = int(hashlib.sha256(token.encode("utf-8")).hexdigest(), 16)
            bucket = h % dimensions
            weight = 1.0 / (1.0 + math.log(idx + 1))
            sign = 1.0 if (h >> 8) % 2 == 0 else -1.0
            vector[bucket] += sign * weight

        # Normalize to unit vector
        norm = math.sqrt(sum(x * x for x in vector))
        if norm > 0:
            vector = [round(x / norm, 6) for x in vector]
        else:
            vector[0] = 1.0
        return vector

    def generate_embedding(
        self,
        text: str,
        model: Optional[str] = None,
        dimensionality: Optional[int] = None,
    ) -> List[float]:
        """
        Generate embedding vector for a single text input.
        """
        target_model = model or self.default_model

        if self.client:
            try:
                from google.genai import types

                config = None
                if dimensionality:
                    config = types.EmbedContentConfig(
                        output_dimensionality=dimensionality
                    )

                response = self.client.models.embed_content(
                    model=target_model,
                    contents=text,
                    config=config,
                )

                if hasattr(response, "embeddings") and response.embeddings:
                    return list(response.embeddings[0].values)
                elif hasattr(response, "embedding") and response.embedding:
                    return list(response.embedding.values)
            except Exception as e:
                logger.error("Error generating Gemini embedding via API: %s", e)

        return self._generate_fallback_vector(
            text, dimensions=dimensionality or self.FALLBACK_DIMENSIONS
        )

    def generate_embeddings(
        self,
        texts: List[str],
        model: Optional[str] = None,
    ) -> List[List[float]]:
        """
        Batch generate embeddings for multiple texts.
        """
        return [self.generate_embedding(t, model=model) for t in texts]

    def embed_object(
        self,
        obj: Any,
        text: Optional[str] = None,
        model: Optional[str] = None,
    ) -> ContentEmbedding:
        """
        Generate and persist a ContentEmbedding record for a Django model instance.
        """
        if text is None:
            # Auto-extract text representation
            if hasattr(obj, "get_embedding_text"):
                text = obj.get_embedding_text()
            elif hasattr(obj, "content"):
                text = f"{getattr(obj, 'name', '')} {obj.content}".strip()
            elif hasattr(obj, "description"):
                text = f"{getattr(obj, 'title', getattr(obj, 'name', ''))} {obj.description}".strip()
            else:
                text = str(obj)

        model_name = model or self.default_model
        vector = self.generate_embedding(text, model=model_name)
        snippet = (text[:250] + "...") if len(text) > 250 else text

        content_type = ContentType.objects.get_for_model(obj)
        embedding_obj, _ = ContentEmbedding.objects.update_or_create(
            content_type=content_type,
            object_id=obj.pk,
            model_name=model_name,
            defaults={
                "embedding": vector,
                "text_snippet": snippet,
                "dimensions": len(vector),
            },
        )
        return embedding_obj

    def search_similar(
        self,
        query: Union[str, List[float]],
        content_type: Optional[Union[ContentType, str]] = None,
        top_k: int = 10,
        min_score: float = 0.0,
    ) -> List[Dict[str, Any]]:
        """
        Search for existing ContentEmbedding items similar to query (text or vector).
        Returns a list of dicts: [{"object": ..., "score": ..., "embedding": ..., "text_snippet": ...}]
        """
        if isinstance(query, str):
            query_vector = self.generate_embedding(query)
        else:
            query_vector = query

        qs = ContentEmbedding.objects.all().select_related("content_type")

        if content_type:
            if isinstance(content_type, str):
                try:
                    app_label, model = content_type.lower().split(".")
                    ct = ContentType.objects.get(app_label=app_label, model=model)
                    qs = qs.filter(content_type=ct)
                except Exception:
                    pass
            elif isinstance(content_type, ContentType):
                qs = qs.filter(content_type=content_type)

        results = []
        for emb in qs:
            score = cosine_similarity(query_vector, emb.embedding)
            if score >= min_score:
                results.append(
                    {
                        "object": emb.content_object,
                        "score": round(score, 4),
                        "embedding_id": emb.pk,
                        "text_snippet": emb.text_snippet,
                        "content_type": (
                            f"{emb.content_type.app_label}.{emb.content_type.model}"
                            if emb.content_type
                            else None
                        ),
                        "object_id": emb.object_id,
                    }
                )

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
