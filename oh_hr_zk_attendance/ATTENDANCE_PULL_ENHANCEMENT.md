# Attendance Pull Module Enhancement

## Overview
This enhancement adds a powerful attendance pull wizard to the existing `oh_hr_zk_attendance` module, allowing users to pull attendance data from biometric devices with site-specific and date range filtering.

## Features Implemented

### 1. Site-Specific Filtering
- Users can select a specific site/location to pull attendance from
- Only devices associated with the selected site will be used
- If no site is selected, all devices will be queried

### 2. Date Range Filtering  
- **Today Only**: Quick option to pull today's attendance only
- **Date Range**: Custom from/to date selection for historical data
- Automatic date validation (from_date ≤ to_date)

### 3. Smart Device Selection
- Automatic device filtering based on selected site
- Manual device selection override option
- Clear visual indicators for available devices

### 4. Enhanced User Interface
- Intuitive wizard-based interface
- Radio button selection for pull type
- Date widgets with proper validation
- Helpful information and instructions
- Success/error notifications with detailed results

## Technical Implementation

### New Files Added:
- `wizards/attendance_pull_wizard.py` - Main wizard logic
- `views/attendance_pull_wizard_view.xml` - Wizard UI definition

### Enhanced Files:
- `models/zk_machine.py` - Added filtered download functionality
- `views/zk_machine_view.xml` - Added pull button
- `security/ir.model.access.csv` - Added wizard permissions
- `__manifest__.py` - Added new view file

### Key Methods:
- `download_attendance_filtered(from_date, to_date)` - Filtered attendance download
- `action_pull_attendance()` - Main wizard action
- `_onchange_site_id()` - Auto-populate devices based on site

## Usage Instructions

### Access Methods:
1. **Via Menu**: Attendances → Biometric Manager → Pull Attendance
2. **Via Device Form**: Use "Pull Attendance" button in device form header

### Workflow:
1. Open the Pull Attendance wizard
2. Select target site/location (optional)
3. Choose devices (auto-populated or manual selection)
4. Select date range type (Today or Custom)
5. Set date range if using custom dates
6. Click "Pull Attendance" to execute

### Results:
- Success notification shows number of records pulled
- Failure details for any unreachable devices
- Duplicate detection prevents data duplication
- New attendance records automatically created in HR system

## Benefits

### For Users:
- ✅ Faster targeted attendance pulling
- ✅ Reduced network traffic and processing time
- ✅ Better control over data synchronization
- ✅ Clear feedback on operation results

### For Administrators:
- ✅ Site-specific monitoring capabilities
- ✅ Historical data retrieval options
- ✅ Improved troubleshooting with detailed error messages
- ✅ Maintains existing functionality while adding new features

## Security & Permissions
- Uses existing HR attendance user groups
- No additional security setup required
- Maintains proper access control

## Compatibility
- Fully backward compatible with existing functionality
- No changes to existing cron jobs or data structures
- Works with all supported biometric device models