#!/usr/bin/python
#
# This file is part of django-feedly project.
#
# Copyright (C) 2011-2020 William Oliveira de Lagos <william.lagos@icloud.com>
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
#

import json

from django.http import JsonResponse
from django.views import View

from .models import Page

PAGE_NAME_PREFIX = '!#'


def page_to_dict(page):
    return {
        'id': page.id,
        'name': page.name_trimmed(),
        'content': page.content,
        'date': page.date.isoformat(),
    }


class BlocksView(View):

    def get(self, request):
        return JsonResponse({'blocks': 'success'})


class PageListView(View):

    def get(self, request):
        pages = Page.objects.all().order_by('-date')
        data = [page_to_dict(p) for p in pages]
        return JsonResponse({'pages': data})

    def post(self, request):
        try:
            body = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({'error': 'Invalid JSON body'}, status=400)
        name = body.get('name', '').strip()
        content = body.get('content', '').strip()
        if not name:
            return JsonResponse({'error': 'name is required'}, status=400)
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        page = Page.objects.create(
            name='%s%s' % (PAGE_NAME_PREFIX, name),
            content=content,
            user=request.user,
        )
        return JsonResponse(page_to_dict(page), status=201)


class PageDetailView(View):

    def get(self, request, page_id):
        try:
            page = Page.objects.get(id=page_id)
        except Page.DoesNotExist:
            return JsonResponse({'error': 'Page not found'}, status=404)
        return JsonResponse(page_to_dict(page))

    def put(self, request, page_id):
        try:
            page = Page.objects.get(id=page_id)
        except Page.DoesNotExist:
            return JsonResponse({'error': 'Page not found'}, status=404)
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        if page.user != request.user:
            return JsonResponse({'error': 'Permission denied'}, status=403)
        try:
            body = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({'error': 'Invalid JSON body'}, status=400)
        name = body.get('name', '').strip()
        content = body.get('content', '').strip()
        if name:
            page.name = '%s%s' % (PAGE_NAME_PREFIX, name)
        if content:
            page.content = content
        page.save()
        return JsonResponse(page_to_dict(page))

    def delete(self, request, page_id):
        try:
            page = Page.objects.get(id=page_id)
        except Page.DoesNotExist:
            return JsonResponse({'error': 'Page not found'}, status=404)
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        if page.user != request.user:
            return JsonResponse({'error': 'Permission denied'}, status=403)
        page.delete()
        return JsonResponse({'status': 'deleted'})

