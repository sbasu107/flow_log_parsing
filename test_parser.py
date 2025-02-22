import unittest
import os
import random
from parser import open_flowlog, open_lt

class TestParser(unittest.TestCase):
    def setUp(self):
        self.test_flowlog = "test_flowlog.txt"
        self.test_lookuptable = "test_lookuptable.txt"
        
    def tearDown(self):
        if os.path.exists(self.test_flowlog):
            os.remove(self.test_flowlog)
        if os.path.exists(self.test_lookuptable):
            os.remove(self.test_lookuptable)

    def test_input_files_ascii(self):
        """Test that files contain only ASCII characters"""
        input_files = ["flowlog.txt", "lookuptable.txt"]
        for i in range(len(input_files)):
            try:
                with open(input_files[i], "r", encoding="ascii") as f:
                    content = f.read()
                is_ascii = True
            except UnicodeDecodeError:
                is_ascii = False
        self.assertTrue(is_ascii, "Input files should contain only ASCII characters")

    def test_flowlog_size_limit(self):
        """Test that the flowlog can handle files up to 10MB"""
        ten_mb = 10 * 1024 * 1024
        log_entry = "2 123456789012 eni-0a1b2c3d 10.0.1.201 198.51.100.2 443 49153 6 25 20000 1620140761 1620140821 ACCEPT OK\n"
        
        with open(self.test_flowlog, "w") as f:
            while os.path.getsize(self.test_flowlog) < ten_mb:
                f.write(log_entry)
                
        try:
            result = open_flowlog(self.test_flowlog)
            can_process_large_file = True
        except Exception:
            can_process_large_file = False
            
        self.assertTrue(can_process_large_file, "Should handle 10MB files")
        self.assertTrue(os.path.getsize(self.test_flowlog) >= ten_mb, "File should be at least 10MB")

    def test_lookup_table_capacity(self):
        """Test that lookup table can handle 10000 mappings"""
        with open(self.test_lookuptable, "w") as f:
            f.write("dstport,protocol,tag\n")
            for i in range(10000):
                port = i + 1
                protocol = "tcp"
                tag = f"tag_{i}"
                f.write(f"{port},{protocol},{tag}\n")
                
        try:
            result = open_lt(self.test_lookuptable)
            entries_count = len(result)
        except Exception as e:
            self.fail(f"Failed to process lookup table: {str(e)}")

        self.assertEqual(entries_count, 10000, "Should handle 10000 mappings")

    def test_same_tag_multiple_ports(self):
        """
        Test that the same tag can be mapped to multiple port/protocol combos
        """
        with open(self.test_lookuptable, "w") as f:
            f.write("dstport,protocol,tag\n")
            for i in range(10):
                port = 10000 + i
                protocol = random.choice(["tcp", "udp"])
                tag = random.choice(["tagA", "tagB", "tagC"])
                f.write(f"{port},{protocol},{tag}\n")

        try:
            result = open_lt(self.test_lookuptable)
            self.assertEqual(len(result), 10, "There should be 10 unique port/protocol combos")
            values = list(result.values())
            tagA_count = values.count("tagA")
            tagB_count = values.count("tagB")
            self.assertTrue(tagA_count > 1 or tagB_count > 1, "At least one tag should repeat")
        except Exception as e:
            self.fail(f"Failed to process repeated tag for multiple entries: {str(e)}")

    def test_protocol_case_insensitivity(self):
        """Ensure that the lookup table parsing is case-insensitive for the protocol field."""
        with open(self.test_lookuptable, "w") as f:
            f.write("dstport,protocol,tag\n")
            f.write("80,TCP,tagA\n")
            f.write("443,TcP,tagB\n")
            f.write("53,UDP,tagC\n")
            f.write("67,Udp,tagD\n")
            f.write("1,ICMP,tagE\n")
            f.write("2,IcMp,tagF\n")

        try:
            result = open_lt(self.test_lookuptable)
            self.assertEqual(len(result), 6, "Should parse 6 entries despite protocol case differences")

            self.assertIn(("80", "6"), result, "TCP as upper should map to '6'")
            self.assertIn(("443", "6"), result, "Mixed-case 'TcP' should map to '6'")
            self.assertIn(("53", "17"), result, "UDP as uppercase should map to '17'")
            self.assertIn(("1", "1"), result, "ICMP should map to '1'")
        except Exception as e:
            self.fail(f"Case-insensitive protocol test failed: {str(e)}")

if __name__ == '__main__':
    unittest.main()