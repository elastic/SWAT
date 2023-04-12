from setuptools import setup, find_packages

setup(
    name="swot",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "google-auth",
        "google-auth-oauthlib",
        "google-auth-httplib2",
        "google-api-python-client",
    ],
    entry_points={
        "console_scripts": [
            "swot = swot.main:main",
        ],
    },
)
