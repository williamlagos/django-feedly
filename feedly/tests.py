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
from datetime import timedelta
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.utils.timezone import now

from .ai import GeminiEmbeddingService, cosine_similarity
from .models import ContentEmbedding, ModerationRecord, Page, UserInterestProfile
from .moderation import ContentModerationService
from .ranking import FeedRanker


class BlocksViewTest(TestCase):
    def test_blocks_get(self):
        client = Client()
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data, {"blocks": "success"})


class PageListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        Page.objects.create(name="!#First Page", content="Hello world", user=self.user)
        Page.objects.create(
            name="!#Second Page", content="Another page", user=self.user
        )

    def test_list_pages(self):
        response = self.client.get("/pages/")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("pages", data)
        self.assertEqual(len(data["pages"]), 2)

    def test_list_pages_structure(self):
        response = self.client.get("/pages/")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        page = data["pages"][0]
        self.assertIn("id", page)
        self.assertIn("name", page)
        self.assertIn("content", page)
        self.assertIn("date", page)

    def test_create_page_requires_auth(self):
        response = self.client.post(
            "/pages/",
            json.dumps({"name": "New Page", "content": "Content"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)

    def test_create_page_authenticated(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.post(
            "/pages/",
            json.dumps({"name": "New Page", "content": "Content"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.content)
        self.assertEqual(data["name"], "New Page")
        self.assertEqual(data["content"], "Content")

    def test_create_page_missing_name(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.post(
            "/pages/",
            json.dumps({"content": "Content"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_create_page_invalid_json(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.post(
            "/pages/",
            "not json",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_create_page_rejected_by_moderation(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.post(
            "/pages/",
            json.dumps(
                {
                    "name": "Crypto scam",
                    "content": "claim your airdrop at http://scam.xyz double your bitcoin",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn("error", data)


class PageDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.page = Page.objects.create(
            name="!#Test Page", content="Test content", user=self.user
        )

    def test_get_page(self):
        response = self.client.get("/pages/%d/" % self.page.id)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["name"], "Test Page")
        self.assertEqual(data["content"], "Test content")

    def test_get_nonexistent_page(self):
        response = self.client.get("/pages/99999/")
        self.assertEqual(response.status_code, 404)

    def test_update_page_requires_auth(self):
        response = self.client.put(
            "/pages/%d/" % self.page.id,
            json.dumps({"name": "Updated", "content": "Updated content"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)

    def test_update_page_authenticated(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.put(
            "/pages/%d/" % self.page.id,
            json.dumps({"name": "Updated", "content": "Updated content"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["name"], "Updated")
        self.assertEqual(data["content"], "Updated content")

    def test_delete_page_requires_auth(self):
        response = self.client.delete("/pages/%d/" % self.page.id)
        self.assertEqual(response.status_code, 401)

    def test_delete_page_authenticated(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.delete("/pages/%d/" % self.page.id)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["status"], "deleted")
        self.assertFalse(Page.objects.filter(id=self.page.id).exists())


class GeminiEmbeddingServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="author1", password="pw")
        self.page1 = Page.objects.create(
            name="!#Django AI",
            content="Building smart apps with Django and Gemini",
            user=self.user,
        )
        self.page2 = Page.objects.create(
            name="!#Gardening Tips",
            content="How to grow organic tomatoes and basil",
            user=self.user,
        )

    def test_cosine_similarity(self):
        v1 = [1.0, 0.0, 0.0]
        v2 = [1.0, 0.0, 0.0]
        v3 = [0.0, 1.0, 0.0]
        self.assertAlmostEqual(cosine_similarity(v1, v2), 1.0)
        self.assertAlmostEqual(cosine_similarity(v1, v3), 0.0)
        self.assertEqual(cosine_similarity([], v2), 0.0)

    def test_fallback_embedding_generation(self):
        service = GeminiEmbeddingService()
        vec1 = service.generate_embedding("Django AI")
        vec2 = service.generate_embedding("Django AI")
        vec3 = service.generate_embedding("Gardening Tips")

        self.assertEqual(vec1, vec2)
        self.assertEqual(len(vec1), GeminiEmbeddingService.FALLBACK_DIMENSIONS)
        self.assertGreater(cosine_similarity(vec1, vec2), 0.99)
        self.assertLess(cosine_similarity(vec1, vec3), 0.99)

    def test_embed_object_and_search_similar(self):
        service = GeminiEmbeddingService()
        emb1 = service.embed_object(self.page1)
        emb2 = service.embed_object(self.page2)

        self.assertIsInstance(emb1, ContentEmbedding)
        self.assertEqual(emb1.content_object, self.page1)

        results = service.search_similar("Django Gemini", top_k=5)
        self.assertGreaterEqual(len(results), 1)
        top_result = results[0]
        self.assertEqual(top_result["object"], self.page1)
        self.assertGreater(top_result["score"], 0.0)

    def test_live_mocked_gemini_client(self):
        service = GeminiEmbeddingService(api_key="fake-test-key")
        mock_client = MagicMock()
        mock_embedding = MagicMock()
        mock_embedding.values = [0.1, 0.2, 0.3, 0.4]
        mock_client.models.embed_content.return_value = MagicMock(
            embeddings=[mock_embedding]
        )
        service.client = mock_client

        vec = service.generate_embedding("Test prompt")
        self.assertEqual(vec, [0.1, 0.2, 0.3, 0.4])
        mock_client.models.embed_content.assert_called_once()


class ContentModerationServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test_author", password="pw")
        self.reviewer = User.objects.create_user(
            username="moderator", password="pw", is_staff=True
        )
        self.page = Page.objects.create(
            name="!#Harmless post",
            content="A great day for open source",
            user=self.user,
        )

    def test_safe_content(self):
        service = ContentModerationService()
        result = service.moderate_text(
            "Welcome to the community! Hope you enjoy our articles."
        )
        self.assertEqual(result["status"], ModerationRecord.STATUS_APPROVED)
        self.assertTrue(service.is_safe("Welcome to the community!"))

    def test_spam_detection(self):
        service = ContentModerationService()
        result = service.moderate_text(
            "Double your bitcoin now! Free money guaranteed at telegram: @scam"
        )
        self.assertIn(
            result["status"],
            [ModerationRecord.STATUS_FLAGGED, ModerationRecord.STATUS_REJECTED],
        )
        self.assertIn("spam", result["categories_flagged"])
        self.assertFalse(service.is_safe("Double your bitcoin now!"))

    def test_toxicity_detection(self):
        service = ContentModerationService()
        result = service.moderate_text("You idiot, I hate you so much")
        self.assertIn(
            result["status"],
            [ModerationRecord.STATUS_FLAGGED, ModerationRecord.STATUS_REJECTED],
        )
        self.assertIn("toxicity", result["categories_flagged"])

    def test_moderate_object_auto_quarantine(self):
        toxic_page = Page.objects.create(
            name="!#Toxic post",
            content="You moron, fraudster and scam artist!",
            user=self.user,
        )
        service = ContentModerationService()
        record = service.moderate_object(toxic_page, auto_quarantine=True)

        self.assertTrue(record.is_quarantined)
        self.assertIn(
            record.status,
            [ModerationRecord.STATUS_FLAGGED, ModerationRecord.STATUS_REJECTED],
        )

        # Reviewer manually approves it
        reviewed = service.review_record(
            record,
            reviewer=self.reviewer,
            new_status=ModerationRecord.STATUS_APPROVED,
            reason="False positive",
        )
        self.assertFalse(reviewed.is_quarantined)
        self.assertEqual(reviewed.status, ModerationRecord.STATUS_APPROVED)


class FeedRankerTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="tech_guy", password="pw")
        self.user2 = User.objects.create_user(username="chef", password="pw")
        self.viewer = User.objects.create_user(username="viewer", password="pw")

        self.page_recent = Page.objects.create(
            name="!#Python Updates", content="Python 3.13 features", user=self.user1
        )
        self.page_food = Page.objects.create(
            name="!#Pasta Recipe", content="How to make fresh pasta", user=self.user2
        )

        # Embedding setup
        self.embedding_service = GeminiEmbeddingService()
        self.embedding_service.embed_object(self.page_recent)
        self.embedding_service.embed_object(self.page_food)

    def test_chronological_feed_and_quarantine_filter(self):
        ranker = FeedRanker(embedding_service=self.embedding_service)
        feed = ranker.get_chronological_feed(Page.objects.all())
        self.assertEqual(len(feed), 2)

        # Quarantine one page
        mod_service = ContentModerationService()
        mod_service.moderate_object(
            self.page_recent, text="kill yourself bomb recipe", auto_quarantine=True
        )

        feed_filtered = ranker.get_chronological_feed(
            Page.objects.all(), exclude_quarantined=True
        )
        self.assertEqual(len(feed_filtered), 1)
        self.assertEqual(feed_filtered[0], self.page_food)

    def test_trending_feed(self):
        ranker = FeedRanker(embedding_service=self.embedding_service)
        # Give page_food higher engagement
        setattr(self.page_food, "likes_count", 50)
        setattr(self.page_food, "boosts_count", 20)

        trending = ranker.get_trending_feed([self.page_recent, self.page_food])
        self.assertEqual(trending[0]["item"], self.page_food)
        self.assertGreater(trending[0]["score"], trending[1]["score"])

    def test_personalized_feed_with_interests(self):
        ranker = FeedRanker(embedding_service=self.embedding_service)
        # Update viewer's interest vector to tech
        ranker.update_user_interest_vector(
            self.viewer, topics=["Python", "Django", "Coding"]
        )

        personalized = ranker.get_personalized_feed(
            user=self.viewer,
            items=[self.page_recent, self.page_food],
            social_graph_fn=lambda u, a: a == self.user1,
        )
        self.assertEqual(len(personalized), 2)
        # Tech post should rank higher due to topic affinity & social graph
        self.assertEqual(personalized[0]["item"], self.page_recent)


class FeedsApiViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="feed_user", password="password123"
        )
        self.page = Page.objects.create(
            name="!#AI Engineering", content="Deep learning with Python", user=self.user
        )
        GeminiEmbeddingService().embed_object(self.page)

    def test_chronological_feed_view(self):
        res = self.client.get("/feeds/chronological/")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content)
        self.assertEqual(data["strategy"], "chronological")
        self.assertGreaterEqual(data["count"], 1)

    def test_trending_feed_view(self):
        res = self.client.get("/feeds/trending/")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content)
        self.assertEqual(data["strategy"], "trending")

    def test_personalized_feed_view_authenticated(self):
        self.client.login(username="feed_user", password="password123")
        res = self.client.get("/feeds/personalized/")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content)
        self.assertEqual(data["strategy"], "personalized")

    def test_semantic_search_view(self):
        res = self.client.post(
            "/feeds/search/",
            data=json.dumps({"query": "AI Deep learning", "top_k": 5}),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content)
        self.assertIn("results", data)
        self.assertGreaterEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["item"]["name"], "AI Engineering")

    def test_content_moderation_view(self):
        res = self.client.post(
            "/feeds/moderate/",
            data=json.dumps({"text": "Hello world, nice to meet you"}),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content)
        self.assertEqual(data["status"], "approved")

    def test_user_interests_view(self):
        self.client.login(username="feed_user", password="password123")
        res_post = self.client.post(
            "/feeds/interests/",
            data=json.dumps({"topics": ["python", "ai", "machine learning"]}),
            content_type="application/json",
        )
        self.assertEqual(res_post.status_code, 200)
        data_post = json.loads(res_post.content)
        self.assertTrue(data_post["has_vector"])
        self.assertEqual(data_post["topics"], ["python", "ai", "machine learning"])

        res_get = self.client.get("/feeds/interests/")
        self.assertEqual(res_get.status_code, 200)
        data_get = json.loads(res_get.content)
        self.assertEqual(data_get["topics"], ["python", "ai", "machine learning"])
