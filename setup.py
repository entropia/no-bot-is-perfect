import os
from setuptools import setup, find_packages


PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

setup(name='no-bot-is-perfect',
	version='0.1',
	author='Joachim Breitner',
	author_email='mail@joachim-breitner.de',
	url='https://github.com/entropia/no-bot-is-perfect',
	packages=find_packages(),
	include_package_data=True,
	description='GPN 14 programming game',
	install_requires=open('%s/nbip_server/requirements.txt' % os.environ.get('OPENSHIFT_REPO_DIR', PROJECT_ROOT)).readlines(),
)
