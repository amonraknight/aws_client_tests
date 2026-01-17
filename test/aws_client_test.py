import unittest
from src.aws_client import AwsClient

class aws_client_unit_tests(unittest.TestCase):

    def test_init_loads_dotenv(self):
        client = AwsClient()
        

if __name__ == '__main__':
    unittest.main()