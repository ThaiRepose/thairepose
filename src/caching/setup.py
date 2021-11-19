from setuptools import setup
setup(
    name='TR-caching',
    version='0.1.0',
    py_modules=['main'],
    install_requires=[
        'Click',
    ],
    entry_points={
        'console_scripts': [
            'tr-caching = main:cli',
        ],
    },
)
