from setuptools import setup

setup(
    name='oboe',
    version='0.2',
    description='Converts an Obsidian vault into HTML',
    url='https://github.com/kmaasrud/oboe',
    author='kmaasrud',
    author_email='kmaasrud@outlook.com',
    license='MIT',
    packages=['oboe'],
    install_requires=[
      'markdown2',
      'regex',
      'pypandoc'
    ],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'oboe=oboe:main'
        ]
    }
)
