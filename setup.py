from pathlib import Path

from setuptools import find_packages, setup

HYPHEN_E_DOT = "-e ."


def get_requirements(file_path: str) -> list[str]:
    requirements = Path(file_path).read_text().splitlines()
    return [req for req in requirements if req and req != HYPHEN_E_DOT]


setup(
    name="shl_agent",
    version="0.0.1",
    author="Abhilesh",
    author_email="singhrathor753@gmail.com",
    packages=find_packages(),
    install_requires=get_requirements("requirements.txt"),
)
