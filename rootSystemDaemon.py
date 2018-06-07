import socket
import os
from kassensystem.lib.readconfig import config
import debinterface


SOCK_PATH = config.get('general', 'root_worker_sock_path')


def get_adapter_name():
    adapter_name = config.get('ethernet', 'port', fallback=None)
    if adapter_name is None:
        raise ValueError('Ethernet Port not configured')
    return adapter_name


def create_interface(name):
    options = {
        'addrFam': 'inet',
        'name': name,
        'source': 'manual',
    }
    interfaces = debinterface.Interfaces()
    interfaces.addAdapter(options)
    interfaces.writeInterfaces()
    interfaces.updateAdapters()


def restart_networking(name):
    os.system('ip addr flush dev {}'.format(name))
    os.system('systemctl restart networking')


def main():

    if os.path.exists(SOCK_PATH):
        os.remove(SOCK_PATH)
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.settimeout(5)
    sock.bind(SOCK_PATH)
    sock.listen(5)

    while 1:
        try:
            conn, addr = sock.accept()
            data = conn.recv(1024)

            command_string = data.decode()
            command = command_string.split(' ')

            if command[0] == 'time':
                if len(command) == 2:
                    set_time(int(command[1]))
            if command[0] == 'interface':
                if len(command) >= 2:
                    if command[1] == 'set' and len(command) == 4:
                        activate_interface(command[2], command[3])
                    elif command[1] == 'deactivate':
                        deactivate_interface()
        except socket.timeout:
            continue


def set_time(unix_timestamp):
    print('date -s @{}'.format(unix_timestamp))
    os.system('date -s @{}'.format(unix_timestamp))


def deactivate_interface():
    try:
        adapter_name = get_adapter_name()
        interfaces = debinterface.Interfaces()
        adapter = interfaces.getAdapter(adapter_name)
        if adapter is not None:
            interfaces.removeAdapterByName(adapter_name)
        interfaces.writeInterfaces()
        restart_networking(adapter_name)
    except ValueError:
        return


def activate_interface(ip, netmask):
    try:
        adapter_name = get_adapter_name()
        interfaces = debinterface.Interfaces()
        adapter = interfaces.getAdapter(adapter_name)
        if adapter is None:
            create_interface(adapter_name)
            interfaces = debinterface.Interfaces()
            adapter = interfaces.getAdapter(adapter_name)
        adapter.setAddressSource('static')
        adapter.setAddress(ip)
        adapter.setNetmask(netmask)
        adapter.setAuto(True)
        interfaces.writeInterfaces()
        restart_networking(adapter_name)
    except ValueError:
        return


if __name__ == '__main__':
    # deactivate_interface()
    # activate_interface('10.0.1.3', '255.255.255.0')
    main()
