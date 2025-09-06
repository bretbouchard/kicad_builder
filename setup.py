from setuptools import setup, find_packages

setup(
    name="kicad_builder",
    version="0.1",
    packages=find_packages(include=['tools*']),
    install_requires=open('hardware/requirements-dev.txt').read().splitlines(),
    package_data={'': ['*.json', '*.md']},
)
