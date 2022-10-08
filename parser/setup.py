from setuptools import setup

requires = [req for req in open('requirements.txt').read().split('\n') if req.strip()]
test_requirements = [req for req in open('requirements-test.txt').read().split('\n') if req.strip()]

setup(
    name='openfoodfacts_taxonomy_parser',
    version='0.1.0',
    description='Taxonomy Parser written in Python for Open Food Facts',
    author='Pierre Slamich',
    author_email='pierre@openfoodfacts.org',
    url='https://world.openfoodfacts.org',
    packages=['openfoodfacts_taxonomy_parser', ],
    package_dir={'openfoodfacts_taxonomy_parser': 'openfoodfacts_taxonomy_parser'},
    install_requires=requires,
    extras_require={
    },
    test_suite='tests',
    tests_require=test_requirements,
)