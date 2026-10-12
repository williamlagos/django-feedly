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
import logging
import os
import re
from typing import Any, Dict, List, Optional

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now

from .models import ModerationRecord

logger = logging.getLogger(__name__)


class ContentModerationService:
    """
    Automated content safety and moderation pipeline using Google Gemini models
    with heuristic fallback for offline/development environments.
    """

    DEFAULT_MODEL = "gemini-3.8-flash"
    DEFAULT_THRESHOLD = 0.65

    CATEGORIES = [
        "toxicity",
        "harassment",
        "hate_speech",
        "dangerous_content",
        "spam",
    ]

    # Heuristic patterns for offline testing and baseline fallback
    HEURISTIC_SPAM_PATTERNS = [
        r"buy\s+crypto\s+now",
        r"free\s+money\s+guaranteed",
        r"telegram\s*:\s*@",
        r"whatsapp\s*:\s*\+",
        r"double\s+your\s+bitcoin",
        r"viagra|cialis",
        r"claim\s+your\s+airdrop\s+at\s+http",
    ]
    HEURISTIC_TOXIC_PATTERNS = [
        r"\b(idiot|stupid|moron|bastard|hate\s+you)\b",
        r"\b(scam\s+artist|fraudster)\b",
    ]
    HEURISTIC_DANGER_PATTERNS = [
        r"kill\s+yourself",
        r"bomb\s+recipe",
        r"how\s+to\s+make\s+(poison|explosives)",
    ]

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        threshold: float = DEFAULT_THRESHOLD,
    ):
        self.api_key = (
            api_key
            or getattr(settings, "GEMINI_API_KEY", None)
            or os.environ.get("GEMINI_API_KEY")
        )
        self.model = model or self.DEFAULT_MODEL
        self.threshold = threshold
        self.client = None

        if self.api_key:
            try:
                from google import genai

                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.warning(
                    "Failed to initialize Google GenAI Client for moderation: %s", e
                )

    def _heuristic_moderate(self, text: str) -> Dict[str, Any]:
        """
        Rule-based classifier used when live Gemini API is unreachable or in tests.
        """
        text_lower = text.lower()
        scores = {cat: 0.05 for cat in self.CATEGORIES}
        flagged_cats = []

        # Spam detection
        for pat in self.HEURISTIC_SPAM_PATTERNS:
            if re.search(pat, text_lower):
                scores["spam"] = 0.92
                flagged_cats.append("spam")
                break

        # Toxicity detection
        for pat in self.HEURISTIC_TOXIC_PATTERNS:
            if re.search(pat, text_lower):
                scores["toxicity"] = 0.85
                scores["harassment"] = 0.75
                flagged_cats.extend(["toxicity", "harassment"])
                break

        # Danger detection
        for pat in self.HEURISTIC_DANGER_PATTERNS:
            if re.search(pat, text_lower):
                scores["dangerous_content"] = 0.98
                flagged_cats.append("dangerous_content")
                break

        flagged_cats = list(dict.fromkeys(flagged_cats))  # Deduplicate

        max_score = max(scores.values())
        if max_score >= 0.9:
            status = ModerationRecord.STATUS_REJECTED
            reason = f"Automated rule violation: {', '.join(flagged_cats)}"
            confidence = max_score
        elif max_score >= self.threshold:
            status = ModerationRecord.STATUS_FLAGGED
            reason = f"Potential policy concern: {', '.join(flagged_cats)}"
            confidence = max_score
        else:
            status = ModerationRecord.STATUS_APPROVED
            reason = "Content meets safety criteria."
            confidence = 0.95

        return {
            "status": status,
            "categories_flagged": flagged_cats,
            "safety_scores": scores,
            "confidence_score": round(confidence, 3),
            "reason": reason,
        }

    def moderate_text(self, text: str, author: Optional[User] = None) -> Dict[str, Any]:
        """
        Analyze text content against safety guidelines.
        """
        if self.client:
            prompt = (
                "You are an automated safety and content moderation system for an online social and creator platform. "
                "Analyze the following text against safety policies:\n\n"
                f"--- BEGIN CONTENT ---\n{text}\n--- END CONTENT ---\n\n"
                "Evaluate the content across these 5 categories: [toxicity, harassment, hate_speech, dangerous_content, spam]. "
                "Respond ONLY with a valid JSON object matching this exact schema:\n"
                "{\n"
                '  "status": "approved" | "flagged" | "rejected",\n'
                '  "categories_flagged": ["category1", ...],\n'
                '  "safety_scores": {"toxicity": 0.0, "harassment": 0.0, "hate_speech": 0.0, "dangerous_content": 0.0, "spam": 0.0},\n'
                '  "confidence_score": 0.95,\n'
                '  "reason": "Brief explanation"\n'
                "}"
            )
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                )
                output = response.text.strip()
                if "```json" in output:
                    output = output.split("```json")[1].split("```")[0].strip()
                elif "```" in output:
                    output = output.split("```")[1].split("```")[0].strip()
                parsed = json.loads(output)
                return {
                    "status": parsed.get("status", ModerationRecord.STATUS_APPROVED),
                    "categories_flagged": parsed.get("categories_flagged", []),
                    "safety_scores": parsed.get("safety_scores", {}),
                    "confidence_score": float(parsed.get("confidence_score", 0.9)),
                    "reason": parsed.get("reason", "Gemini AI assessment"),
                }
            except Exception as e:
                logger.error(
                    "Gemini moderation call failed, falling back to heuristics: %s", e
                )

        return self._heuristic_moderate(text)

    def is_safe(self, text: str) -> bool:
        """
        Quick check if a text passes moderation without flagging or rejection.
        """
        result = self.moderate_text(text)
        return result["status"] == ModerationRecord.STATUS_APPROVED

    def moderate_object(
        self,
        obj: Any,
        text: Optional[str] = None,
        author: Optional[User] = None,
        auto_quarantine: bool = True,
    ) -> ModerationRecord:
        """
        Analyze and create an audit ModerationRecord for any model instance.
        """
        if text is None:
            if hasattr(obj, "content"):
                text = obj.content
            elif hasattr(obj, "description"):
                text = obj.description
            else:
                text = str(obj)

        if author is None and hasattr(obj, "user"):
            author = obj.user
        elif author is None and hasattr(obj, "creator"):
            author = getattr(obj.creator, "user", None) or (
                obj.creator if isinstance(obj.creator, User) else None
            )

        mod_result = self.moderate_text(text, author=author)
        content_type = ContentType.objects.get_for_model(obj)

        is_quarantined = auto_quarantine and mod_result["status"] in [
            ModerationRecord.STATUS_FLAGGED,
            ModerationRecord.STATUS_REJECTED,
        ]

        record, _ = ModerationRecord.objects.update_or_create(
            content_type=content_type,
            object_id=obj.pk,
            defaults={
                "author": author,
                "content_text": text,
                "status": mod_result["status"],
                "categories_flagged": mod_result["categories_flagged"],
                "safety_scores": mod_result["safety_scores"],
                "confidence_score": mod_result["confidence_score"],
                "reason": mod_result["reason"],
                "is_quarantined": is_quarantined,
            },
        )
        return record

    def review_record(
        self,
        record: ModerationRecord,
        reviewer: User,
        new_status: str,
        reason: str = "",
    ) -> ModerationRecord:
        """
        Manual moderation override and review action.
        """
        record.status = new_status
        record.reviewed_by = reviewer
        record.reviewed_at = now()
        if reason:
            record.reason = f"{record.reason} | Moderator note: {reason}".strip(" | ")

        if new_status == ModerationRecord.STATUS_APPROVED:
            record.is_quarantined = False
        elif new_status in [
            ModerationRecord.STATUS_REJECTED,
            ModerationRecord.STATUS_FLAGGED,
        ]:
            record.is_quarantined = True

        record.save()
        return record
