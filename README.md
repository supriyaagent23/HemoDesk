[![Python CI](https://github.com/supriyaagent23/HemoDesk/actions/workflows/ci.yml/badge.svg)](https://github.com/supriyaagent23/HemoDesk/actions/workflows/ci.yml)
[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://python.org)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Flet](https://img.shields.io/badge/Flet-0.20+-orange.svg)](https://flet.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# 🩸 HemoDesk - Blood Bank Management System

A comprehensive desktop application for managing blood donors, donations, inventory, and patient requests. Built with **Flet** (Python GUI framework) and **SQLite** database.

## ✨ Features

### 🖥️ Dashboard
- Real-time statistics overview
- Blood stock levels with visual progress bars
- Quick action buttons for common tasks
- Pending lab tests notifications
- Professional medical theme

### 👥 Donor Management
- Add, edit, and delete donors
- Track donor blood types (including "Unknown" for lab testing)
- View donation history
- Automatic total donations counter
- Phone number and age validation

### 🔬 Lab Testing & Donations
- Test unknown blood types in one click
- Automatic donation recording after blood type confirmation
- Thank you messages for donors
- Seamless workflow: Test → Donate → Stock

### 📦 Blood Stock Management
- Real-time inventory tracking for all 8 blood types
- Low stock alerts (threshold: 5 units)
- Visual progress bars for capacity monitoring
- Add/remove stock manually
- Configure settings (threshold, max limit, wait periods)

### 📋 Patient Requests
- Create blood requests for patients
- Track request status (Pending/Fulfilled/Rejected)
- Filter by status
- Urgency levels (Critical, High, Normal, Low)
- Auto-update stock when fulfilling requests

### ✅ Donor Eligibility
- Check if donors are eligible to donate
- 90-day waiting period between donations
- Age restrictions (18-65 years)
- View donor donation history
- Eligibility rules and guidelines

### 🎉 Thank You System
- Automatic thank you messages for donors
- Track all thank you messages sent
- Snackbar notifications on successful donations

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Installation

1. Clone the repository
```bash
git clone https://github.com/supriyaagent23/HemoDesk.git
cd HemoDesk