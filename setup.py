from setuptools import find_packages, setup

setup(
    name='aptos',
    version='1.0.2',
    url='https://github.com/pennsignals/aptos',
    author='Jason Walsh',
    author_email='jason.walsh@uphs.upenn.edu',
    maintainer='Jason Walsh',
    packages=find_packages(),
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],
    entry_points={
        'console_scripts': [
            'aptos = aptos.__main__:main',
        ],
    },
    license='Apache',
    keywords=[
        'json-schema',
        'avro',
        'validation',
        'data-interchange',
    ],
    python_requires='>=3.5',
)
