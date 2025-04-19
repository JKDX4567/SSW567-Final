import unittest
import importlib
import MRTD
from mutpy import commandline
import sys


class TestMRTD(unittest.TestCase):

    def test_scan_mrz_exists(self):
        importlib.reload(MRTD)
        scan_mrz = MRTD.scan_mrz
        self.assertIsNone(scan_mrz())

    def test_query_database_exists(self):
        importlib.reload(MRTD)
        query_database = MRTD.query_database
        self.assertIsNone(query_database())

    def test_fletcher16_checksum(self):
        importlib.reload(MRTD)
        fletcher16 = MRTD.fletcher16
        self.assertEqual(fletcher16(b''), 0)
        self.assertEqual(fletcher16(b'ABC123'), 2909)

    def test_calculate_check_digit_basic(self):
        importlib.reload(MRTD)
        calculate_check_digit = MRTD.calculate_check_digit
        fletcher16 = MRTD.fletcher16
        self.assertEqual(calculate_check_digit(""), 0)
        self.assertEqual(calculate_check_digit("123456789"), fletcher16(b"123456789") % 10)
        self.assertEqual(calculate_check_digit("L898902C3"), fletcher16(b"L898902C3") % 10)

    def test_encode_decode_roundtrip(self):
        importlib.reload(MRTD)
        encode_mrz = MRTD.encode_mrz
        decode_mrz = MRTD.decode_mrz
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
        importlib.reload(MRTD)
        encode_mrz = MRTD.encode_mrz
        verify_mrz = MRTD.verify_mrz
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
        importlib.reload(MRTD)
        encode_mrz = MRTD.encode_mrz
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
        importlib.reload(MRTD)
        verify_mrz = MRTD.verify_mrz
        line1 = "P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<"
        line2 = "L898902C36UTO7408122F1204159ZE184226B<<<<<11"
        result = verify_mrz(line1, line2)
        self.assertFalse(result['valid'])
        self.assertFalse(result['details']['passport_number'])

    def test_mrz_length_constraints(self):
        line1 = "P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<"
        line2 = "L898902C36UTO7408122F1204159ZE184226B<<<<<10"
        self.assertEqual(len(line1), 44)
        self.assertEqual(len(line2), 44)

    def test_verify_mrz_invalid_passport_number(self):
        importlib.reload(MRTD)
        verify_mrz = MRTD.verify_mrz
        line1 = "P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<"
        line2 = "L898902C35UTO7408122F1204159ZE184226B<<<<<0"
        result = verify_mrz(line1, line2)
        self.assertFalse(result['valid'])
        self.assertFalse(result['details']['passport_number'])

    def test_verify_mrz_invalid_birth_date(self):
        importlib.reload(MRTD)
        verify_mrz = MRTD.verify_mrz
        line1 = "P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<"
        line2 = "L898902C36UTO7408125F1204159ZE184226B<<<<<0"
        result = verify_mrz(line1, line2)
        self.assertFalse(result['valid'])
        self.assertFalse(result['details']['birth_date'])

    def test_verify_mrz_invalid_length(self):
        importlib.reload(MRTD)
        verify_mrz = MRTD.verify_mrz
        line1 = "P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<"  # 43 chars
        line2 = "L898902C36UTO7408122F1204159ZE184226B<<<<<0"
        result = verify_mrz(line1, line2)
        self.assertFalse(result['valid'])

    def test_verify_mrz_with_filler_characters(self):
        importlib.reload(MRTD)
        verify_mrz = MRTD.verify_mrz
        encode_mrz = MRTD.encode_mrz
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
        importlib.reload(MRTD)
        verify_mrz = MRTD.verify_mrz
        line1 = "P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<"
        line2 = "L898902C36UTO7408122F1204159ZE184226B<<<<<0"
        result = verify_mrz(line1, line2)
        self.assertIn('valid', result)
        self.assertIn('details', result)
        self.assertIsInstance(result['details'], dict)

    def test_verify_check_digits_valid(self):
        importlib.reload(MRTD)
        encode_mrz = MRTD.encode_mrz
        decode_mrz = MRTD.decode_mrz
        verify_check_digits = MRTD.verify_check_digits
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

    def expected_check(self, data: str) -> int:
        importlib.reload(MRTD)
        fletcher16 = MRTD.fletcher16
        return fletcher16(data.encode('ascii')) % 10

    # EXTRA TEST CASES TO KILL MUTANTS FROM MutPy
    def test_calculate_check_digit_known_values(self):
        importlib.reload(MRTD)
        calculate_check_digit = MRTD.calculate_check_digit
        self.assertEqual(calculate_check_digit('L898902C3'), self.expected_check('L898902C3'))
        self.assertEqual(calculate_check_digit('740812'), self.expected_check('740812'))
        self.assertEqual(calculate_check_digit('120415'), self.expected_check('120415'))
        self.assertEqual(calculate_check_digit('ZE184226B'), self.expected_check('ZE184226B'))

    def test_verify_check_digits_field_breakdown(self):
        importlib.reload(MRTD)
        encode_mrz = MRTD.encode_mrz
        decode_mrz = MRTD.decode_mrz
        verify_check_digits = MRTD.verify_check_digits
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

        self.assertTrue(result['details']['passport_number'])
        self.assertTrue(result['details']['birth_date'])
        self.assertTrue(result['details']['expiration_date'])
        self.assertTrue(result['details']['personal_number'])

    def test_verify_check_digits_invalid_passport(self):
        importlib.reload(MRTD)
        encode_mrz = MRTD.encode_mrz
        decode_mrz = MRTD.decode_mrz
        verify_check_digits = MRTD.verify_check_digits
        fields = {'document_type': 'P',
            'issuing_country': 'UTO',
            'last_name': 'ERIKSSON',
            'first_name': 'ANNA',
            'middle_name': 'MARIA',
            'passport_number': 'L898902C3',
            'country_code': 'UTO',
            'birth_date': '740812',
            'sex': 'F',
            'expiration_date': '120415',
            'personal_number': 'ZE184226B'}
        line1, line2 = encode_mrz(fields)
        # Mutate just the passport check digit
        line2 = line2[:9] + '0' + line2[10:]  # Force wrong digit
        decoded = decode_mrz(line1, line2)
        result = verify_check_digits(decoded)

        self.assertFalse(result['details']['passport_number'])
        self.assertTrue(result['details']['birth_date'])  # Still valid

    def test_fletcher16_known_values(self):
        importlib.reload(MRTD)
        fletcher16 = MRTD.fletcher16
        self.assertEqual(fletcher16(b'ABC123'), 2909)
        self.assertEqual(fletcher16(b'L898902C3'), 33032)

    def test_verify_mrz_calculated_digits(self):
        importlib.reload(MRTD)
        encode_mrz = MRTD.encode_mrz
        verify_mrz = MRTD.verify_mrz
        calculate_check_digit = MRTD.calculate_check_digit
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

        self.assertEqual(result['calculated']['passport_number'], str(calculate_check_digit('L898902C3')))
        self.assertEqual(result['calculated']['birth_date'], str(calculate_check_digit('740812')))
        self.assertEqual(result['calculated']['expiration_date'], str(calculate_check_digit('120415')))

    def expected_check_digit(self, data: str) -> int:
        importlib.reload(MRTD)
        fletcher16 = MRTD.fletcher16
        normalized = data.upper().replace('<', '0')
        return fletcher16(normalized.encode('ascii')) % 10

    def test_calculate_check_digit_mutant_protection(self):
        importlib.reload(MRTD)
        calculate_check_digit = MRTD.calculate_check_digit
        fletcher16 = MRTD.fletcher16
        # Single known values that target digit/letter conversion logic
        self.assertEqual(calculate_check_digit("123"), fletcher16(b"123") % 10)
        self.assertEqual(calculate_check_digit("ABC"), fletcher16(b"ABC") % 10)
        self.assertEqual(calculate_check_digit("<<<<"), self.expected_check_digit("<<<<"))
        self.assertEqual(calculate_check_digit("A1<"), self.expected_check_digit("A1<") % 10)

    def test_verify_check_digits_specific(self):
        importlib.reload(MRTD)
        calculate_check_digit = MRTD.calculate_check_digit
        verify_check_digits = MRTD.verify_check_digits
        decoded = {
            'line2': {
                'passport_number': 'L898902C3',
                'passport_number_check_digit': str(calculate_check_digit('L898902C3')),
                'birth_date': '740812',
                'birth_date_check_digit': str(calculate_check_digit('740812')),
                'expiration_date': '120415',
                'expiration_date_check_digit': str(calculate_check_digit('120415')),
                'personal_number': 'ZE184226B',
                'personal_number_check_digit': str(calculate_check_digit('ZE184226B')),
            }
        }

        result = verify_check_digits(decoded)
        self.assertTrue(result['valid'])
        for val in result['details'].values():
            self.assertTrue(val)

    def test_mrz_length_is_always_44(self):
        importlib.reload(MRTD)
        encode_mrz = MRTD.encode_mrz
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

    def test_fletcher16_precise_math(self):
        importlib.reload(MRTD)
        fletcher16 = MRTD.fletcher16
        # Validate exact output of raw Fletcher math
        self.assertEqual(fletcher16(b"ABC123"), 2909)
        self.assertEqual(fletcher16(b"L898902C3"), 33032)
        self.assertEqual(fletcher16(b"0000"), 57792)  # Used internally for <<<< normalization


if __name__ == '__main__':
    unittest.main(commandline.main(sys.argv))
