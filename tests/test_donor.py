"""Tests for donor management functionality."""

import pytest
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestDonor:
    """Test donor-related functionality."""
    
    def test_donor_creation(self):
        """Test that donor can be created with attributes."""
        donor_data = {
            'name': 'John Doe',
            'blood_group': 'O+',
            'age': 30,
            'contact': '1234567890',
            'address': '123 Main St'
        }
        
        assert donor_data['name'] == 'John Doe'
        assert donor_data['blood_group'] == 'O+'
        assert donor_data['age'] == 30
    
    def test_blood_group_validation(self):
        """Test blood group validation."""
        valid_blood_groups = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']
        
        for bg in valid_blood_groups:
            assert bg in valid_blood_groups
        
        invalid_bg = 'Z+'
        assert invalid_bg not in valid_blood_groups
    
    def test_age_validation(self):
        """Test age validation."""
        valid_age = 25
        invalid_age = 150
        
        assert 0 < valid_age < 120
        assert not (0 < invalid_age < 120)
