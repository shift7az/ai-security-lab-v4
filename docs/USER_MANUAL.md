# AI Security Lab v4.0 - User Manual

Complete guide for using the AI Security Lab dashboard and features.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Dashboard Overview](#dashboard-overview)
3. [Camera Management](#camera-management)
4. [Threat Detection](#threat-detection)
5. [Alert System](#alert-system)
6. [Settings & Configuration](#settings--configuration)
7. [User Management](#user-management)
8. [Reports & Analytics](#reports--analytics)
9. [Best Practices](#best-practices)

---

## Getting Started

### First Login

1. Navigate to: `http://your-server:3000/login`
2. Enter your credentials:
   - **Username:** admin
   - **Password:** (provided by system administrator)
3. Click "Sign In"

### Dashboard Navigation

The main interface consists of:
- **Top Navigation Bar:** Access to different sections
- **Side Menu:** Quick links to key features
- **Main Content Area:** Current view
- **Status Indicators:** System health and alerts

---

## Dashboard Overview

### Main Dashboard

The default view shows:

#### System Health Status
- **Online/Offline Status:** Green = healthy, Red = issue
- **Active Cameras:** Number of cameras streaming
- **Total Detections:** Detections in last 24 hours
- **Active Alerts:** Current unresolved alerts

#### Threat Overview
Real-time visualization of threats by severity:
- **Critical:** Immediate action required
- **High:** Attention needed soon
- **Medium:** Monitor situation
- **Low:** Informational

#### Camera Grid
Live view of all camera feeds with:
- Camera name and location
- Current status indicator
- Recent detection count
- Quick access menu

#### Recent Alerts Panel
Latest security alerts with:
- Timestamp
- Threat level
- Location (camera)
- Quick actions (View, Acknowledge, Dismiss)

---

## Camera Management

### Viewing Cameras

1. Navigate to **Dashboard**
2. Camera grid shows all active cameras
3. Click any camera for detailed view

### Camera Details

Individual camera view shows:
- Live feed (if available)
- Camera metadata (name, location, status)
- Detection history
- Performance metrics

### Adding a Camera

1. Navigate to **Settings** > **Cameras**
2. Click **"Add Camera"**
3. Fill in details:
   ```
   Name: Front Entrance
   Location: Building A, Main Entrance
   Stream URL: rtsp://camera-ip:554/stream
   Status: Active
   ```
4. Click **"Save"**

### Camera Status Indicators

- 🟢 **Online:** Camera streaming normally
- 🟡 **Warning:** Connection issues
- 🔴 **Offline:** Camera not responding
- 🔵 **Maintenance:** Scheduled maintenance

### Troubleshooting Cameras

**Camera Offline:**
1. Check network connection
2. Verify stream URL is correct
3. Test camera credentials
4. Check camera power status

**Poor Video Quality:**
1. Adjust resolution settings
2. Check network bandwidth
3. Verify camera focus
4. Clean camera lens

---

## Threat Detection

### Understanding Threat Levels

**Critical (Red):**
- Weapons detected
- Unauthorized access to restricted areas
- Aggressive behavior
- **Response:** Immediate action required

**High (Orange):**
- Suspicious behavior patterns
- Unusual activity in secure zones
- Multiple people in restricted area
- **Response:** Investigate within 5 minutes

**Medium (Yellow):**
- Loitering detected
- After-hours activity
- Unidentified vehicles
- **Response:** Monitor and assess

**Low (Green):**
- Normal activity patterns
- Expected behaviors
- Routine movements
- **Response:** Log and track

### Detection Types

1. **Weapon Detection**
   - Firearms
   - Knives
   - Other weapons

2. **Behavior Analysis**
   - Loitering
   - Running
   - Fighting
   - Falling

3. **Access Control**
   - Unauthorized entry
   - Tailgating
   - After-hours access

4. **Crowd Detection**
   - Crowd gathering
   - Density monitoring
   - Flow analysis

### Viewing Detections

1. Navigate to **Detections**
2. Use filters:
   - **Date Range:** Last 24h, 7d, 30d, Custom
   - **Threat Level:** All, Critical, High, Medium, Low
   - **Camera:** All cameras or specific
   - **Type:** All types or specific

3. Click any detection for details:
   - Snapshot image
   - Detection confidence score
   - Timestamp
   - Camera location
   - AI model used
   - Related alerts

### False Positives

If you identify a false detection:

1. Open the detection detail
2. Click **"Mark as False Positive"**
3. Provide reason (optional)
4. System learns and improves

---

## Alert System

### Alert Priority Levels

**Critical:**
- Immediate notification
- SMS + Email + Dashboard
- Auto-escalate after 2 minutes

**High:**
- Urgent notification
- Email + Dashboard
- Escalate after 5 minutes

**Medium:**
- Standard notification
- Dashboard only
- Review within 15 minutes

**Low:**
- Info notification
- Dashboard log
- Review as needed

### Managing Alerts

#### Acknowledging Alerts

1. Navigate to **Alerts** section
2. Find the alert
3. Click **"Acknowledge"**
4. Add notes (optional)
5. Alert moved to "Acknowledged" status

#### Resolving Alerts

1. Open alert details
2. Click **"Resolve"**
3. Select resolution type:
   - False Alarm
   - Handled
   - Escalated
   - Other
4. Add resolution notes
5. Alert archived

#### Alert Filters

Filter alerts by:
- Status: Active, Acknowledged, Resolved
- Priority: All, Critical, High, Medium, Low
- Time Range: Today, Week, Month, Custom
- Camera: All or specific
- Type: Threat, System, Camera

### Alert Notifications

**Dashboard Notifications:**
- Real-time popup alerts
- Audio notifications (can disable)
- Notification badge counter

**Email Notifications:**
Configure in **Settings** > **Notifications**:
- Enable/disable per priority level
- Set email addresses
- Customize message template

**SMS Notifications (Enterprise):**
- Available for Critical and High alerts
- Configure in **Settings** > **Notifications**
- Requires SMS service integration

---

## Settings & Configuration

### System Settings

Navigate to **Settings** to configure:

#### General Settings
- System Name
- Timezone
- Language
- Date/Time Format

#### Detection Settings
- Confidence Threshold (0-100%)
- Detection Sensitivity
- Minimum Object Size
- Frame Processing Rate

#### Alert Settings
- Auto-acknowledge timeout
- Escalation rules
- Notification preferences
- Alert retention period

#### Performance Settings
- Max Concurrent Analyses
- Queue Size
- Worker Count
- GPU Acceleration

### Viewing Current Settings

1. Navigate to **Settings**
2. Settings grouped by category
3. Current values displayed
4. Click **"Edit"** to modify

### Modifying Settings

1. Click **"Edit"** next to setting
2. Update value
3. Click **"Save"**
4. System applies changes automatically

**Note:** Some settings require service restart to take effect.

---

## User Management

### User Roles

**Admin:**
- Full system access
- User management
- System configuration
- All monitoring features

**Operator:**
- View cameras and detections
- Manage alerts
- Generate reports
- Limited settings access

**Viewer:**
- View-only access
- See cameras and detections
- View alerts
- No configuration access

### Managing Users (Admin Only)

#### Adding Users

1. Navigate to **Settings** > **Users**
2. Click **"Add User"**
3. Fill in details:
   ```
   Username: john.doe
   Email: john.doe@company.com
   Role: Operator
   Password: (auto-generated or set)
   ```
4. Click **"Create User"**
5. User receives welcome email

#### Editing Users

1. Navigate to **Settings** > **Users**
2. Find user in list
3. Click **"Edit"**
4. Update details
5. Click **"Save"**

#### Deactivating Users

1. Navigate to **Settings** > **Users**
2. Find user
3. Click **"Deactivate"**
4. Confirm action
5. User can no longer log in

### Password Management

**Changing Your Password:**
1. Click profile icon (top right)
2. Select **"Change Password"**
3. Enter current password
4. Enter new password (twice)
5. Click **"Update Password"**

**Password Requirements:**
- Minimum 8 characters
- At least one uppercase letter
- At least one number
- At least one special character

---

## Reports & Analytics

### Dashboard Charts

#### Threat Trend Chart
- Line chart showing threats over time
- Filter by severity level
- Adjustable time range
- Export data as CSV

#### Camera Heatmap
- Visual representation of activity by camera
- Color-coded intensity
- Shows hotspots
- Helps identify high-traffic areas

#### Alert Distribution
- Pie chart of alert types
- Breakdown by category
- Percentage distribution
- Total count display

#### System Metrics
- CPU, Memory, GPU usage
- Historical trends
- Performance indicators
- Health status

### Generating Reports

1. Navigate to **Reports**
2. Select report type:
   - Daily Summary
   - Weekly Analysis
   - Monthly Report
   - Custom Range

3. Configure options:
   - Date range
   - Cameras to include
   - Threat levels
   - Output format (PDF, CSV, JSON)

4. Click **"Generate Report"**
5. Download when ready

### Scheduled Reports

**Setting Up Automated Reports:**
1. Navigate to **Reports** > **Scheduled**
2. Click **"New Schedule"**
3. Configure:
   - Report type
   - Frequency (Daily, Weekly, Monthly)
   - Recipients (email addresses)
   - Format
4. Click **"Save Schedule"**

Reports automatically emailed on schedule.

---

## Best Practices

### Daily Operations

**Morning Routine:**
1. Check system health status
2. Review overnight alerts
3. Verify all cameras online
4. Clear acknowledged alerts

**During Day:**
1. Monitor active alerts
2. Respond to critical threats immediately
3. Investigate high-priority detections
4. Document incidents

**End of Day:**
1. Review day's activity summary
2. Resolve pending alerts
3. Check system performance
4. Plan next day's focus areas

### Threat Response

**Critical Threats:**
1. Verify threat on camera feed
2. Dispatch security/police immediately
3. Monitor situation continuously
4. Document all actions
5. Follow organizational protocols

**High Priority:**
1. Assess situation from cameras
2. Determine response needed
3. Dispatch appropriate personnel
4. Monitor until resolved
5. Log outcome

**Medium/Low Priority:**
1. Review detection details
2. Determine if investigation needed
3. Schedule follow-up if required
4. Document findings
5. Update alert status

### System Maintenance

**Weekly Tasks:**
- Review false positive rate
- Check camera health
- Update user accounts
- Archive old alerts
- Review system performance

**Monthly Tasks:**
- Generate performance reports
- Update system settings
- Review user access logs
- Plan system improvements
- Backup configuration

### Getting Help

**In-App Help:**
- Click **"?"** icon (top right)
- Access contextual help
- View keyboard shortcuts
- Watch tutorial videos

**Support Resources:**
- Documentation: `/docs`
- FAQ: `/docs/FAQ.md`
- GitHub Issues: Report bugs
- Email: support@example.com

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `/` | Focus search |
| `g h` | Go to home |
| `g c` | Go to cameras |
| `g a` | Go to alerts |
| `g s` | Go to settings |
| `r` | Refresh data |
| `?` | Show shortcuts |
| `Esc` | Close modals |

---

## Glossary

**Detection:** An AI-identified object or behavior in camera footage

**Threat Level:** Severity rating assigned to a detection

**Alert:** A notification requiring attention or action

**Camera Feed:** Live or recorded video stream from a camera

**Confidence Score:** AI's certainty level (0-100%) about a detection

**False Positive:** Incorrect detection that should be ignored

**Hypertable:** Time-series database table for efficient data storage

**WebSocket:** Technology enabling real-time data updates

---

**Version:** 4.0.0  
**Last Updated:** January 2025  
**Support:** support@example.com
