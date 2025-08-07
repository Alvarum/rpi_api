from pathlib import Path
from setuptools import find_packages, setup

ROOT = Path(__file__).parent

# Si quieres leer README para la descripción larga
README = (ROOT / "README.md").read_text(encoding="utf-8")

setup(
    name="guardian_rpi_api",
    version="1.0.0",
    description="API Flask privada para que Grid Guardian se comunique con la Raspberry Pi",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Everseek",
    packages=find_packages(exclude=("tests", "docs")),
    include_package_data=True,
    python_requires=">=3.9",
    install_requires=[
        "Flask>=2.3",
        "python-dotenv>=1.0",
    ],
    entry_points={
        "console_scripts": [
            # Ejecutable de consola para arrancar la API:
            # $ guardian-rpi-api
            "guardian-rpi-api = guardian_rpi_api.app:main",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Flask",
        "License :: Other/Proprietary License",
        "Operating System :: POSIX :: Linux",
    ],
)
