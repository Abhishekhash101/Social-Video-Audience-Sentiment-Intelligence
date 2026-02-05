from setuptools import setup,find_packages

def get_requirements(filepath):
    with open(filepath) as fobj:
        req=fobj.readlines()
        req =[r.strip() for r in req if r!='-e .']
        return req

setup(
    name="Social Video Audience Sentiment Intelligence",
    version="1.0",
    author="Abhishek Kumar",
    packages=find_packages(),
    install_requires=get_requirements("requirements.txt")
)