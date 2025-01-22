
import unittest

import decerts as d


class TestData(unittest.TestCase):


    def test_sql_fix(self):
        expected = 'NULL'
        self.assertEqual(expected, d.sql_fix(''))

        expected = "'Land''s End'"
        self.assertEqual(expected, d.sql_fix("Land's End"))

        expected = "'7%% solution'"
        self.assertEqual(expected, d.sql_fix('7% solution'))


    def test_untag(self):
        expected = 'Los Angeles County SD'
        self.assertEqual(expected, d.untag('<td>Los Angeles County SD</td>'))

        # this should not be in input, but it is what is expected.
        #
        expected = '<Los Angeles County SD'
        self.assertEqual(expected, d.untag('<<td>Los Angeles County SD</td>'))

        # again, should not be in input, but expected.
        #
        expected = '<>Los Angeles County SD'
        self.assertEqual(expected, d.untag('<<td>>Los Angeles County SD</td>'))

        expected = 'Pursuant to GC &#167; 1029 - Conviction for Violation ' \
                   'PC &#167; 261(a)(7) Rape by Threat to Arrest or Deport (09/07/1993) '
        given = '<td><p>Pursuant to GC &#167; 1029 - Conviction for Violation ' \
                'PC &#167; 261(a)(7) Rape by Threat to Arrest or Deport (09/07/1993) </p>'
        self.assertEqual(expected, d.untag(given))


    def test_clean(self):
        given = ['<p class="textRed">',
                 '  <span class="sr-only">Begin strikethrough text</span>',
                 '  <s>Temporary Suspension</s>',
                 '  <span class="sr-only">End strikethrough text</span>',
                 '</p>']
        given = '\n'.join(given)
        expected = '<p class="textRed">  <s>Temporary Suspension</s></p>'
        self.assertEqual(expected, d.clean(given))


    def test_clean_and_untag(self):
        given = '<td>San Bernardino County SD </td>'
        expected = 'San Bernardino County SD'
        self.assertEqual(expected, d.clean(d.untag(given)))


    def test_split_last_employ(self):
        given = 'Alameda County SD (last employed 01/10/2000)'
        expected = ['Alameda County SD', '01/10/2000']
        self.assertEqual(expected, d.split_last_employ(given))

        given = 'Merced County SO'
        expected = ['Merced County SO']
        self.assertEqual(expected, d.split_last_employ(given))

        given = 'Santa Monica PD (Last employed 06/21/2022)'
        expected = ['Santa Monica PD', '06/21/2022']
        self.assertEqual(expected, d.split_last_employ(given))

        given = 'San Diego County SD	(last employed 02/10/2023)'
        expected = ['San Diego County SD', '02/10/2023']
        self.assertEqual(expected, d.split_last_employ(given))

        given = 'Perris PD (Obsolete Agency - Last employed 04/14/1983)'
        expected = ['Perris PD', '04/14/1983', 'Obsolete Agency']
        self.assertEqual(expected, d.split_last_employ(given))

        # not expected, but we should know what happens.
        #
        given = 'Perris PD (Obsolete Agency)'
        expected = ['Perris PD', '', 'Obsolete Agency']
        self.assertEqual(expected, d.split_last_employ(given))


if __name__ == '__main__':
    unittest.main()

