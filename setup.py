from setuptools import setup, find_packages


setup(
    name='subscity',
    version='0.1',
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    author='Max Danilov',
    author_email='contact@maxdanilov.ru',
    description='.',
    long_description='.',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Information Technology',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7'
    ],
    package_dir={'subscity': 'subscity'},
    packages=find_packages()
)
