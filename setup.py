# -*- coding: utf-8 -*-
from setuptools import setup


def readme():
	try:
		with open('README.rst') as f:
			return f.read()
	except:
		pass

setup(name='pyinrail',
	version='1.0.0',
	classifiers=[
		'Development Status :: 4 - Beta',
		'License :: OSI Approved :: MIT License',
		'Programming Language :: Python',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.3',
		'Programming Language :: Python :: 3.4',
		'Programming Language :: Python :: 3.5',
		'Programming Language :: Python :: 3.6',
	],
	keywords='indian railways enquiry api wrapper',
	description='Python Wrapper for Indian Railways Enquiry API',
	long_description=readme(),
	url='https://github.com/nikhilkumarsingh/pyinrail',
	author='Nikhil Kumar Singh',
	author_email='nikhilksingh97@gmail.com',
	license='MIT',
	packages=['pyinrail'],
	install_requires=['requests',  'demjson', 'pandas', 'Pillow', 'pytesseract', 'fuzzywuzzy'],
	include_package_data=True,
	zip_safe=False)
