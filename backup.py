# -*- coding: utf-8 -*-
import os
import telnetlib
import paramiko
import time
import datetime

def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        print("Directory", directory, "created")
    else:
        print("Directory", directory, "already exists")

def telnet_login(switch):
    tn = telnetlib.Telnet(switch['ip'], switch.get('port', 23))
    tn.read_until(b'Username:')
    tn.write(switch['username'].encode('ascii') + b"\n")
    tn.read_until(b"password:")
    tn.write(switch['password'].encode('ascii') + b"\n")
    print("Successfully telnet logged in to", switch['ip'])
    return tn

def ssh_login(switch):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(switch['ip'], port=switch.get('port', 22), username=switch['username'], password=switch['password'])
    print("Successfully ssh logged in to", switch['ip'])
    return ssh

def execute_telnet_command(connection, command, switch, delay=2):
    connection.write(command.encode('ascii') + b"\n")
    time.sleep(delay)
    output = connection.read_very_eager().decode('ascii')
    print(output)
    today = datetime.date.today()
    filename = f"{switch['hostname']}_{today}.txt"
    with open(filename, 'a') as f:
        f.write(output)

def execute_ssh_command(connection, commands, switch, delay=2):
    channel = connection.invoke_shell()
    for command in commands:
        channel.send(command + '\n')
        time.sleep(delay)
        output = ''
        while channel.recv_ready():
            output += channel.recv(65535).decode('ascii')
            time.sleep(delay)
        print(output)
        today = datetime.date.today()
        filename = f"{switch['hostname']}_{today}.txt"
        with open(filename, 'a') as f:
            f.write(output)

login_functions = {
    'telnet': telnet_login,
    'ssh': ssh_login
}

def login(switch):
    protocol = switch.get('protocol', 'telnet')
    if protocol not in login_functions:
        print("Unknown protocol:", protocol)
        return None
    return login_functions[protocol](switch)

def execute_command(connection, commands, switch, delay=2):
    try:
        if isinstance(connection, telnetlib.Telnet):
            for command in commands:
                execute_telnet_command(connection, command, switch, delay)
        elif isinstance(connection, paramiko.SSHClient):
            execute_ssh_command(connection, commands, switch, delay)
        else:
            print("Unknown connection type")
    except Exception as e:
        print("An error occurred:", str(e))
    finally:
        connection.close()

def exec_backup_config(commands, switches):
    for switch in switches:
        connection = login(switch)
        if connection:
            vendor = switch.get('vendor')
            if vendor in commands:
                execute_command(connection, commands[vendor], switch)
            else:
                print("Unknown vendor:", vendor)

def main():
    commands = {
        'huawei': [
            "screen-length 0 temporary",
            "dis cu",
            "dis version"
        ],
        'cisco': [
            "terminal length 0",
            "show running-config",
            "show version"
        ]
    }
    switches = [
        {'hostname': 'BJ1_I4', 'ip': '172.18.0.42', 'port': 23, 'username': 'tianrj', 'password': 'abc1234', 'vendor': 'huawei', 'protocol': 'telnet'},
        {'hostname': 'BJ1_E15', 'ip': '171.18.0.214', 'port': 22, 'username': 'tianrj', 'password': 'abc1234', 'vendor': 'huawei', 'protocol': 'ssh'}
    ]
    directory = "output"
    create_directory(directory)
    os.chdir(directory)  # ÇÐ»»¹¤×÷Ä¿Â¼
    exec_backup_config(commands, switches)

if __name__ == "__main__":
    main()
