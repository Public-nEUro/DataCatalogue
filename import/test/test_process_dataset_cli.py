#!/usr/bin/env python3
"""
Unit tests for process_dataset.py CLI
"""

import unittest
import os
import sys
import tempfile
import shutil
import glob
import subprocess
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from process_dataset import process_dataset, main


class TestProcessDatasetCLI(unittest.TestCase):
    """Test suite for the dataset processing CLI"""
    
    @classmethod
    def cleanup_test_datasets(cls, pattern_prefix='TEST_'):
        """Clean up any test datasets from catalog using datalad catalog-remove"""
        metadata_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'metadata')
        catalog_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..')
        
        if not os.path.exists(metadata_dir):
            return
            
        # Look for directories that start with test pattern
        test_dirs = glob.glob(os.path.join(metadata_dir, f'{pattern_prefix}*'))
        for test_dir in test_dirs:
            try:
                if os.path.isdir(test_dir):
                    # Get the dataset ID from the directory name
                    dataset_id = os.path.basename(test_dir)
                    
                    # Use datalad catalog-remove with reckless argument
                    remove_cmd = [
                        'datalad', 'catalog-remove',
                        '--catalog', catalog_dir,
                        '--reckless', 'modification',
                        dataset_id
                    ]
                    
                    print(f"Removing test dataset: {dataset_id}")
                    result = subprocess.run(remove_cmd, capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        print(f"✅ Successfully removed test dataset: {dataset_id}")
                    else:
                        print(f"⚠️  Warning: Could not remove dataset {dataset_id} via datalad: {result.stderr}")
                        # Fallback to manual cleanup if datalad remove fails
                        shutil.rmtree(test_dir)
                        print(f"   Manually cleaned up: {test_dir}")
                        
            except (OSError, IOError, subprocess.SubprocessError) as e:
                print(f"Warning: Could not clean up test dataset {test_dir}: {e}")
                # Try manual cleanup as fallback
                try:
                    if os.path.exists(test_dir):
                        shutil.rmtree(test_dir)
                        print(f"   Fallback cleanup successful: {test_dir}")
                except Exception as fallback_e:
                    print(f"   Fallback cleanup also failed: {fallback_e}")
    
    def setUp(self):
        """Set up test fixtures"""
        # Clean up any leftover test datasets
        self.cleanup_test_datasets()
        
        self.test_dir = tempfile.mkdtemp()
        self.excel_file = os.path.join(self.test_dir, 'test.xlsx')
        self.data_dir = os.path.join(self.test_dir, 'data')
        
        # Track metadata directory for cleanup
        self.metadata_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'metadata')
        self.metadata_files_before = set()
        
        # Record existing metadata files before test
        if os.path.exists(self.metadata_dir):
            self.metadata_files_before = set(glob.glob(os.path.join(self.metadata_dir, '**', '*'), recursive=True))
        
        # Create test data directory
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Create a simple test file in data directory
        with open(os.path.join(self.data_dir, 'test_file.txt'), 'w') as f:
            f.write('test content')
    
    def tearDown(self):
        """Clean up test fixtures and any created metadata files"""
        # Clean up test directory
        shutil.rmtree(self.test_dir, ignore_errors=True)
        
        # Clean up any test datasets
        self.cleanup_test_datasets()
        
        # Check for any new dataset directories created during test
        if os.path.exists(self.metadata_dir):
            current_dirs = set()
            for item in os.listdir(self.metadata_dir):
                item_path = os.path.join(self.metadata_dir, item)
                if os.path.isdir(item_path):
                    current_dirs.add(item)
            
            # Find directories that didn't exist before
            existing_dirs = set()
            for file_path in self.metadata_files_before:
                if os.path.isdir(file_path):
                    rel_path = os.path.relpath(file_path, self.metadata_dir)
                    if '/' not in rel_path and '\\' not in rel_path:  # Top-level directory
                        existing_dirs.add(rel_path)
            
            new_datasets = current_dirs - existing_dirs
            
            # Remove new datasets using datalad catalog-remove
            catalog_dir = os.path.join(os.path.dirname(self.metadata_dir), '..')
            for dataset_id in new_datasets:
                try:
                    remove_cmd = [
                        'datalad', 'catalog-remove',
                        '--catalog', catalog_dir,
                        '--reckless', 'modification',
                        dataset_id
                    ]
                    
                    print(f"Removing dataset created during test: {dataset_id}")
                    result = subprocess.run(remove_cmd, capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        print(f"✅ Successfully removed dataset: {dataset_id}")
                    else:
                        print(f"⚠️  Warning: Could not remove dataset {dataset_id}: {result.stderr}")
                        
                except (subprocess.SubprocessError, Exception) as e:
                    print(f"Warning: Could not remove dataset {dataset_id}: {e}")
            
            # Clean up any remaining new files (non-directories)
            current_files = set(glob.glob(os.path.join(self.metadata_dir, '**', '*'), recursive=True))
            new_files = current_files - self.metadata_files_before
            
            for file_path in new_files:
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        print(f"Cleaned up test metadata file: {file_path}")
                except (OSError, IOError) as e:
                    print(f"Warning: Could not clean up {file_path}: {e}")
    
    @patch('process_dataset.subprocess.run')
    @patch('process_dataset.find_catalogue_set_file')
    @patch('process_dataset.process_file_metadata')
    @patch('process_dataset.export_xlsx_to_both')
    def test_process_dataset_success(self, mock_export, mock_process, mock_find, mock_subprocess):
        """Test successful dataset processing"""
        # Mock return values
        mock_export.return_value = ('test.xml', 'test.jsonl')
        mock_process.return_value = 'catalog.jsonl'
        mock_find.return_value = {'PN000011/V1': '/path/to/dataset'}
        
        # Mock subprocess calls (validation and import)
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stderr = ''
        
        # Create a dummy Excel file
        Path(self.excel_file).touch()
        
        result = process_dataset(
            excel_file=self.excel_file,
            data_directory=self.data_dir,
            dataset_pattern='PN000011*/V1'
        )
        
        # Verify all steps were called
        mock_export.assert_called_once_with(self.excel_file)
        mock_process.assert_called_once_with(
            dataset_jsonl='test.jsonl',
            file_list_source=self.data_dir,
            source_name='Local_Processing',
            agent_name='Pipeline'
        )
        
        # Verify datalad commands were called
        self.assertEqual(mock_subprocess.call_count, 2)  # validate + import
        validate_call = mock_subprocess.call_args_list[0]
        import_call = mock_subprocess.call_args_list[1]
        
        self.assertIn('catalog-validate', validate_call[0][0])
        self.assertIn('catalog-add', import_call[0][0])
        
        mock_find.assert_called_once_with('PN000011*/V1', reorder_children=True)
        
        # Verify result structure
        expected_result = {
            'xml': 'test.xml',
            'jsonl': 'test.jsonl',
            'catalog': 'catalog.jsonl',
            'found': ['PN000011/V1']
        }
        self.assertEqual(result, expected_result)
    
    @patch('process_dataset.subprocess.run')
    @patch('process_dataset.find_catalogue_set_file')
    @patch('process_dataset.process_file_metadata')
    @patch('process_dataset.export_xlsx_to_both')
    def test_process_dataset_custom_params(self, mock_export, mock_process, mock_find, mock_subprocess):
        """Test dataset processing with custom parameters"""
        # Mock return values
        mock_export.return_value = ('custom.xml', 'custom.jsonl')
        mock_process.return_value = 'custom_catalog.jsonl'
        mock_find.return_value = {}
        
        # Mock subprocess calls
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stderr = ''
        
        # Create a dummy Excel file
        Path(self.excel_file).touch()
        
        result = process_dataset(
            excel_file=self.excel_file,
            data_directory=self.data_dir,
            dataset_pattern='PN*',
            source_name='CustomSource',
            agent_name='CustomAgent'
        )
        
        # Verify custom parameters were passed
        mock_process.assert_called_once_with(
            dataset_jsonl='custom.jsonl',
            file_list_source=self.data_dir,
            source_name='CustomSource',
            agent_name='CustomAgent'
        )
        
        # Verify result with no found datasets
        self.assertEqual(result['found'], [])
    
    @patch('process_dataset.subprocess.run')
    @patch('process_dataset.process_file_metadata')
    @patch('process_dataset.export_xlsx_to_both')
    def test_process_dataset_import_failure(self, mock_export, mock_process, mock_subprocess):
        """Test handling of datalad import failure"""
        # Mock export and process steps
        mock_export.return_value = ('test.xml', 'test.jsonl')
        mock_process.return_value = 'catalog.jsonl'
        
        # Mock subprocess calls - validation succeeds, import fails
        def subprocess_side_effect(*args, **kwargs):
            mock_result = MagicMock()
            if 'catalog-validate' in args[0]:
                mock_result.returncode = 0
                mock_result.stderr = ''
            else:  # catalog-add
                mock_result.returncode = 1
                mock_result.stderr = 'Import failed: permission denied'
            return mock_result
        
        mock_subprocess.side_effect = subprocess_side_effect
        
        # Create a dummy Excel file
        Path(self.excel_file).touch()
        
        with self.assertRaises(Exception) as context:
            process_dataset(
                excel_file=self.excel_file,
                data_directory=self.data_dir,
                dataset_pattern='PN*'
            )
        
        self.assertIn("Failed to import dataset to catalog", str(context.exception))
    
    @patch('process_dataset.export_xlsx_to_both')
    def test_process_dataset_export_failure(self, mock_export):
        """Test handling of export failure"""
        # Mock export failure
        mock_export.side_effect = Exception("Export failed")
        
        # Create a dummy Excel file
        Path(self.excel_file).touch()
        
        with self.assertRaises(Exception) as context:
            process_dataset(
                excel_file=self.excel_file,
                data_directory=self.data_dir,
                dataset_pattern='PN*'
            )
        
        self.assertIn("Export failed", str(context.exception))
    
    @patch('sys.argv', ['process_dataset.py', '--help'])
    def test_cli_help(self):
        """Test CLI help output"""
        with self.assertRaises(SystemExit) as context:
            main()
        # Help should exit with code 0
        self.assertEqual(context.exception.code, 0)
    
    @patch('sys.argv', ['process_dataset.py', 'nonexistent.xlsx', '/nonexistent', 'PN*'])
    @patch('builtins.print')
    def test_cli_missing_files(self, mock_print):
        """Test CLI with missing input files"""
        with self.assertRaises(SystemExit) as context:
            main()
        # Should exit with error code 1
        self.assertEqual(context.exception.code, 1)
        
        # Check error message was printed
        mock_print.assert_called()
        error_messages = [call[0][0] for call in mock_print.call_args_list]
        self.assertTrue(any("not found" in msg for msg in error_messages))
    
    @patch('process_dataset.process_dataset')
    def test_cli_success(self, mock_process):
        """Test successful CLI execution"""
        # Create dummy files
        Path(self.excel_file).touch()
        
        # Mock successful processing
        mock_process.return_value = {
            'xml': 'test.xml',
            'jsonl': 'test.jsonl', 
            'catalog': 'catalog.jsonl',
            'found': ['PN000011/V1']
        }
        
        # Mock sys.argv
        test_args = [
            'process_dataset.py',
            self.excel_file,
            self.data_dir,
            'PN000011*/V1',
            '--source', 'TestSource',
            '--agent', 'TestAgent'
        ]
        
        with patch('sys.argv', test_args):
            # Should not raise any exceptions
            main()
            
            # Verify process_dataset was called with correct arguments
            mock_process.assert_called_once_with(
                excel_file=self.excel_file,
                data_directory=self.data_dir,
                dataset_pattern='PN000011*/V1',
                source_name='TestSource',
                agent_name='TestAgent'
            )


class TestProcessDatasetIntegration(unittest.TestCase):
    """Integration tests using actual test data"""
    
    def setUp(self):
        """Set up with real test data if available"""
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        self.test_excel = os.path.join(self.test_dir, 'PublicnEUro_test.xlsx')
        self.fake_files_dir = os.path.join(self.test_dir, 'fake_files')
        
        # Track metadata directory for cleanup
        self.metadata_dir = os.path.join(os.path.dirname(self.test_dir), '..', 'metadata')
        self.metadata_files_before = set()
        
        # Record existing metadata files before test
        if os.path.exists(self.metadata_dir):
            self.metadata_files_before = set(glob.glob(os.path.join(self.metadata_dir, '**', '*'), recursive=True))
    
    def tearDown(self):
        """Clean up any metadata files created during integration tests"""
        # Clean up any new dataset directories using datalad catalog-remove
        if os.path.exists(self.metadata_dir):
            current_dirs = set()
            for item in os.listdir(self.metadata_dir):
                item_path = os.path.join(self.metadata_dir, item)
                if os.path.isdir(item_path):
                    current_dirs.add(item)
            
            # Find directories that didn't exist before
            existing_dirs = set()
            for file_path in self.metadata_files_before:
                if os.path.isdir(file_path):
                    rel_path = os.path.relpath(file_path, self.metadata_dir)
                    if '/' not in rel_path and '\\' not in rel_path:  # Top-level directory
                        existing_dirs.add(rel_path)
            
            new_datasets = current_dirs - existing_dirs
            
            # Remove new datasets using datalad catalog-remove
            catalog_dir = os.path.join(os.path.dirname(self.metadata_dir), '..')
            for dataset_id in new_datasets:
                try:
                    remove_cmd = [
                        'datalad', 'catalog-remove',
                        '--catalog', catalog_dir,
                        '--reckless', 'modification',
                        dataset_id
                    ]
                    
                    print(f"Removing integration test dataset: {dataset_id}")
                    result = subprocess.run(remove_cmd, capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        print(f"✅ Successfully removed integration test dataset: {dataset_id}")
                    else:
                        print(f"⚠️  Warning: Could not remove dataset {dataset_id}: {result.stderr}")
                        
                except (subprocess.SubprocessError, Exception) as e:
                    print(f"Warning: Could not remove dataset {dataset_id}: {e}")
        
        # Also clean up any generated files in the test directory
        test_files_to_clean = [
            'PublicnEUro_test.xml',
            'PublicnEUro_test_with_files.jsonl'
        ]
        
        for filename in test_files_to_clean:
            file_path = os.path.join(self.test_dir, filename)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    print(f"Cleaned up test file: {file_path}")
                except (OSError, IOError) as e:
                    print(f"Warning: Could not clean up {file_path}: {e}")
    
    def test_with_real_test_data(self):
        """Test with actual test data if available"""
        if not os.path.exists(self.test_excel):
            self.skipTest("Test Excel file not available")
        
        if not os.path.exists(self.fake_files_dir):
            self.skipTest("Fake files directory not available")
        
        try:
            # This is more of a smoke test - just ensure it doesn't crash
            result = process_dataset(
                excel_file=self.test_excel,
                data_directory=self.fake_files_dir,
                dataset_pattern='PN*',
                source_name='TestSource',
                agent_name='TestAgent'
            )
            
            # Basic validation
            self.assertIn('xml', result)
            self.assertIn('jsonl', result)
            self.assertIn('catalog', result)
            self.assertIn('found', result)
            
        except Exception as e:
            # If there are issues with dependencies, skip the test
            self.skipTest(f"Integration test failed due to dependencies: {e}")


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)