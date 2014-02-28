#
# This file is part of Efforia project.
#
# Copyright (C) 2011-2013 William Oliveira de Lagos <william@efforia.com.br>
#
# Efforia is free software: you can redistribute it and/or modify
# it under the terms of the Lesser GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Efforia is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Efforia. If not, see <http://www.gnu.org/licenses/>.
#

from django.conf.urls import patterns,url,include

urlpatterns = patterns('feedly.views',    
    (r'^mosaic','mosaic'),
    (r'^basketclean','basketclean'),
    (r'^basket','basket'),
    (r'^pagseguro/cart','pagsegurocart'),
    (r'^pagseguro','pagseguro'),
    (r'^paypal/cart','paypalcart'),
    (r'^paypal','paypal'),
    (r'^pages','page'),
    (r'^pageview','pageview'),
    (r'^pageedit','pageedit'),
    (r'^deadlines','deadlines'),
)
