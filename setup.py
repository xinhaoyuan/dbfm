from setuptools import setup

setup(
    name = "dbfm",
    description = "An overly simple douban.fm client",
    version = "0.1",
    packages = [ "dbfm" ],
    include_package_data = True,
    author = "Xinhao Yuan",
    author_email = "xinhaoyuan@gmail.com",
    url = "https://github.com/xinhaoyuan/dbfm",
    license = "Apache License 2.0",
    install_requires = [ "requests", "termcolor" ],
    long_description = open("README.md").read(),
    long_description_content_type = "text/markdown",
)
