from setuptools import setup

setup(name='alexa-goingson',
	version='0.1',
	description='San Francisco Event Recommendations for Amazon Echo',
	url='http://github.com/kazistan/alexa-goingson',
	author='Kazdin, Joshua',
	author_email='joshuakazdin@gmail.com',
	license='MIT',
	packages=['baydata'],
	install_requires=[
	'requests',
	'bs4', 
	're',
	'sys',
	'pandas',
	'argparse',
	],
	zip_safe=False)