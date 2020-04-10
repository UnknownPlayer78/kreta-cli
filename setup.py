from setuptools import setup
import kreta

f = open("README.md")
desc = f.read()
f.close()

setup(
    name='kreta',
    version=kreta.__version__,
    description="KRÉTA Ellenörző CLI",
    long_description="",
    author='UnknownPlayer78',
    author_email='',
    license="MIT",
    keywords="e-kreta kreta cli kreta-cli",
    packages=['kreta'],
    scripts=[
        'bin/kreta',
    ]
)
