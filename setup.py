import os

from setuptools import setup


def package_data(pkg, roots):
    data = []
    for root in roots:
        for dirname, _, files in os.walk(os.path.join(pkg, root)):
            for fname in files:
                data.append(os.path.relpath(os.path.join(dirname, fname), pkg))

    return {pkg: data}


setup(
    name='hcjlivedit-xblock',
    version='0.1',
    description='hcjlivedit XBlock',
    license='UNKNOWN',
    packages=[
        'hcjlivedit',
    ],
    install_requires=[
        'XBlock',
    ],
    entry_points={
        'xblock.v1': [
            'hcjlivedit = hcjlivedit:HtmlCssJsLiveEditorXBlock',
        ]
    },
    package_data=package_data("hcjlivedit", ["static", "public"]),
)
