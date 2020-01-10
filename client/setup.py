import setuptools

with open("docs/intro.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dmaster",
    version="0.0.4",
    author="guyrt",
    author_email="richardtguy84@gmail.com",
    description="A better way to manage your data",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/guyrt/datamaster",
    packages=setuptools.find_packages(),
    install_requires=['peewee', 'gitpython', 'pyyaml', 'requests'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points = {
        'console_scripts': ['dmaster=dm.cmdline.cmds:main'],
    },
)
