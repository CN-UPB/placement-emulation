from setuptools import setup

setup(
    name='place_emu',
    version='0.9',
    license='Apache 2.0',
    description='place_emu is a framework with a generic interface to automatically emulated NFV placements',
    url='https://github.com/CN-UPB/placement-emulation',
    author='Stefan Schneider, Manuel Peuster',
    author_email='stefan.schneider@upb.de, manuel.peuster@upb.de',
    packages=['place_emu'],
    install_requires=[
        "networkx",
        "geopy",
        "pyyaml",
        "numpy",
        "requests"
    ],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'place_emu=place_emu.placement_emulator:main',
        ],
    },
)
