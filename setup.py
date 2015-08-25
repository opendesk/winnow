from setuptools import setup, find_packages

setup(
    name='winnow',
    version='0.1.2',
    description='Winnow is a JSON-schema based library for publishing and manipulating families of products.',
    url='https://github.com/opendesk/winnow',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Intended Audience :: Manufacturing',
        'License :: Public Domain'
    ],
    author='Paul Harter',
    author_email='username: paul, domain: opendesk.cc',
    license='UNLICENSE',
    install_requires=['jsonschema'],
    packages=find_packages('src'),
    package_data={'': ['*.json']},
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False
)
