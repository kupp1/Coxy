import subprocess

def get_host_machine_uptime():
    return 'host machine ' + subprocess.check_output(['uptime', '-p']).decode()