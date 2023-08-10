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

from django.db.models import *
from django.conf import settings
from django.contrib.auth.models import User
from django.template import Context,Template
from django.utils.timezone import now
from datetime import date

# locale = settings.LOCALE_DATE

class Page(Model):
    name = CharField(default='!#',max_length=50)
    content = TextField(default='')
    user = ForeignKey(User,related_name='+', on_delete=CASCADE)
    date = DateTimeField(auto_now_add=True)
    def token(self): return self.name[:2]
    def name_trimmed(self): return self.name[2:]
    # def month(self): return locale[self.date.month-1]


