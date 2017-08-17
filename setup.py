from setuptools import find_packages, setup

setup(
    name='aptos',
    version='1.0.1',
    url='https://github.com/pennsignals/aptos',
    author='Jason Walsh',
    author_email='jason.walsh@uphs.upenn.edu',
    maintainer='Jason Walsh',
    packages=find_packages(),
    setup_requires=['nose'],
    tests_require=['coverage'],
    python_requires='>=3.5',
    entry_points={
        'console_scripts': ['aptos = aptos.__main__:main'],
    },
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
    ],
    license='Apache',
    keywords=['json-schema', 'avro', 'validation', 'data-interchange']
)
