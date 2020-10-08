"""Python 3.7. Test module subnet_IPv4.py."""
import unittest
import subnet_IPv4


class TestSubnetIPv4(unittest.TestCase):
    def test_get_bin_ips(self):
        """Test function get_bin_ips(ips)."""
        self.assertEqual(subnet_IPv4.get_bin_ips({'first_ip': '10.168.1.2', 'last_ip': '10.170.3.1'}),
                         {'first_ip': ['00001010', '10101000', '00000001', '00000010'],
                          'last_ip': ['00001010', '10101010', '00000011', '00000001']})
        self.assertNotEqual(subnet_IPv4.get_bin_ips({'first_ip': '2.160.1.2', 'last_ip': '10.170.3.1'}),
                         {'first_ip': ['00000010', '10000000', '00000001', '00000010'],
                          'last_ip': ['00001010', '00000000', '00000011', '00000001']})

    def test_get_mask(self):
        """Test function get_mask(ip_data)."""
        self.assertEqual(subnet_IPv4.get_mask({'first_ip': ['00001010', '11111111', '00000001', '00000010'],
                                               'last_ip': ['00001011', '10101010', '00000011', '00000001']}),
                         {'mask': 7, 'octet': 0})
        self.assertNotEqual(subnet_IPv4.get_mask({'first_ip': ['00011111', '11111111', '00000001', '00000010'],
                                                  'last_ip': ['00001010', '10101000', '00000011', '00000001']}),
                         {'mask': 4, 'octet': 4})

    def test_get_address(self):
        """Test function get_address(octet_num, first_ip)."""
        self.assertEqual(subnet_IPv4.get_address(2, '128.168.12.2'), '128.168.12.0')
        self.assertNotEqual(subnet_IPv4.get_address(1, '0.1.3.68'), '255.1.3.68')


if __name__ == '__main__':
    unittest.main()
