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

from django.contrib import admin

from .models import ContentEmbedding, ModerationRecord, Page, UserInterestProfile


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "date")
    search_fields = ("name", "content")


@admin.register(ContentEmbedding)
class ContentEmbeddingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "content_type",
        "object_id",
        "model_name",
        "dimensions",
        "created_at",
    )
    list_filter = ("model_name", "content_type")
    search_fields = ("text_snippet",)


@admin.register(ModerationRecord)
class ModerationRecordAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "content_type",
        "object_id",
        "status",
        "confidence_score",
        "is_quarantined",
        "created_at",
    )
    list_filter = ("status", "is_quarantined", "content_type")
    search_fields = ("content_text", "reason")


@admin.register(UserInterestProfile)
class UserInterestProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "topics", "updated_at")
    search_fields = ("user__username",)
