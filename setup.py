from setuptools import setup, find_packages

setup(
    name="pscheduler_proxy",
    version="0.1",
    author="GEANT",
    author_email="swd@geant.org",
    description="wrapper for pscheduler i/o",
    url="https://url",
    packages=find_packages(),
    install_requires=[
        "flask",
        "requests"
    ]
)

