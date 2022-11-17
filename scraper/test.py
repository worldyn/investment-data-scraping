import unittest
from enrich_company import prep_company_name,prep_url

class TestPrime(unittest.TestCase):
    def test_company_name_prep(self):
        self.assertEqual(prep_company_name("AM-Pharma"), 'am pharma')
        self.assertEqual(prep_company_name("aaa / bbb"), 'aaa')
        self.assertEqual(prep_company_name("Company  ltd."), 'company')
    
    def test_url_prep(self):
        self.assertEqual(prep_url('https://www.example.com/'), 'www.example.com')
        self.assertEqual(prep_url('http://www.example.com/'), 'www.example.com')
        self.assertEqual(prep_url('http://www.example.com'), 'www.example.com')

if __name__=='__main__':
	unittest.main()