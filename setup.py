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
    url='https://github.com/UnknownPlayer78/kreta-cli',
    license="MIT",
    keywords="e-kreta kreta cli kreta-cli",
    packages=['kreta'],
    scripts=[
        'bin/kreta',
    ],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ]
)
