import ast
import re
from setuptools import setup

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('src/quart_cachecontrol/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

testing_dependencies = ['pytest', 'pytest-asyncio']

setup(
    name='Quart-CacheControl',
    version=version,
    url='https://github.com/luckydonald/quart-cachecontrol',
    license='BSD',
    author='Luckydonald',
    author_email='quart-cachecontrol+code@luckydonald.de',
    description='Set Cache-Control headers on the Quart response',
    long_description=open('README.md', 'r').read(),
    long_description_content_type="text/markdown",
    package_dir={'': 'src'},
    packages=['quart_cachecontrol'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Quart',
    ],
    extras_require={'test': testing_dependencies},
    test_requires=testing_dependencies,
    python_requires='>=3.4',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
