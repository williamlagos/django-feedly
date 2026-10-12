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
#
# You should have received a copy of the GNU Lesser General Public License
# along with Feedly. If not, see <http://www.gnu.org/licenses/>.

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Page(models.Model):
    name = models.CharField(default="!#", max_length=50)
    content = models.TextField(default="")
    user = models.ForeignKey(User, related_name="+", on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    def token(self):
        return self.name[:2]

    def name_trimmed(self):
        return self.name[2:]

    def __str__(self):
        return self.name_trimmed()


class ContentEmbedding(models.Model):
    """
    Stores vector embeddings for any Django model instance or generic text.
    """

    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True, blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    content_object = GenericForeignKey("content_type", "object_id")

    model_name = models.CharField(max_length=100, default="gemini-embedding-001")
    embedding = models.JSONField(
        default=list, help_text="List of floats representing the vector embedding"
    )
    text_snippet = models.TextField(
        blank=True,
        default="",
        help_text="Truncated text used to generate the embedding",
    )
    dimensions = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["model_name"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["content_type", "object_id", "model_name"],
                condition=models.Q(content_type__isnull=False),
                name="unique_content_object_embedding",
            )
        ]

    def __str__(self):
        return f"Embedding({self.model_name}, dims={self.dimensions}) for {self.content_object or self.text_snippet[:30]}"


class ModerationRecord(models.Model):
    """
    Audit log and moderation status for content processed by AI safety filters.
    """

    STATUS_APPROVED = "approved"
    STATUS_FLAGGED = "flagged"
    STATUS_REJECTED = "rejected"
    STATUS_PENDING = "pending_review"

    STATUS_CHOICES = [
        (STATUS_APPROVED, "Approved"),
        (STATUS_FLAGGED, "Flagged"),
        (STATUS_REJECTED, "Rejected"),
        (STATUS_PENDING, "Pending Review"),
    ]

    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True, blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    content_object = GenericForeignKey("content_type", "object_id")

    author = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="moderation_records",
    )
    content_text = models.TextField()

    status = models.CharField(
        max_length=30, choices=STATUS_CHOICES, default=STATUS_APPROVED, db_index=True
    )
    categories_flagged = models.JSONField(
        default=list, help_text="Categories triggering moderation: toxicity, spam, etc."
    )
    safety_scores = models.JSONField(
        default=dict, help_text="Confidence scores by category"
    )
    confidence_score = models.FloatField(default=1.0)
    reason = models.TextField(blank=True, default="")
    is_quarantined = models.BooleanField(default=False, db_index=True)

    reviewed_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="moderated_actions",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["status"]),
            models.Index(fields=["is_quarantined"]),
        ]

    def __str__(self):
        return f"ModerationRecord(status={self.status}, quarantined={self.is_quarantined}) for {self.content_object or self.content_text[:30]}"


class UserInterestProfile(models.Model):
    """
    Maintains semantic interest vector and topic tags for personalized feed ranking.
    """

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="feedly_profile"
    )
    topics = models.JSONField(
        default=list,
        help_text="Explicit topic interests selected by or inferred for the user",
    )
    interest_vector = models.JSONField(
        default=list,
        help_text="Aggregated vector representation of user interests",
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"UserInterestProfile({self.user.username}, topics={len(self.topics)})"
