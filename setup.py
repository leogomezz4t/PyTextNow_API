import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="TNAPI",
    version="0.0.1",
    author="Leo Wu-Gomez",
    author_email="leojwu18@gmail.com",
    description="Texting python package which utilizes TextNow.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/WuGomezCode/TextNow-API",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    include_package_data=True
)