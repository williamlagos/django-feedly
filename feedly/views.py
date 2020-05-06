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

from django.http import HttpResponse as response
from django.http import JsonResponse
from django.views import View

from .feed import Mosaic,Pages
from .core import Feedly

import logging, urllib.parse

class BoardsView(View):
    def get(self, request):
        return JsonResponse({'boards': 'success'})

logger = logging.getLogger("feedly.views")

def profileview(request,name='me'):
    e = Feedly()
    if request.method == 'GET':
        return e.profile_view(request,name)

def pageview(request):
    p = Pages()
    if request.method == 'GET':
        return p.page_view(request)
    
def pageedit(request):
    p = Pages()
    if request.method == 'GET':
        return p.edit_page(request)
    elif request.method == 'POST':
        return p.save_page(request)

def page(request):
    p = Pages()
    if request.method == 'GET':
        return p.view_page(request)
    elif request.method == 'POST':
        return p.create_page(request)

def mosaic(request):
    m = Mosaic()
    if request.method == 'GET':
        return m.view_mosaic(request)

def deadlines(request):
    m = Mosaic()
    if request.method == 'GET':
        return m.deadlines(request)

def main(request):
    e = Feedly()
    if request.method == 'GET':
        return e.start(request)
    elif request.method == 'POST':
        return e.external(request)