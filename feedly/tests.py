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

from django.contrib.auth.models import User
from django.test import TestCase, Client

from .models import Page


class BlocksViewTest(TestCase):

    def test_blocks_get(self):
        client = Client()
        response = client.get('/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data, {'blocks': 'success'})


class PageListViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass'
        )
        Page.objects.create(name='!#First Page', content='Hello world', user=self.user)
        Page.objects.create(name='!#Second Page', content='Another page', user=self.user)

    def test_list_pages(self):
        response = self.client.get('/pages/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('pages', data)
        self.assertEqual(len(data['pages']), 2)

    def test_list_pages_structure(self):
        response = self.client.get('/pages/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        page = data['pages'][0]
        self.assertIn('id', page)
        self.assertIn('name', page)
        self.assertIn('content', page)
        self.assertIn('date', page)

    def test_create_page_requires_auth(self):
        response = self.client.post(
            '/pages/',
            json.dumps({'name': 'New Page', 'content': 'Content'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 401)

    def test_create_page_authenticated(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(
            '/pages/',
            json.dumps({'name': 'New Page', 'content': 'Content'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.content)
        self.assertEqual(data['name'], 'New Page')
        self.assertEqual(data['content'], 'Content')

    def test_create_page_missing_name(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(
            '/pages/',
            json.dumps({'content': 'Content'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)

    def test_create_page_invalid_json(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(
            '/pages/',
            'not json',
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)


class PageDetailViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass'
        )
        self.page = Page.objects.create(
            name='!#Test Page', content='Test content', user=self.user
        )

    def test_get_page(self):
        response = self.client.get('/pages/%d/' % self.page.id)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['name'], 'Test Page')
        self.assertEqual(data['content'], 'Test content')

    def test_get_nonexistent_page(self):
        response = self.client.get('/pages/99999/')
        self.assertEqual(response.status_code, 404)

    def test_update_page_requires_auth(self):
        response = self.client.put(
            '/pages/%d/' % self.page.id,
            json.dumps({'name': 'Updated', 'content': 'Updated content'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 401)

    def test_update_page_authenticated(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.put(
            '/pages/%d/' % self.page.id,
            json.dumps({'name': 'Updated', 'content': 'Updated content'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['name'], 'Updated')
        self.assertEqual(data['content'], 'Updated content')

    def test_delete_page_requires_auth(self):
        response = self.client.delete('/pages/%d/' % self.page.id)
        self.assertEqual(response.status_code, 401)

    def test_delete_page_authenticated(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.delete('/pages/%d/' % self.page.id)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'deleted')
        self.assertFalse(Page.objects.filter(id=self.page.id).exists())
