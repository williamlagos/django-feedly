#!/usr/bin/python
# -*- coding:utf-8 -*-
#
# This file is part of Efforia Open Source Initiative.
#
# Copyright (C) 2011-2014 William Oliveira de Lagos <william@efforia.com.br>
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

from django.forms import Form,CharField

class BasketForm(Form):
    business = CharField(max_length=100)
    notify_url = CharField(max_length=100)
    return_url = CharField(max_length=100)
    cancel_return = CharField(max_length=100)
    currency_code = CharField(max_length=10)
    def render(self): return ''
    def form(self): return ''