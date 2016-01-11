try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'eoldas_ng observation tools. A set of tools to ingest Earth Observation data into the eoldas_ng engine.',
    'author': 'J Gomez-Dans',
    'url': 'http://github.com/jgomezdans/eoldas_ng/',
    'author_email': 'j.gomez-dans@ucl.ac.uk',
    'version': '0.1',
    'install_requires': ['numpy','gdal', 'gp_emulator', 'eoldas_ng','nose'],
    'packages': ['eoldas_ng_observations'],
    'scripts': [],
    'name': 'eoldas_ng_observations'
}

setup ( **config )
