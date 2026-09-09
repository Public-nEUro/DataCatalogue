import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch


IMPORT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(IMPORT_DIR))

import export_xlsx  # noqa: E402


CROSSREF = 'http://www.crossref.org/schema/5.5.0'
FUNDREF = 'http://www.crossref.org/fundref.xsd'
RELATIONS = 'http://www.crossref.org/relations.xsd'
NS = {'cr': CROSSREF, 'fr': FUNDREF, 'rel': RELATIONS}


class CrossrefExportTests(unittest.TestCase):
    def setUp(self):
        self.metadata = {
            'id': 'PN000011',
            'dataset_version': 'V2',
            'title': 'Clinical pediatric brain MRI',
            'name': 'PN000011 Clinical pediatric brain MRI',
            'description': 'MRI data with motion correction.',
            'doi_without_prefix': '10.70883/VMIF5895',
            'keywords': ['pediatric', 'MRI', 'motion correction'],
            'dateCreated': '2025-09-15 00:00:00',
            'dateModified': '2026-09-09 00:00:00',
            'authors': [{
                'givenName': 'Llucia',
                'familyName': 'Coll',
                'orcid': '0000-0002-1825-0097',
            }],
            'funding': [{
                'name': 'Elsass foundation',
                'identifier': '18-3-0147',
            }],
            'publications': [{
                'title': 'A paper using these data',
                'datePublished': '2026',
                'doi': 'https://doi.org/10.1000/example',
                'authors': [{'familyName': 'Coll'}],
            }],
            'participants': {'content': {'total_number': ['47']}},
            'detailed_metadata': {'content': {
                'bids_version': ['1.9.0'],
                'bids_datasettype': 'raw',
                'bids_datatypes': ['anat', 'func'],
            }},
        }

    def export(self):
        temporary = tempfile.NamedTemporaryFile(suffix='.xml', delete=False)
        temporary.close()
        self.addCleanup(Path(temporary.name).unlink, missing_ok=True)
        with patch.object(export_xlsx, 'parse_excel_metadata', return_value=self.metadata):
            export_xlsx.export_xlsx_to_xml(
                'unused.xlsx',
                temporary.name,
                skip_validation=True,
                data_size='4.20 GB',
            )
        return ET.parse(temporary.name).getroot()

    def test_uses_crossref_5_5_0(self):
        root = self.export()
        self.assertEqual(root.tag, f'{{{CROSSREF}}}doi_batch')
        self.assertEqual(root.attrib['version'], '5.5.0')
        schema_location = root.attrib['{http://www.w3.org/2001/XMLSchema-instance}schemaLocation']
        self.assertIn('crossref5.5.0.xsd', schema_location)

    def test_exports_rich_dataset_metadata(self):
        root = self.export()
        dataset = root.find('.//cr:dataset', NS)

        self.assertEqual(dataset.findtext('cr:contributors/cr:person_name/cr:ORCID', namespaces=NS),
                         'https://orcid.org/0000-0002-1825-0097')
        self.assertEqual(dataset.findtext('cr:publisher_item/cr:item_number', namespaces=NS),
                         'PN000011')
        self.assertEqual(dataset.findtext('cr:format', namespaces=NS),
                         'BIDS 1.9.0; raw; data types: anat, func')
        self.assertEqual(dataset.findtext('cr:version_info/cr:version', namespaces=NS), 'V2')

        description = dataset.findtext('cr:description', namespaces=NS)
        self.assertIn('Keywords: pediatric, MRI, motion correction', description)
        self.assertIn('Participants: 47', description)
        self.assertIn('Total size: 4.20 GB', description)

        self.assertEqual(
            dataset.findtext("fr:program/fr:assertion/fr:assertion[@name='funder_name']", namespaces=NS),
            'Elsass foundation',
        )
        relation = dataset.find('.//rel:inter_work_relation', NS)
        self.assertEqual(relation.attrib['relationship-type'], 'isDataBasisFor')
        self.assertEqual(relation.attrib['identifier-type'], 'doi')
        self.assertEqual(relation.text, '10.1000/example')

        citation = dataset.find("cr:citation_list/cr:citation[@type='journal_article']", NS)
        self.assertEqual(citation.findtext('cr:doi', namespaces=NS), '10.1000/example')
        self.assertEqual(citation.findtext('cr:cYear', namespaces=NS), '2026')

    def test_exports_dataset_lifecycle_dates(self):
        dataset = self.export().find('.//cr:dataset', NS)
        self.assertEqual(dataset.findtext('cr:database_date/cr:creation_date/cr:year', namespaces=NS),
                         '2025')
        self.assertEqual(dataset.findtext('cr:database_date/cr:publication_date/cr:year', namespaces=NS),
                         '2025')
        self.assertEqual(dataset.findtext('cr:database_date/cr:update_date/cr:year', namespaces=NS),
                         '2026')

    def test_encodes_a_mononym_as_the_required_surname(self):
        self.metadata['authors'] = [{'givenName': 'Charlie', 'familyName': ''}]
        person = self.export().find('.//cr:person_name', NS)
        self.assertIsNone(person.find('cr:given_name', NS))
        self.assertEqual(person.findtext('cr:surname', namespaces=NS), 'Charlie')

    def test_ignores_a_non_doi_publication_identifier(self):
        self.metadata['publications'][0]['doi'] = 'none'
        dataset = self.export().find('.//cr:dataset', NS)
        self.assertIsNone(dataset.find('rel:program', NS))
        self.assertIsNone(dataset.find('cr:citation_list', NS))


if __name__ == '__main__':
    unittest.main()
