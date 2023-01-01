#!/usr/bin/env python3

import unittest
from redcap_branch_parser import BranchingLogicParser

class REDCapBranchParserTests(unittest.TestCase):
    def setUp(self):
        self.parser = BranchingLogicParser()

    def test_function1(self):
        test_string: str = "[variable]='1'"
        results = self.parser.parse(test_string)
        print(results)

if __name__ == '__main__':
    unittest.main()