# RCCM Quiz Application - Maintenance & Troubleshooting Manual

## 📋 Document Information

**Created**: 2025-08-31  
**Version**: 1.0  
**Purpose**: Complete maintenance and troubleshooting guide  
**Target Audience**: System administrators, developers, maintainers

---

## 🚨 Emergency Quick Reference

### System Health Check Commands
```bash
# Navigate to application directory
cd C:\Users\ABC\Desktop\rccm-quiz-app-production

# Quick health verification
python monitoring/system_health_monitor.py

# Verify core files exist
dir app.py config.py templates\question_types.html schemas\validation_schemas.py

# Check data files
dir data\4-1.csv data\4-2_2*.csv
```

### Emergency Contact Information
- **System Status**: All components operational as of 2025-08-31
- **Last Health Check**: Passed (6/6 files verified)
- **Critical Dependencies**: Python 3.x, Flask, Marshmallow

---

## 🔧 Daily Maintenance Procedures

### Daily Health Check (5 minutes)
1. **File Integrity Verification**
   ```bash
   python monitoring/system_health_monitor.py
   ```
   Expected output: "HEALTH MONITORING SUMMARY: File Integrity: 6/6"

2. **Application Startup Test**
   ```bash
   python app.py
   ```
   Expected: Flask development server starts without errors

3. **Template Verification**
   - Navigate to application in browser
   - Verify homepage loads correctly
   - Test department selection functionality

### Weekly Maintenance (15 minutes)
1. **Log File Review**
   - Check monitoring/health_log.json for any anomalies
   - Review Flask application logs for errors

2. **Data File Backup**
   ```bash
   # Create backup of data directory
   xcopy data\* backup\data_%date%\ /E /I
   ```

3. **Configuration Verification**
   - Verify config.py contains all 13 departments
   - Check QUESTION_TYPES configuration integrity

### Monthly Maintenance (30 minutes)
1. **Comprehensive System Analysis**
   ```bash
   python monitoring/future_roadmap_analysis.py
   ```

2. **Performance Baseline Update**
   - Document current response times
   - Record system resource usage
   - Update performance metrics

3. **Security Review**
   - Review access logs
   - Check for any security advisories
   - Verify secure cookie configuration

---

## 🐛 Troubleshooting Guide

### Problem Category 1: Question Loading Issues

#### Symptom: "問題が不足しています (0問 < 10問必要)"
**Root Cause Analysis:**
- Most common cause: CSV file encoding issues
- Secondary cause: Missing or corrupted data files
- Tertiary cause: Incorrect category filtering

**Diagnostic Steps:**
1. **Verify Data Files Present**
   ```bash
   dir data\4-1.csv
   dir data\4-2_*.csv
   ```
   Expected: 4-1.csv + 11 specialist year files (4-2_2008 through 4-2_2018)

2. **Check File Encoding**
   ```python
   # Check CSV file can be read
   with open('data/4-1.csv', 'r', encoding='utf-8') as f:
       lines = f.readlines()
       print(f"4-1.csv: {len(lines)} lines loaded")
   ```
   Expected output: "4-1.csv: 203 lines loaded" (202 questions + header)

3. **Verify Question Loading Function**
   ```python
   from utils import load_questions_improved
   questions = load_questions_improved('basic', '2018', 'all')
   print(f"Loaded questions: {len(questions)}")
   ```

**Solutions:**
- **File Missing**: Restore from backup or re-download data files
- **Encoding Issue**: Re-save CSV files with UTF-8 encoding
- **Permission Issue**: Check file permissions and directory access

#### Symptom: Questions from Wrong Department Appearing
**Root Cause Analysis:**
- Category mapping mismatch
- Department configuration error
- Data file contamination

**Diagnostic Steps:**
1. **Check Department Configuration**
   ```python
   from config import RCCMConfig
   departments = RCCMConfig.DEPARTMENTS
   for dept_id, info in departments.items():
       print(f"{dept_id}: {info['name']}")
   ```

2. **Verify Question Categories in Data**
   ```python
   import pandas as pd
   df = pd.read_csv('data/4-2_2018.csv', encoding='utf-8')
   categories = df['category'].unique()
   print("Available categories:", categories)
   ```

**Solutions:**
- **Configuration Fix**: Update config.py DEPARTMENTS mapping
- **Data Cleanup**: Verify CSV category values match configuration
- **Cache Clear**: Restart application to clear any cached data

### Problem Category 2: Parameter Validation Errors

#### Symptom: ValidationError exceptions in logs
**Root Cause Analysis:**
- Invalid parameter format
- Schema definition mismatch
- Missing required parameters

**Diagnostic Steps:**
1. **Test Parameter Validation Directly**
   ```python
   from schemas.validation_schemas import validate_exam_parameters
   from werkzeug.datastructures import ImmutableMultiDict
   
   # Test with known good parameters
   test_params = ImmutableMultiDict([
       ('department', 'road'),
       ('question_type', 'specialist'),
       ('category', 'all')
   ])
   
   try:
       result = validate_exam_parameters(test_params)
       print("Validation successful:", result)
   except Exception as e:
       print("Validation failed:", e)
   ```

2. **Check Schema Definitions**
   ```python
   from schemas.validation_schemas import ExamParameterSchema
   schema = ExamParameterSchema()
   print("Schema fields:", schema.fields.keys())
   ```

**Solutions:**
- **Parameter Format**: Ensure parameters match expected schema
- **Schema Update**: Modify validation schema if requirements changed
- **Fallback Mechanism**: Verify legacy parameter processing is working

### Problem Category 3: Template Rendering Problems

#### Symptom: "ページが見つかりません" or blank pages
**Root Cause Analysis:**
- Template file missing or corrupted
- Template variable context missing
- Template inheritance issues

**Diagnostic Steps:**
1. **Verify Template Files**
   ```bash
   dir templates\*.html
   ```
   Expected: 37 template files including core templates

2. **Test Template Rendering**
   ```python
   from flask import Flask, render_template
   app = Flask(__name__)
   
   with app.app_context():
       # Test basic template rendering
       html = render_template('base.html')
       print("Base template renders:", len(html) > 0)
   ```

3. **Check Template Variables**
   - Verify template context in route functions
   - Check for missing or undefined variables

**Solutions:**
- **File Restore**: Replace corrupted templates from backup
- **Context Fix**: Ensure all required variables are passed to template
- **Inheritance Check**: Verify template extends correct base template

### Problem Category 4: Session Management Issues

#### Symptom: Lost progress or unexpected redirects
**Root Cause Analysis:**
- Session configuration issues
- Cookie problems
- Session variable corruption

**Diagnostic Steps:**
1. **Check Session Configuration**
   ```python
   from config import Config
   print("Session cookie name:", Config.SESSION_COOKIE_NAME)
   print("Session lifetime:", Config.PERMANENT_SESSION_LIFETIME)
   ```

2. **Test Session Functionality**
   ```python
   from flask import Flask, session
   app = Flask(__name__)
   app.config.from_object('config.DevelopmentConfig')
   
   with app.test_client() as client:
       with client.session_transaction() as sess:
           sess['test'] = 'value'
       
       response = client.get('/')
       print("Session test successful")
   ```

**Solutions:**
- **Config Update**: Review session configuration settings
- **Cookie Clear**: Clear browser cookies and restart session
- **Secret Key**: Verify SECRET_KEY is properly configured

---

## 🔍 Advanced Diagnostic Tools

### System Health Monitor Usage
```bash
# Generate comprehensive health report
python monitoring/system_health_monitor.py

# Check specific component
python -c "
from monitoring.system_health_monitor import UltraSyncHealthMonitor
monitor = UltraSyncHealthMonitor()
integrity = monitor.check_implementation_integrity()
print('Implementation status:', integrity['overall_status'])
"
```

### Future Enhancement Analysis
```bash
# Generate strategic roadmap analysis
python monitoring/future_roadmap_analysis.py

# Review specific improvement areas
python -c "
import json
with open('monitoring/future_roadmap.json', 'r') as f:
    roadmap = json.load(f)
    strategic = roadmap['strategic_roadmap']
    print('Medium-term opportunities:', len(strategic['medium_term_opportunities']))
"
```

### Performance Monitoring
```python
# Basic performance metrics
import time
import psutil
import os

# Application size metrics
app_size = os.path.getsize('app.py')
print(f"App.py size: {app_size / 1024:.1f} KB")

# Template count
template_count = len([f for f in os.listdir('templates') if f.endswith('.html')])
print(f"Template files: {template_count}")

# Data file metrics
data_files = [f for f in os.listdir('data') if f.endswith('.csv')]
total_data_size = sum(os.path.getsize(f'data/{f}') for f in data_files)
print(f"Data files: {len(data_files)}, Total size: {total_data_size / 1024:.1f} KB")
```

---

## 🛡️ Security Maintenance

### Security Checklist (Monthly)
- [ ] **Session Security**: Verify secure cookie flags in production
- [ ] **Input Validation**: Test parameter validation with edge cases
- [ ] **File Permissions**: Check data directory access permissions
- [ ] **Dependencies**: Review for security advisories

### Security Monitoring Commands
```bash
# Check current security configuration
python -c "
from config import ProductionConfig
print('Secure cookies:', ProductionConfig.SESSION_COOKIE_SECURE)
print('HTTP only:', ProductionConfig.SESSION_COOKIE_HTTPONLY)
print('SameSite policy:', ProductionConfig.SESSION_COOKIE_SAMESITE)
"

# Test input validation security
python -c "
from schemas.validation_schemas import validate_exam_parameters
from werkzeug.datastructures import ImmutableMultiDict

# Test with malicious input
malicious_params = ImmutableMultiDict([('department', '<script>alert(1)</script>')])
try:
    validate_exam_parameters(malicious_params)
    print('Security test FAILED: Malicious input accepted')
except:
    print('Security test PASSED: Malicious input rejected')
"
```

---

## 📊 Performance Optimization

### Performance Monitoring
```python
# Response time measurement
import time
import requests

def measure_response_time(url):
    start_time = time.time()
    try:
        response = requests.get(url, timeout=10)
        end_time = time.time()
        return {
            'status_code': response.status_code,
            'response_time': end_time - start_time,
            'content_length': len(response.content)
        }
    except Exception as e:
        return {'error': str(e)}

# Test key endpoints (when server is running)
endpoints = [
    'http://localhost:5000/',
    'http://localhost:5000/departments',
    'http://localhost:5000/departments/road/types'
]

for endpoint in endpoints:
    result = measure_response_time(endpoint)
    print(f"{endpoint}: {result}")
```

### Optimization Recommendations
Based on current system analysis:

1. **Template Optimization** (Future consideration)
   - Current: 37 templates with some inline CSS/JS
   - Opportunity: External CSS/JS files for better caching
   - Priority: Low (current performance acceptable)

2. **Database Optimization** (Future consideration)
   - Current: CSV-based question storage
   - Opportunity: SQLite database for better query performance
   - Priority: Future (only if scale increases significantly)

3. **Caching Implementation** (Future consideration)
   - Current: No response caching
   - Opportunity: Flask-Caching for static content
   - Priority: Low (current response times acceptable)

---

## 🗄️ Backup and Recovery

### Backup Strategy
```bash
# Complete system backup
set BACKUP_DATE=%date:~-4,4%-%date:~-10,2%-%date:~-7,2%
mkdir backup\full_backup_%BACKUP_DATE%

# Copy critical files
xcopy *.py backup\full_backup_%BACKUP_DATE%\ /Y
xcopy config.py backup\full_backup_%BACKUP_DATE%\ /Y
xcopy requirements.txt backup\full_backup_%BACKUP_DATE%\ /Y

# Copy directories
xcopy data\* backup\full_backup_%BACKUP_DATE%\data\ /E /I
xcopy templates\* backup\full_backup_%BACKUP_DATE%\templates\ /E /I
xcopy schemas\* backup\full_backup_%BACKUP_DATE%\schemas\ /E /I

echo Backup completed: backup\full_backup_%BACKUP_DATE%
```

### Recovery Procedures
In case of system corruption:

1. **Identify Corruption Scope**
   ```bash
   python monitoring/system_health_monitor.py
   ```
   Review health report for missing or corrupted files

2. **Selective File Recovery**
   ```bash
   # Restore specific files from backup
   copy backup\latest\app.py app.py
   copy backup\latest\config.py config.py
   ```

3. **Complete System Recovery**
   ```bash
   # Full restoration from backup
   xcopy backup\full_backup_YYYY-MM-DD\* . /E /Y
   ```

4. **Verification After Recovery**
   ```bash
   python monitoring/system_health_monitor.py
   python app.py
   ```

---

## 📞 Support and Escalation

### Self-Service Resolution
1. **Check System Health**: Run monitoring tools
2. **Review Logs**: Check health_log.json for recent issues
3. **Verify Configuration**: Ensure config.py is intact
4. **Test Components**: Use diagnostic commands above

### Escalation Criteria
Escalate to senior technical support if:
- Multiple system health checks fail
- Data corruption affects multiple CSV files
- Security-related issues are detected
- Performance degrades significantly (>5x slower)

### Documentation Updates
When resolving new issues:
1. Document the problem and solution
2. Update this troubleshooting manual
3. Create preventive measures if applicable
4. Share knowledge with team members

---

## 📈 Monitoring and Alerting

### Automated Monitoring Setup
```python
# Create monitoring script for regular execution
# File: monitoring/scheduled_health_check.py

import schedule
import time
from system_health_monitor import run_health_monitoring

def automated_health_check():
    print("Running scheduled health check...")
    result = run_health_monitoring()
    
    if result and result['implementation_integrity']['overall_status'] != 'HEALTHY':
        print("WARNING: System health issue detected!")
        # Add notification logic here (email, log alert, etc.)

# Schedule daily health checks
schedule.every().day.at("09:00").do(automated_health_check)
schedule.every().day.at("17:00").do(automated_health_check)

# Keep monitoring running
while True:
    schedule.run_pending()
    time.sleep(3600)  # Check every hour
```

### Key Metrics to Monitor
- **File Integrity**: All critical files present and correct size
- **Implementation Status**: PHASE 1 components functioning
- **Response Times**: Homepage and key endpoints under 2 seconds
- **Error Rates**: Less than 1% of requests resulting in errors
- **Data Consistency**: Question loading successful for all departments

---

This maintenance manual provides comprehensive guidance for keeping the RCCM Quiz Application running smoothly. Regular use of these procedures will ensure system stability and early detection of any issues.