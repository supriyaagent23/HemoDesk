[![Python CI](https://github.com/supriyaagent23/HemoDesk/actions/workflows/ci.yml/badge.svg)](https://github.com/supriyaagent23/HemoDesk/actions/workflows/ci.yml)
[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://python.org)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Flet](https://img.shields.io/badge/Flet-0.20+-orange.svg)](https://flet.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# 🩸 HemoDesk - Blood Bank Management System

A comprehensive desktop application for managing blood donors, donations, inventory, and patient requests. Built with **Flet** (Python GUI framework) and **SQLite** database.

## Features

### Donor Management
- Add, edit, and delete donors
- Passport number as unique identifier
- Search donors by name or passport
- Filter donors by eligibility status
- Age validation (18-80 years)
- Phone number validation (10 digits)

### Blood Stock Management
- Real-time tracking for all 8 blood types (A+, A-, B+, B-, AB+, AB-, O+, O-)
- Low stock alerts (threshold: 5 units)
- Visual progress bars
- Manual stock add/remove
- Configurable settings

### Lab Testing & Donations
- Test unknown blood types
- Automatic donation recording after test (1 unit)
- Thank you messages for donors

### Donation Recording
- Search donors by name or passport
- Enter units (1-10)
- Automatic stock update
- Eligibility check before donation

### Patient Requests
- Create blood requests with urgency levels (Critical, High, Normal, Low)
- Track request status (Pending/Fulfilled/Rejected)
- Filter by status
- Auto-update stock when fulfilling

### Donor Eligibility
- 90-day waiting period between donations
- Age restrictions (18-65 years)
- Donation history view

## Tech Stack

- **Language**: Python 3.9+
- **GUI Framework**: Flet 0.20+
- **Database**: SQLite
- **Testing**: pytest, pytest-cov
- **Code Quality**: black, flake8, mypy, ruff

## Installation

```bash
# Clone repository
git clone https://github.com/supriyaagent23/HemoDesk.git
cd HemoDesk

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py