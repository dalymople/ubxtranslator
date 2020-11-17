from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(name='ubxtranslator',
      version='0.2.1',
      description='A lightweight python library for translating UBX packets',
      long_description=readme(),
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Programming Language :: Python :: 3',
          'Topic :: Communications'
      ],
      url='http://github.com/dalymople/ubxtranslator',
      author='Dalymople',
      author_email='dalymople@gmail.com',
      license='GNU GPL v3',
      packages=['ubxtranslator'],
      zip_safe=False,
      test_suite='nose.collector',
      tests_require=['nose'],
      )
