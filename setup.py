import setuptools


setuptools.setup(
                 name='portus',
                 version='0.1',
                 author='Harrison Mamin',
                 author_email='hmamin55@gmail.com',
                 description='Export selected jupyter notebook cells to py '
                             'scripts.',
                 packages=setuptools.find_packages(),
                 install_requires=['Click'],
                 entry_points="""[console_scripts]
                                 portus=portus:portus
                              """
)
