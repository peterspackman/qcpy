from setuptools import setup

setup(name='qcpy',
      version='0.1.1',
      description='Tools for automating running quantum chemistry jobs',
      url='http://github.com/peterspackman/qcauto',
      author='Peter Spackman',
      license='GPLv3',
      packages=['qcpy'],
      install_requires=['numpy', 'jinja2'],
      zip_safe=False,
      test_suite='nose.collector',
      tests_require=['nose']
)
