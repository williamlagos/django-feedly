=====
Feedly
=====

Feedly is a Django app to create list and grid-based feeds. The
feeds created with this app can have social and e-commerce aspects.

Quick start
-----------

1. Add "feedly" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
        ...
        'feedly',
    )

2. Include the polls URLconf in your project urls.py like this::

    url(r'^feedly/', include('feedly.urls')),

3. Run `python manage.py syncdb` to create the feedly models.

3. Run `python manage.py loaddata fixtures.json` to create the data on feed.

5. Visit http://127.0.0.1:8000/ to view a sample with populated data