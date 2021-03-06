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
        'Programming Language :: Python :: 3.6'
    ],
    package_dir={'subscity': 'subscity'},
    entry_points={
        'console_scripts': [
            'update_base=subscity.scripts:update_base',
            'update_movies=subscity.scripts:update_movies',
            'update_cinemas=subscity.scripts:update_cinemas',
            'update_screenings=subscity.scripts:update_screenings',
            'update_test_fixtures=subscity.scripts:update_test_fixtures',
            'update_test_cinema_fixtures=subscity.scripts:update_test_cinema_fixtures',
            'update_test_movie_fixtures=subscity.scripts:update_test_movie_fixtures',
            'update_test_screening_fixtures=subscity.scripts:update_test_screening_fixtures',
            'update_test_movie_details_fixtures=subscity.scripts:update_test_movie_details_fixtures'
        ]
    },
    packages=find_packages()
)
