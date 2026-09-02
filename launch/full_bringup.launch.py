from launch import LaunchDescription
from launch.actions import ExecuteProcess, IncludeLaunchDescription, SetEnvironmentVariable, RegisterEventHandler, TimerAction
from launch.event_handlers import OnProcessStart
from ament_index_python.packages import get_package_share_directory
import os
from launch.substitutions import Command, PathJoinSubstitution
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():

    world = os.path.join(
        get_package_share_directory('obj_navigate'),
        'worlds',
        'warehouse_world.sdf'
    )
    gz_yaml = os.path.join(
        get_package_share_directory('obj_navigate'),
        'config',
        'gz_bridge.yaml'
    )
    urdf_file_path = os.path.join(
        get_package_share_directory('obj_navigate'),
        'urdf',
        '3dmappingrobot.urdf' 
    )
    carto_config = os.path.join(
        get_package_share_directory('obj_navigate'),
        'config'
    )
    robot_description = open( urdf_file_path).read()

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('ros_gz_sim'),
                'launch',
                'gz_sim.launch.py'
            )
        ),
        launch_arguments={
            'gz_args': f'-r {world}'
        }.items()
    )
    robot_state_pub = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[
            {'robot_description': robot_description},
            {'use_sim_time':True}
        ]
    )
    joint_state_pub = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher'
    )
    spawn_entry = Node(
        package='ros_gz_sim',
        executable='create',
        parameters=[{'use_sim_time': True}],
        arguments=[
            '-topic', 'robot_description',
        ]
    )
    cartograph = Node(
        package='cartographer_ros',
        executable='cartographer_node',
        name='cartographer_node',
        output='screen',
        parameters=[{'use_sim_time': True}],
        arguments=[ '-configuration_directory', carto_config,
                    '-configuration_basename', 'cartograph.lua',
        ]
    )
    cartograph_grid = Node(
        package='cartographer_ros',
        executable='cartographer_occupancy_grid_node',
        name='cartographer_occupancy_grid_node',
        output='screen',
        parameters=[{'use_sim_time': True}],
        arguments=['-resolution','0.05',
            '-publish_period_sec','1.0',
        ]
    )
    gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        output='screen',
        parameters=[{'use_sim_time': True}],
        arguments=[
            '/lidar/scan@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan',
            '/camera/image@sensor_msgs/msg/Image@gz.msgs.Image',
            '/camera/depth_image@sensor_msgs/msg/Image@gz.msgs.Image',
            '/camera/camera_info@sensor_msgs/msg/CameraInfo@gz.msgs.CameraInfo',
            '/camera/points@sensor_msgs/msg/PointCloud2[gz.msgs.PointCloudPacked',
            '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
            '/odom@nav_msgs/msg/Odometry@gz.msgs.Odometry',
            '/tf@tf2_msgs/msg/TFMessage@gz.msgs.Pose_V',
        ],
        remappings=[
            ('/lidar/scan','/scan'),
            ('/camera/image','/camera/image'),
            ('/camera/depth_image','/camera/depth_image'),
            ('/camera/camera_info','/camera/camera_info'),
            ('/camera/points','/camera/points'),
        ]
    )
    rviz = Node(
        package="rviz2",
        executable="rviz2",
            parameters=[
            {
                "use_sim_time": True
            }
        ],
        output="screen"
    )


    return LaunchDescription([
        gz_sim,
        robot_state_pub,
        joint_state_pub,
        spawn_entry,
        gz_bridge,
        rviz,
        # cartograph,
        # cartograph_grid
    ])