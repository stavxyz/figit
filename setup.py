from setuptools import setup, find_packages

dependencies = [
    'argcomplete>=0.6.3',
    'argh>=0.23.3',
    'requests>=2.1.0',
    ]

setup(
    name='gimages',
    description='Upload images to your github enterprise server.',
    keywords='gimages',
    version='1.0',
    entry_points = {'console_scripts': ['gimage=gimage.gimage:main']},
    packages = find_packages(exclude=['tests']),
    author='samstav',
    author_email='smlstvnh@gmail.com',
    install_requires=dependencies,
    license='Apache 2',
    classifiers=["Programming Language :: Python"],
    url='https://github.com/smlstvnh/gimage'
)
