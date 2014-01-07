from setuptools import setup, find_packages

dependencies = [
    'argcomplete>=0.6.3',
    'argh>=0.23.3',
    'requests>=2.1.0',
    'beautifulsoup4>=4.3.2',
    'xerox>=0.3.1'
    ]

setup(
    name='figit',
    description='Upload images to your github enterprise server.',
    keywords='figit',
    version='1.0.1',
    entry_points = {'console_scripts': ['figit=figit.figit:main']},
    packages = find_packages(exclude=['tests']),
    author='samstav',
    author_email='smlstvnh@gmail.com',
    install_requires=dependencies,
    license='Apache 2',
    classifiers=["Programming Language :: Python"],
    url='https://github.com/smlstvnh/figit'
)
