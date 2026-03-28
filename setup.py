from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="copy-photo",
    version="1.2.1",
    author="Evgeny Vekovshinin",
    author_email="evgeny@vekovshinin.ru",
    description="Professional photo copying and organization tool with EXIF support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/evekovshinin/copy-photo",
    packages=find_packages(include=["copy_photo", "copy_photo.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Natural Language :: Russian",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Utilities",
    ],
    python_requires=">=3.6",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "copy-photo=copy_photo.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "copy_photo": ["data/*.json"],
    },
    project_urls={
        "Bug Reports": "https://github.com/yourusername/copy-photo/issues",
        "Source": "https://github.com/evekovshinin/copy-photo",
    },
)
