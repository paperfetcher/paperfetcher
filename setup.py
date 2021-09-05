from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("VERSION", "r") as vh:
    version = vh.read()
version = version.strip()

setup(name='paperfetcher',
      python_requires='>3.7',
      version=version,
      author='Akash Pallath',
      author_email='apallath@seas.upenn.edu',
      description='Python package to mine papers for systematic reviews.',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://github.com/paperfetcher/paperfetcher',
      packages=['paperfetcher'],
      install_requires=[
          'requests',
          'tqdm',
          'pandas',
          'openpyxl',
          'pytest'
      ],)
