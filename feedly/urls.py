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

from django.urls import path

from .views import (
    BlocksView,
    ChronologicalFeedView,
    ContentModerationView,
    PageDetailView,
    PageListView,
    PersonalizedFeedView,
    SemanticSearchView,
    TrendingFeedView,
    UserInterestProfileView,
)

urlpatterns = [
    path("", BlocksView.as_view(), name="feedly-blocks"),
    path("pages/", PageListView.as_view(), name="feedly-pages"),
    path("pages/<int:page_id>/", PageDetailView.as_view(), name="feedly-page-detail"),
    path(
        "feeds/chronological/",
        ChronologicalFeedView.as_view(),
        name="feedly-feed-chronological",
    ),
    path("feeds/trending/", TrendingFeedView.as_view(), name="feedly-feed-trending"),
    path(
        "feeds/personalized/",
        PersonalizedFeedView.as_view(),
        name="feedly-feed-personalized",
    ),
    path("feeds/search/", SemanticSearchView.as_view(), name="feedly-semantic-search"),
    path("feeds/moderate/", ContentModerationView.as_view(), name="feedly-moderate"),
    path(
        "feeds/interests/",
        UserInterestProfileView.as_view(),
        name="feedly-user-interests",
    ),
]
