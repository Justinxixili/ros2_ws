from setuptools import find_packages, setup

package_name = 'dual_arm_demo'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
    ('share/ament_index/resource_index/packages',
        ['resource/' + package_name]),

    ('share/' + package_name, ['package.xml']),

    # 安装 launch 文件
    ('share/' + package_name + '/launch', [
        'launch/dual_arm_rviz.launch.py',
    ]),

    # 安装 urdf
    ('share/' + package_name + '/urdf', [
        'urdf/marvin_m6_l.urdf',
        'urdf/marvin_m6_r.urdf',
    ]),

    # 安装 meshes（左右臂）
    ('share/' + package_name + '/meshes/left_arm', [
        'meshes/left_arm/Base_L.STL',
        'meshes/left_arm/Link1_L.STL',
        'meshes/left_arm/Link2_L.STL',
        'meshes/left_arm/Link3_L.STL',
        'meshes/left_arm/Link4_L.STL',
        'meshes/left_arm/Link5_L.STL',
        'meshes/left_arm/Link6_L.STL',
        'meshes/left_arm/Link7_L.STL',
    ]),
    ('share/' + package_name + '/meshes/right_arm', [
        'meshes/right_arm/Base_R.STL',
        'meshes/right_arm/Link1_R.STL',
        'meshes/right_arm/Link2_R.STL',
        'meshes/right_arm/Link3_R.STL',
        'meshes/right_arm/Link4_R.STL',
        'meshes/right_arm/Link5_R.STL',
        'meshes/right_arm/Link6_R.STL',
        'meshes/right_arm/Link7_R.STL',
    ]),
],

    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='look',
    maintainer_email='look@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
entry_points={
    'console_scripts': [
        'dual_arm_publisher = dual_arm_demo.dual_arm_publisher:main',
        'pvt_player = dual_arm_demo.pvt_player:main',
        'joint_points_player = dual_arm_demo.joint_points_player:main',
        'getAB = dual_arm_demo.getAB:main',

    ],
},



)
