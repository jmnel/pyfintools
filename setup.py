import setuptools

with open('README.md', 'r') as f:
    long_description = f.read()

setuptools.setup(
    name='pyfintools',
    version='0.0.1',
    author='Jacques Nel',
    author_email='jmnel92@gmail.com',
    description='Financial tools library',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/jmnel/pyfintools',
    install_requires=[
        'matplotlib>=3.1.3'
        'numpy>=1.19.1',
        'pandas-market-calendars>=1.4.0',
        'pandas>=1.0.1',
        'pycairo>=1.19.1',
        'requests>=2',
    ],
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6'
)
