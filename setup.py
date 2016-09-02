from setuptools import setup

setup(name='qcauto',
      version='0.1.0',
      description='Tools for automating running quantum chemistry jobs',
      url='http://github.com/peterspackman/qcauto',
      author='Peter Spackman',
      license='GPLv3',
      packages=['qcauto'],
      install_requires=['numpy', 'attrs', 'periodictable', 'jinja2'],
      zip_safe=False,
      test_suite='nose.collector',
      tests_require=['nose']
      )
