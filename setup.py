from setuptools import setup, find_packages

setup(name='winnow',
    version='0.1',
    description='Product family publishing and manipulation',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7.6',
        'Intended Audience :: Manufacturing',
        'License :: Public Domain'
    ],
    author='Paul Harter',
    author_email='username: paul, domain: opendesk.cc',
    requires=['jsonschema'],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False)

