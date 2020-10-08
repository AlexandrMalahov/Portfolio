"""Python 3.7. Test module subnet_IPv6.py."""
import unittest
import subnet_IPv6


class TestSubnetIPv6(unittest.TestCase):
    def test_get_full_ip(self):
        """Test function get_full_ip(ip)."""
        self.assertEqual(subnet_IPv6.get_full_ip('ffe0::80:10:0:0'), 'ffe00000000000000080001000000000')
        self.assertNotEqual(subnet_IPv6.get_full_ip('ffff::'), 'ffff0008877000000000000000000000')

    def test_get_mask(self):
        """Test function get_mask(first_ip, last_ip)."""
        self.assertEqual(
            subnet_IPv6.get_mask(
                'ffff0000000000000000000000000000', 'ffff0000000000000000000000110000'), {'mask': 104, 'hextet_num': 6}
        )
        self.assertNotEqual(
            subnet_IPv6.get_mask(
                'ffff0000000000000000000000000000', 'ffff0000000001000000000000110000'), {'mask': 87, 'hextet_num': 2}
        )

    def test_get_address(self):
        """Test function get_address('first_ip, hextet_num)."""
        self.assertEqual(subnet_IPv6.get_address('ffff0000000000000000000000000000', 6), 'ffff::')
        self.assertNotEqual(subnet_IPv6.get_address('ffff0000000000000000000000000111', 8), 'ffff::')


if __name__ == '__main__':
    unittest.main()
