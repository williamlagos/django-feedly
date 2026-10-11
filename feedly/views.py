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

import json

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from .ai import GeminiEmbeddingService
from .models import Page, UserInterestProfile
from .moderation import ContentModerationService
from .ranking import FeedRanker

PAGE_NAME_PREFIX = "!#"


def page_to_dict(page):
    if page is None:
        return {}
    return {
        "id": page.id,
        "name": page.name_trimmed(),
        "content": page.content,
        "date": page.date.isoformat(),
        "user": page.user.username if getattr(page, "user", None) else None,
    }


class BlocksView(View):
    def get(self, request):
        return JsonResponse({"blocks": "success"})


class PageListView(View):
    def get(self, request):
        pages = Page.objects.all().order_by("-date")
        data = [page_to_dict(p) for p in pages]
        return JsonResponse({"pages": data})

    def post(self, request):
        try:
            body = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({"error": "Invalid JSON body"}, status=400)
        name = body.get("name", "").strip()
        content = body.get("content", "").strip()
        if not name:
            return JsonResponse({"error": "name is required"}, status=400)
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required"}, status=401)

        # AI Moderation safety check before publishing
        moderation_service = ContentModerationService()
        mod_result = moderation_service.moderate_text(f"{name}\n{content}")
        if mod_result["status"] == "rejected":
            return JsonResponse(
                {
                    "error": "Content rejected by safety moderation",
                    "reason": mod_result["reason"],
                    "categories": mod_result["categories_flagged"],
                },
                status=400,
            )

        page = Page.objects.create(
            name="%s%s" % (PAGE_NAME_PREFIX, name),
            content=content,
            user=request.user,
        )

        # Record moderation audit log
        moderation_service.moderate_object(
            page, text=f"{name}\n{content}", author=request.user
        )

        # Auto-generate semantic embedding
        embedding_service = GeminiEmbeddingService()
        embedding_service.embed_object(page, text=f"{name} {content}")

        return JsonResponse(page_to_dict(page), status=201)


class PageDetailView(View):
    def get(self, request, page_id):
        try:
            page = Page.objects.get(id=page_id)
        except Page.DoesNotExist:
            return JsonResponse({"error": "Page not found"}, status=404)
        return JsonResponse(page_to_dict(page))

    def put(self, request, page_id):
        try:
            page = Page.objects.get(id=page_id)
        except Page.DoesNotExist:
            return JsonResponse({"error": "Page not found"}, status=404)
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required"}, status=401)
        if page.user != request.user:
            return JsonResponse({"error": "Permission denied"}, status=403)
        try:
            body = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({"error": "Invalid JSON body"}, status=400)
        name = body.get("name", "").strip()
        content = body.get("content", "").strip()
        if name:
            page.name = "%s%s" % (PAGE_NAME_PREFIX, name)
        if content:
            page.content = content
        page.save()

        # Update embedding on edit
        embedding_service = GeminiEmbeddingService()
        embedding_service.embed_object(
            page, text=f"{page.name_trimmed()} {page.content}"
        )

        return JsonResponse(page_to_dict(page))

    def delete(self, request, page_id):
        try:
            page = Page.objects.get(id=page_id)
        except Page.DoesNotExist:
            return JsonResponse({"error": "Page not found"}, status=404)
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required"}, status=401)
        if page.user != request.user:
            return JsonResponse({"error": "Permission denied"}, status=403)
        page.delete()
        return JsonResponse({"status": "deleted"})


# ==========================================
# AI Feeds, Discovery & Moderation Views
# ==========================================


class ChronologicalFeedView(View):
    def get(self, request):
        limit = int(request.GET.get("limit", 20))
        offset = int(request.GET.get("offset", 0))

        pages = Page.objects.all().select_related("user")
        ranker = FeedRanker()
        feed_pages = ranker.get_chronological_feed(
            pages, limit=limit, offset=offset, exclude_quarantined=True
        )

        return JsonResponse(
            {
                "strategy": "chronological",
                "count": len(feed_pages),
                "feed": [page_to_dict(p) for p in feed_pages],
            }
        )


class TrendingFeedView(View):
    def get(self, request):
        limit = int(request.GET.get("limit", 20))
        gravity = float(request.GET.get("gravity", 1.5))

        pages = Page.objects.all().select_related("user")
        ranker = FeedRanker()
        trending = ranker.get_trending_feed(
            pages, limit=limit, gravity=gravity, exclude_quarantined=True
        )

        return JsonResponse(
            {
                "strategy": "trending",
                "count": len(trending),
                "feed": [
                    {
                        "item": page_to_dict(entry["item"]),
                        "score": entry["score"],
                        "age_hours": entry["age_hours"],
                    }
                    for entry in trending
                ],
            }
        )


class PersonalizedFeedView(View):
    def get(self, request):
        limit = int(request.GET.get("limit", 20))

        pages = Page.objects.all().select_related("user")
        ranker = FeedRanker()

        if request.user.is_authenticated:
            ranked = ranker.get_personalized_feed(
                user=request.user,
                items=pages,
                limit=limit,
                exclude_quarantined=True,
            )
            return JsonResponse(
                {
                    "strategy": "personalized",
                    "user": request.user.username,
                    "count": len(ranked),
                    "feed": [
                        {
                            "item": page_to_dict(entry["item"]),
                            "score": entry["score"],
                            "semantic_score": entry["semantic_score"],
                            "social_score": entry["social_score"],
                        }
                        for entry in ranked
                    ],
                }
            )

        # Unauthenticated fallback to chronological
        chronological = ranker.get_chronological_feed(pages, limit=limit)
        return JsonResponse(
            {
                "strategy": "chronological_fallback",
                "count": len(chronological),
                "feed": [page_to_dict(p) for p in chronological],
            }
        )


@method_decorator(csrf_exempt, name="dispatch")
class SemanticSearchView(View):
    def post(self, request):
        try:
            body = json.loads(request.body)
            query = body.get("query", "").strip()
            top_k = int(body.get("top_k", 10))
            min_score = float(body.get("min_score", 0.0))
            content_type = body.get("content_type")
        except Exception:
            return JsonResponse({"error": "Invalid search payload"}, status=400)

        if not query:
            return JsonResponse({"error": "query parameter is required"}, status=400)

        service = GeminiEmbeddingService()
        raw_results = service.search_similar(
            query=query,
            content_type=content_type,
            top_k=top_k,
            min_score=min_score,
        )

        results = []
        for r in raw_results:
            obj = r["object"]
            item_data = (
                page_to_dict(obj)
                if isinstance(obj, Page)
                else {"id": getattr(obj, "id", None), "repr": str(obj)}
            )
            results.append(
                {
                    "score": r["score"],
                    "text_snippet": r["text_snippet"],
                    "content_type": r["content_type"],
                    "object_id": r["object_id"],
                    "item": item_data,
                }
            )

        return JsonResponse(
            {
                "query": query,
                "count": len(results),
                "results": results,
            }
        )


@method_decorator(csrf_exempt, name="dispatch")
class ContentModerationView(View):
    def post(self, request):
        try:
            body = json.loads(request.body)
            text = body.get("text", "").strip()
        except Exception:
            return JsonResponse({"error": "Invalid JSON body"}, status=400)

        if not text:
            return JsonResponse({"error": "text is required"}, status=400)

        author = request.user if request.user.is_authenticated else None
        service = ContentModerationService()
        result = service.moderate_text(text, author=author)

        return JsonResponse(result)


@method_decorator(csrf_exempt, name="dispatch")
class UserInterestProfileView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required"}, status=401)

        profile, _ = UserInterestProfile.objects.get_or_create(user=request.user)
        return JsonResponse(
            {
                "user": request.user.username,
                "topics": profile.topics,
                "has_vector": bool(profile.interest_vector),
                "updated_at": profile.updated_at.isoformat(),
            }
        )

    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required"}, status=401)

        try:
            body = json.loads(request.body)
            topics = body.get("topics", [])
            if not isinstance(topics, list):
                return JsonResponse(
                    {"error": "topics must be a list of strings"}, status=400
                )
        except Exception:
            return JsonResponse({"error": "Invalid JSON body"}, status=400)

        ranker = FeedRanker()
        profile = ranker.update_user_interest_vector(request.user, topics)

        return JsonResponse(
            {
                "user": request.user.username,
                "topics": profile.topics,
                "has_vector": bool(profile.interest_vector),
                "dimensions": len(profile.interest_vector),
                "updated_at": profile.updated_at.isoformat(),
            }
        )
