import setuptools
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


def dependencies():
    project_path = os.path.dirname(os.path.realpath(__file__))
    requirement_path = os.path.join(project_path, 'requirements.txt')
    install_requires = []

    if os.path.isfile(requirement_path):
        with open(requirement_path) as f:
            install_requires = f.read().splitlines()

    return install_requires


setuptools.setup(
    name="PyTextNow",
    version="2.0.0",
    author="Leo Wu-Gomez",
    author_email="leojwu18@gmail.com",
    description="Texting python package which utilizes TextNow.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/leogomezz4t/PyTextNow_API",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    include_package_data=True,
    install_requires=dependencies(),
)
