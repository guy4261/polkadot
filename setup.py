from setuptools import find_packages, setup


install_requires = open("requirements.txt").readlines()

setup(
    name='polkadot',
    version='0.0.1',
    install_requires=install_requires,
    packages=find_packages(where="polkadot"),
    entry_points={
    'console_scripts': [
        'polkadot = polkadot.validate:main',
        ]
    }
)

# 'importlib-metadata; python_version == "3.8"',
