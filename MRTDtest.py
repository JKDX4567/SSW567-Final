import unittest
from MRTD import *

class test_MRTD(unittest.TestCase):
    def test_scan_mrz_exists(self):
        self.assertIsNone(scan_mrz())

    def test_query_database_exists(self):
        self.assertIsNone(query_database())

    def test_fletcher16_checksum(self):
        self.assertEqual(fletcher16(b''), 0)
        self.assertEqual(fletcher16(b'ABC123'), 2909)

    def test_calculate_check_digit_basic(self):
        self.assertEqual(calculate_check_digit(""), 0)
        self.assertEqual(calculate_check_digit("123456789"), fletcher16(b"123456789") % 10)
        self.assertEqual(calculate_check_digit("L898902C3"), fletcher16(b"L898902C3") % 10)

    def test_encode_decode_roundtrip(self):
        fields = {
            'document_type': 'P',
            'issuing_country': 'UTO',
            'last_name': 'ERIKSSON',
            'first_name': 'ANNA',
            'middle_name': 'MARIA',
            'passport_number': 'L898902C3',
            'country_code': 'UTO',
            'birth_date': '740812',
            'sex': 'F',
            'expiration_date': '120415',
            'personal_number': 'ZE184226B'
        }
        line1, line2 = encode_mrz(fields)
        decoded = decode_mrz(line1, line2)
        self.assertEqual(decoded['line1']['last_name'], 'ERIKSSON')
        self.assertEqual(decoded['line1']['first_name'], 'ANNA')
        self.assertEqual(decoded['line1']['middle_name'], 'MARIA')
        self.assertEqual(decoded['line2']['passport_number'], 'L898902C3')
        self.assertEqual(decoded['line2']['birth_date'], '740812')

    def test_verify_mrz_valid(self):
        fields = {
            'document_type': 'P',
            'issuing_country': 'UTO',
            'last_name': 'ERIKSSON',
            'first_name': 'ANNA',
            'middle_name': 'MARIA',
            'passport_number': 'L898902C3',
            'country_code': 'UTO',
            'birth_date': '740812',
            'sex': 'F',
            'expiration_date': '120415',
            'personal_number': 'ZE184226B'
        }
        line1, line2 = encode_mrz(fields)
        result = verify_mrz(line1, line2)

        self.assertTrue(result['valid'])

    def test_encoded_mrz_line_lengths(self):
        fields = {
            'document_type': 'P',
            'issuing_country': 'UTO',
            'last_name': 'DOE',
            'first_name': 'JANE',
            'middle_name': '',
            'passport_number': 'A12345678',
            'country_code': 'UTO',
            'birth_date': '900101',
            'sex': 'F',
            'expiration_date': '300101',
            'personal_number': '123456789'
        }
        line1, line2 = encode_mrz(fields)
        self.assertEqual(len(line1), 44)
        self.assertEqual(len(line2), 44)

    def test_verify_mrz_invalid_check(self):
        line1 = "P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<"
        line2 = "L898902C36UTO7408122F1204159ZE184226B<<<<<11"
        result = verify_mrz(line1, line2)
        self.assertFalse(result['valid'])
        self.assertFalse(result['details']['composite'])

    def test_mrz_length_constraints(self):
        line1 = "P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<"
        line2 = "L898902C36UTO7408122F1204159ZE184226B<<<<<10"
        self.assertEqual(len(line1), 44)
        self.assertEqual(len(line2), 44)

    def test_verify_mrz_invalid_passport_number(self):
        line1 = "P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<"
        line2 = "L898902C35UTO7408122F1204159ZE184226B<<<<<0"
        result = verify_mrz(line1, line2)
        self.assertFalse(result['valid'])
        self.assertFalse(result['details']['passport_number'])

    def test_verify_mrz_invalid_birth_date(self):
        line1 = "P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<"
        line2 = "L898902C36UTO7408125F1204159ZE184226B<<<<<0"
        result = verify_mrz(line1, line2)
        self.assertFalse(result['valid'])
        self.assertFalse(result['details']['birth_date'])

    def test_verify_mrz_invalid_length(self):
        line1 = "P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<"  # 43 chars
        line2 = "L898902C36UTO7408122F1204159ZE184226B<<<<<0"
        result = verify_mrz(line1, line2)
        self.assertFalse(result['valid'])

    def test_verify_mrz_with_filler_characters(self):
        fields = {
            'document_type': 'P',
            'issuing_country': 'UTO',
            'last_name': 'ERIKSSON',
            'first_name': 'ANNA',
            'middle_name': 'MARIA',
            'passport_number': 'L898902C3',
            'country_code': 'UTO',
            'birth_date': '740812',
            'sex': 'F',
            'expiration_date': '120415',
            'personal_number': 'ZE184226B'
        }
        line1, line2 = encode_mrz(fields)
        result = verify_mrz(line1, line2)
        self.assertTrue(result['valid'])

    def test_verify_mrz_result_structure(self):
        line1 = "P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<"
        line2 = "L898902C36UTO7408122F1204159ZE184226B<<<<<0"
        result = verify_mrz(line1, line2)
        self.assertIn('valid', result)
        self.assertIn('details', result)
        self.assertIsInstance(result['details'], dict)

    def test_verify_check_digits_valid(self):
        fields = {
            'document_type': 'P',
            'issuing_country': 'UTO',
            'last_name': 'ERIKSSON',
            'first_name': 'ANNA',
            'middle_name': 'MARIA',
            'passport_number': 'L898902C3',
            'country_code': 'UTO',
            'birth_date': '740812',
            'sex': 'F',
            'expiration_date': '120415',
            'personal_number': 'ZE184226B'      
            }
        line1, line2 = encode_mrz(fields)
        decoded = decode_mrz(line1, line2)
        result = verify_check_digits(decoded)
        self.assertTrue(result['valid'])
        self.assertTrue(all(result['details'].values()))


    
if __name__ == '__main__':
    unittest.main()
