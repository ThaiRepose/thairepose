from setuptools import setup
setup(
    name='TR-caching',
    version='0.1.0',
    py_modules=['api_caching'],
    install_requires=[
        'Click',
    ],
    entry_points={
        'console_scripts': [
            'tr-caching = api_caching:cli',
        ],
    },
)