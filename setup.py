from setuptools import setup, find_packages

setup(
    name='securify',
    version='0.0.1',
    packages=find_packages(),
    python_requires='>=3.13',
    install_requires=[
        'py-solc',
        'semantic_version',
        'graphviz',
        'py-etherscan-api'
    ],
    entry_points={
            'console_scripts': [
                'securify = securify.__main__:main'
            ]
    }
)
