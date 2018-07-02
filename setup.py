from setuptools import setup, find_packages

setup(
    name="perfsonar_data_helper",
    version="0.3",
    author="GEANT",
    author_email="swd@geant.org",
    description="wrapper for pscheduler i/o",
    url="https://github.com/erik-geant/perfsonar-data-helper",
    packages=find_packages(),
    install_requires=[
        "flask",
        "flask-cors",
        "requests",
        "requests-futures",
        "jsonschema"
    ]
)

