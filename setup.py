from setuptools import setup

setup(name='paperfetcher',
      python_requires='>3.7',
      version='0.0.1',
      author='Akash Pallath',
      author_email='apallath@seas.upenn.edu',
      description='Python package to mine papers for systematic reviews.',
      url='https://github.com/paperfetcher/paperfetcher',
      packages=['paperfetcher'],
      install_requires=[
          'requests',
          'tqdm',
          'pandas',
          'pytest'
      ],)
