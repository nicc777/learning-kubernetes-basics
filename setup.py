from setuptools import setup, find_packages
from os import path
from io import open

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='cool-app',
    version='0.0.1',
    description='An example Flask project, deployed in Docker for testing Kubernetes',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://localhost:5000/',
    author='Nico Coetzee',
    author_email='nicc777@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    keywords='flask cognito docker kubernetes',
    #package_dir={'': 'src'},  
    #packages=find_packages(where='src'),  
    packages=find_packages(),  
    include_package_data=True,
    install_requires=['Flask', 'cognitojwt', 'Flask-Cognito', 'gunicorn'],
    python_requires='>=3.*, <4',
    extras_require={  
        'dev': ['check-manifest'],
        'test': ['coverage'],
    },
    # entry_points={  
    #     'console_scripts': [
    #         'sample=sample:main',
    #     ],
    # },
    # project_urls={  
    #     'Bug Reports': 'https://localhost',
    #     'Source': 'https://localhost',
    # },
)
