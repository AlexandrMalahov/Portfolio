"""Python 3.7. Defining the subnet and IP group mask. Code works with IPv4."""


def get_bin_ips(ips):
    """Convert IP addresses to binary type."""
    return {'first_ip': ['{:08b}'.format(int(ip)) for ip in ips['first_ip'].split('.')],
            'last_ip': ['{:08b}'.format(int(ip)) for ip in ips['last_ip'].split('.')]}


def get_mask(ip_data):
    """Calculate same binary numbers in ip addresses."""
    first_ip = iter(''.join(ip_data['first_ip']))
    last_ip = iter(''.join(ip_data['last_ip']))
    bit_counter = 0  # Counter of same bits from first and last ip. Quantity of same bits are equal subnet mask.
    while True:
        if next(first_ip) == next(last_ip):
            bit_counter += 1  # While value from first and last ip are same.
        else:
            break  # Cycle is interrupted when the elements are not equal to each other.
    # 'octet' is number of octet where ips have different values.
    return {'mask': bit_counter, 'octet': bit_counter // 8}


def get_address(octet_num, first_ip):
    """Return the subnet address."""
    first_ip = first_ip.split('.')  # Splitting ip to octets for further treatment.
    octet = int(first_ip[octet_num])  # Octet of first ip where ips have different values.
    if octet < 4:  # Minimum subnet must be more or equal 4 bits.
        octet = str(0)
    elif octet % 4 != 0:
        octet = octet - octet % 4  # Rounding to a multiple of 4.
    first_ip[octet_num] = str(octet)
    if octet_num < 3:
        for i in range(octet_num + 1, 3 + 1):
            first_ip[i] = str(0)  # For set subnet address.
    return '.'.join(first_ip)
