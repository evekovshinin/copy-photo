from setuptools import setup, find_packages

setup(
    name="copy-photo",
    version="1.1.0",
    packages=find_packages(),
    install_requires=[
        "tqdm>=4.0.0",
    ],
    entry_points={
        'console_scripts': [
            'copy-photo=copy-photo.cli:main',
        ],
    },
    author="Evgeny Vekovshinin",
    description="Tool for copying images from memory cards",
    python_requires=">=3.6",
)
