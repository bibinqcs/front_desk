# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
#from pip.req import parse_requirements
import re, ast

# get version from __version__ variable in front_desk/__init__.py
_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('requirements.txt') as f:
        install_requires = f.read().strip().split('\n')

with open('front_desk/__init__.py', 'rb') as f:
	version = str(ast.literal_eval(_version_re.search(
	f.read().decode('utf-8')).group(1)))

#requirements = parse_requirements("requirements.txt", session="")

setup(
	name='front_desk',
	version=version,
	description='App for reception',
	author='Quark Cyber Systems',
	author_email='vivek@quarkcs.com',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
	#dependency_links=[str(ir._link) for ir in requirements if ir._link]
)
