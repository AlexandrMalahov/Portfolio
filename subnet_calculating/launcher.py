"""Python 3.7. Check arguments of command line and parse file with IPs. Main module."""
import argparse
import os.path
import re
from subnet_calculating import subnet_IPv4
from subnet_calculating import subnet_IPv6


def check_version(version):
    """Check version value."""
    try:
        version = int(version)  # 'version' value must be integer.
    except ValueError:
        raise ValueError('Version value must be integer.')
    if version == 4 or version == 6:  # We have two IP versions.
        return version
    else:
        raise ValueError('Version value must be 4 or 6.')


def check_file(file):
    """Check if file exists."""
    existence = os.path.exists(file)  # Checking file for existable
    if existence:
        return file
    else:
        raise FileNotFoundError('File "{}" does not exist.'.format(file))


def check_ip(ip):
    """Check ipv4."""
    try:
        ip = list(map(int, ip.split('.')))  # Transformation octets to int type for checking correct value.
    except ValueError:
        return False
    for octet in ip:
        if 0 <= octet <= 255:  # Octet value must be between 0 and 255
            return True
        else:
            return False


def get_query_params_from_command_line():
    """Parse and check arguments from command line."""
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', help='input path/name of text file with IP group.')
    parser.add_argument('-v', '--version', help='input IP version (4 or 6).')
    args = parser.parse_args()
    return {'file': check_file(args.file), 'version': check_version(args.version)}


def parse_file_data(query_params):
    """Parse file data. Exclude incorrect IPs. Return first ip and last ip."""
    regex = r'\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}' if query_params['version'] == 4 else \
        r'(([0-9a-fA-F]{0,4}:){1,7}[0-9a-fA-F]{0,4})'
    with open(query_params['file'], 'r') as f:
        data = re.findall(regex, f.read())
    cleaned_ips = []  # List for valid IPs.
    if query_params['version'] == 4:
        for ip in data:
            if check_ip(ip):  # IP validation.
                cleaned_ips.append(ip)
    else:
        for ip in data:
            cleaned_ips.append(ip[0])
    return {'first_ip': cleaned_ips[0], 'last_ip': cleaned_ips[-1]}


if __name__ == '__main__':
    QUERY_PARAMS = get_query_params_from_command_line()
    IPS = parse_file_data(QUERY_PARAMS)
    if QUERY_PARAMS['version'] == 4:
        MASK = subnet_IPv4.get_mask(subnet_IPv4.get_bin_ips(IPS))
        print('Result net: {address}/{mask}'.format(
            address=subnet_IPv4.get_address(MASK['octet'], IPS['first_ip']), mask=MASK['mask']))
    else:
        FIRST_IP = subnet_IPv6.get_full_ip(IPS['first_ip'])
        LAST_IP = subnet_IPv6.get_full_ip(IPS['last_ip'])
        MASK = subnet_IPv6.get_mask(FIRST_IP, LAST_IP)
        print('Result net: {address}/{mask}'.format(
            address=subnet_IPv6.get_address(FIRST_IP, MASK['hextet_num']), mask=MASK['mask']))
