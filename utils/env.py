from utils.custom_log_format import logger

info = logger().info
warn = logger().warning
error = logger().error
debug = logger().debug
exception = logger().exception


FOLDERS = [
        'folders',
        'to',
        'check'
]
USER_PASSWD_LIST = [
        ('email', 'passwd')
    ]