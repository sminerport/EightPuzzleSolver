from setuptools import setup, find_packages

setup(
    name="eight-puzzle-solver",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
)
