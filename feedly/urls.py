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

from django.conf.urls import url,include
from feedly.views import *

urlpatterns = [
    url("^pay/(?P<order_id>\d+)/$", payment_redirect, name="payment_redirect"),
    url("^execute", payment_execute, name="payment_execute"),
    url(r'^mosaic', mosaic),
    url(r'^basketclean', basketclean),
    url(r'^basket', basket),
    url(r'^pagseguro/cart', pagsegurocart),
    url(r'^pagseguro', pagseguro),
    url(r'^paypal/cart', paypalcart),
    url(r'^paypal', paypal),
    url(r'^pages', page),
    url(r'^pageview', pageview),
    url(r'^pageedit', pageedit),
    url(r'^deadlines', deadlines),
]
