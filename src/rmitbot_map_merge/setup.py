from setuptools import find_packages, setup
from glob import glob
import os

package_name = 'rmitbot_map_merge'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
    (
        'share/ament_index/resource_index/packages',
        ['resource/' + package_name],
    ),
    (
        os.path.join('share', package_name),
        ['package.xml'],
    ),
    (
        os.path.join('share', package_name, 'launch'),
        glob('launch/*.py'),
    ),
    (
        os.path.join('share', package_name, 'config'),
        glob('config/*.yaml'),
    ),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ben',
    maintainer_email='locnguyenthanh2411@gmail.com',
    description='Multi-robot occupancy grid map merging package',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
    'console_scripts': [
        'map_merge_node = rmitbot_map_merge.map_merge_node:main',
    ],
    },
)
