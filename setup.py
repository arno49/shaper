import os
import sys
from setuptools import find_packages, setup
import versioneer


PROJECT_DIR = os.path.normpath(os.path.abspath(os.path.dirname(__file__)))

# allow setup.py to be run from any path
os.chdir(PROJECT_DIR)


with open(os.path.join(PROJECT_DIR, 'README.md')) as readme:
    description = readme.read()


with open(os.path.join(PROJECT_DIR, 'requirements/base')) as req_fd:
    install_requires = req_fd.readlines()

if (sys.version_info > (3, 0)):
    with open(os.path.join(PROJECT_DIR, 'requirements/python3')) as req_fd:
        install_requires += req_fd.readlines()


with open(os.path.join(PROJECT_DIR, 'requirements/test')) as req_fd:
    test_requires = req_fd.readlines()


with open(os.path.join(PROJECT_DIR, 'requirements/debug')) as req_fd:
    debug_requires = req_fd.readlines()


dev_requires = test_requires + debug_requires


setup(
    name='shaper',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    packages=find_packages(),
    include_package_data=True,
    description='Manage application options',
    long_description=description,
    url='https://github.com/arno49/shaper/wiki',
    author='Ivan Bogomazov',
    author_email='ivan.bogomazov@gmail.com',
    install_requires=install_requires,
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Topic :: Utilities',
        'License :: OSI Approved :: Apache Software License',
    ],
    entry_points={
        'console_scripts': [
            'shaper = shaper.cli:main'
        ]
    },
    extras_require={
        'test': test_requires,
        'dev': dev_requires
    }
)
