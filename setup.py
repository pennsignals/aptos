from setuptools import find_packages, setup

setup(
    name='aptos',
    version='1.0.0',
    url='https://github.com/pennsignals/aptos',
    author='Jason Walsh',
    author_email='jason.walsh@uphs.upenn.edu',
    maintainer='Jason Walsh',
    packages=find_packages(),
    tests_require=['nose'],
    test_suite='nose.collector',
    entry_points={
        'console_scripts': ['aptos = aptos.__main__:main'],
    },
    license='License :: OSI Approved :: Apache Software License',
    keywords=['json schema', 'avro', 'validation']
)
