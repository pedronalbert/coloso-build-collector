
from distutils.core import setup

setup(name='coloso-builds-collector',
      version='1.0.0',
      description='Recolector de builds profesionales de Coloso',
      author='Alberto Pedron',
      author_email='pedron.albert@gmail.com',
      url='http://www.coloso.net',
      packages=['pick', 'peewee', 'playhouse', 'pydash', 'retrying', 'requests'],
     )