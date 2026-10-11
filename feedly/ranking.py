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

import math
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Union

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet
from django.utils.timezone import now

from .ai import GeminiEmbeddingService, cosine_similarity
from .models import ContentEmbedding, ModerationRecord, Page, UserInterestProfile


class FeedRanker:
    """
    Multi-strategy ranking engine for social feeds, discovery lists, and articles.
    Strategies:
      1. Chronological (time-ordered)
      2. Personalized Affinity (blending social follow graph, semantic topic vector, and recency)
      3. Trending / Velocity (Hacker News gravity decay on engagement signals)
    """

    DEFAULT_PERSONALIZED_WEIGHTS = {
        "social": 0.35,
        "semantic": 0.45,
        "recency": 0.20,
    }

    def __init__(self, embedding_service: Optional[GeminiEmbeddingService] = None):
        self.embedding_service = embedding_service or GeminiEmbeddingService()

    @staticmethod
    def _get_item_datetime(item: Any) -> datetime:
        dt = getattr(item, "date", getattr(item, "created_at", None))
        if dt is None:
            return now()
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt

    @staticmethod
    def _get_item_author(item: Any) -> Optional[User]:
        if hasattr(item, "user") and isinstance(item.user, User):
            return item.user
        if hasattr(item, "author") and isinstance(item.author, User):
            return item.author
        if hasattr(item, "creator"):
            if isinstance(item.creator, User):
                return item.creator
            if hasattr(item.creator, "user") and isinstance(item.creator.user, User):
                return item.creator.user
        return None

    def _get_quarantined_object_ids(self, content_type: Optional[ContentType]) -> set:
        if not content_type:
            return set(
                ModerationRecord.objects.filter(is_quarantined=True).values_list(
                    "object_id", flat=True
                )
            )
        return set(
            ModerationRecord.objects.filter(
                content_type=content_type, is_quarantined=True
            ).values_list("object_id", flat=True)
        )

    def get_chronological_feed(
        self,
        items: Union[QuerySet, List[Any]],
        limit: int = 20,
        offset: int = 0,
        exclude_quarantined: bool = True,
    ) -> List[Any]:
        """
        Pure chronological feed sorted by date descending.
        """
        if isinstance(items, QuerySet):
            item_list = list(items)
        else:
            item_list = list(items)

        if exclude_quarantined and item_list:
            ct = None
            if hasattr(item_list[0], "_meta"):
                ct = ContentType.objects.get_for_model(item_list[0])
            quarantined = self._get_quarantined_object_ids(ct)
            item_list = [
                i
                for i in item_list
                if getattr(i, "pk", getattr(i, "id", None)) not in quarantined
            ]

        item_list.sort(key=self._get_item_datetime, reverse=True)
        return item_list[offset : offset + limit]

    def get_trending_feed(
        self,
        items: Union[QuerySet, List[Any]],
        limit: int = 20,
        gravity: float = 1.5,
        exclude_quarantined: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Trending engagement feed calculated via gravity decay:
        Score = (Likes*1.0 + Boosts*2.0 + Replies*1.5 + Views*0.1 + 1.0) / (Age_hours + 2)^gravity
        """
        if isinstance(items, QuerySet):
            item_list = list(items)
        else:
            item_list = list(items)

        if exclude_quarantined and item_list:
            ct = None
            if hasattr(item_list[0], "_meta"):
                ct = ContentType.objects.get_for_model(item_list[0])
            quarantined = self._get_quarantined_object_ids(ct)
            item_list = [
                i
                for i in item_list
                if getattr(i, "pk", getattr(i, "id", None)) not in quarantined
            ]

        current_time = now()
        scored_items = []

        for item in item_list:
            likes = float(getattr(item, "likes_count", 0))
            boosts = float(getattr(item, "boosts_count", 0))
            replies = float(getattr(item, "replies_count", 0))
            views = float(getattr(item, "views_count", 0))

            engagement = (
                (likes * 1.0) + (boosts * 2.0) + (replies * 1.5) + (views * 0.1)
            )

            dt = self._get_item_datetime(item)
            age_hours = max(0.1, (current_time - dt).total_seconds() / 3600.0)

            score = (engagement + 1.0) / math.pow(age_hours + 2.0, gravity)

            scored_items.append(
                {
                    "item": item,
                    "score": round(score, 5),
                    "engagement": engagement,
                    "age_hours": round(age_hours, 2),
                }
            )

        scored_items.sort(key=lambda x: x["score"], reverse=True)
        return scored_items[:limit]

    def get_personalized_feed(
        self,
        user: User,
        items: Union[QuerySet, List[Any]],
        limit: int = 20,
        weights: Optional[Dict[str, float]] = None,
        social_graph_fn: Optional[Callable[[User, User], bool]] = None,
        exclude_quarantined: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Personalized feed blending:
          - Social affinity: whether the viewer follows the item author
          - Semantic affinity: cosine similarity between user's interest vector and item embedding
          - Recency: exponential decay over hours
        """
        w = weights or self.DEFAULT_PERSONALIZED_WEIGHTS
        w_social = w.get("social", 0.35)
        w_semantic = w.get("semantic", 0.45)
        w_recency = w.get("recency", 0.20)

        if isinstance(items, QuerySet):
            item_list = list(items)
        else:
            item_list = list(items)

        if exclude_quarantined and item_list:
            ct = None
            if hasattr(item_list[0], "_meta"):
                ct = ContentType.objects.get_for_model(item_list[0])
            quarantined = self._get_quarantined_object_ids(ct)
            item_list = [
                i
                for i in item_list
                if getattr(i, "pk", getattr(i, "id", None)) not in quarantined
            ]

        # Retrieve user interest profile vector
        user_vector = None
        try:
            profile = UserInterestProfile.objects.filter(user=user).first()
            if profile and profile.interest_vector:
                user_vector = profile.interest_vector
        except Exception:
            pass

        # Preload embeddings for items if available
        embedding_map = {}
        if item_list and hasattr(item_list[0], "_meta"):
            item_ct = ContentType.objects.get_for_model(item_list[0])
            item_pks = [getattr(i, "pk", getattr(i, "id", None)) for i in item_list]
            for emb in ContentEmbedding.objects.filter(
                content_type=item_ct, object_id__in=item_pks
            ):
                embedding_map[emb.object_id] = emb.embedding

        current_time = now()
        scored_items = []

        for item in item_list:
            author = self._get_item_author(item)
            item_pk = getattr(item, "pk", getattr(item, "id", None))

            # 1. Social score
            s_social = 0.0
            if author and user.is_authenticated:
                if author == user:
                    s_social = 0.7  # Author's own content
                elif social_graph_fn:
                    s_social = 1.0 if social_graph_fn(user, author) else 0.0
                else:
                    # Generic fallback check
                    s_social = 0.2

            # 2. Semantic score
            s_semantic = 0.5  # Neutral default
            item_vector = embedding_map.get(item_pk)
            if user_vector and item_vector:
                similarity = cosine_similarity(user_vector, item_vector)
                # Map [-1.0, 1.0] to [0.0, 1.0]
                s_semantic = max(0.0, (similarity + 1.0) / 2.0)

            # 3. Recency score (half-life of approx 24 hours, lambda = 0.028)
            dt = self._get_item_datetime(item)
            age_hours = max(0.0, (current_time - dt).total_seconds() / 3600.0)
            s_recency = math.exp(-0.028 * age_hours)

            # Composite score
            composite = (
                (w_social * s_social)
                + (w_semantic * s_semantic)
                + (w_recency * s_recency)
            )

            scored_items.append(
                {
                    "item": item,
                    "score": round(composite, 4),
                    "social_score": round(s_social, 3),
                    "semantic_score": round(s_semantic, 3),
                    "recency_score": round(s_recency, 3),
                }
            )

        scored_items.sort(key=lambda x: x["score"], reverse=True)
        return scored_items[:limit]

    def update_user_interest_vector(
        self, user: User, topics: Optional[List[str]] = None
    ) -> UserInterestProfile:
        """
        Generate or update the semantic interest vector for a user from their preferred topics.
        """
        profile, _ = UserInterestProfile.objects.get_or_create(user=user)
        if topics is not None:
            profile.topics = topics

        text_to_embed = ", ".join(profile.topics) if profile.topics else user.username
        vector = self.embedding_service.generate_embedding(text_to_embed)
        profile.interest_vector = vector
        profile.save()
        return profile
