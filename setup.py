import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# Allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-feedly',
    version='0.6.8',
    packages=['feedly'],
    include_package_data=True,
    license='LGPLv3 License',
    description='A Django app to create list and grid-based feeds.',
    long_description=README,
    long_description_content_type='text/x-rst',
    url='https://williamlagos.github.io/',
    author='William Oliveira de Lagos',
    author_email='william.lagos@icloud.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
