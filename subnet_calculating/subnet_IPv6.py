"""Python 3.7. Defining the subnet and IP group mask. Code works with IPv6."""
import re


def get_full_ip(ip):
    """Calculate full ip from abbreviated ip."""
    ip = ip.split(':')  # Splitting ip for hextets.
    full_ip = []
    if '' in ip:  # Abbreviation "::" is become '' in list after split ip.
        num_abbreviated_hextets = '0' * (8 - (len(ip)))  # Calculating hextets for change abbreviation "::".
        index = ip.index('')
        for i in num_abbreviated_hextets:
            ip.insert(index, i)  # Determining the position of abbreviated hextets.
    for hextet in ip:
        hex_len = len(hextet)
        if hex_len < 4:
            hextet = '0' * (4 - hex_len) + hextet  # Adding to hextets leading zeros.
        full_ip.append(hextet)
    return ''.join(full_ip)  # Full ip without separator for simplify calculating mask.


def get_mask(first_ip, last_ip):
    """Calculate same bits in first and last ips."""
    first_ip = iter(first_ip)
    last_ip = iter(last_ip)
    bit_counter = 0  # Counting same values in first and last ip.
    while True:
        if next(first_ip) == next(last_ip):
            bit_counter += 1  # While value from first and last ip are same.
        else:
            break  # Cycle is interrupted when the elements are not equal to each other.
    return {'mask': bit_counter * 4, 'hextet_num': bit_counter // 4}


def get_address(first_ip, hextet_num):
    """Return the subnet address."""
    address = ':'.join([first_ip[x:x+4] for x in range(0, len(first_ip) - len(first_ip) % 4, 4)][:hextet_num])
    # Splitting subnet address to hextets
    return re.sub(''.join(re.findall('0000|:0000', address)), '::', address)  # Simplifying full address.
