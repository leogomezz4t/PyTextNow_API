import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PyTextNow",
    version="0.0.9",
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
    install_requires=[
          'selenium',
    ],
    python_requires='>=3.6',
    include_package_data=True
)
