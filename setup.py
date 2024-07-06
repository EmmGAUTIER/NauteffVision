from setuptools import setup, find_packages

setup(
    name='NauteffVision',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        # Liste des dépendances
    ],
    entry_points={
        'NauteffVision/main.py': [
            # Points d'entrée pour les scripts exécutables
        ],
    },
    author='Emmanuel Gautier
    author_email='emmanuel.gautier@free.fr',
    description='Navigation data visualisation and processing',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/EmmGautier/NauteffVision',
    classifiers=[
        # Classifications du projet
        'python', 'Data science', 'signal processing', 'MEMs', 'Navigation'
    ],
)
