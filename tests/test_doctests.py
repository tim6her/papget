import doctest
import unittest

import papget.doi
import papget.papget

suite = unittest.TestSuite()

flags = doctest.NORMALIZE_WHITESPACE + doctest.ELLIPSIS
suite.addTest(doctest.DocTestSuite(papget.doi,
                                   optionflags=flags))
suite.addTest(doctest.DocTestSuite(papget.papget,
                                   optionflags=flags))

runner = unittest.TextTestRunner(verbosity=2)
runner.run(suite)
