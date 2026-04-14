/**
 * Quick Help FAB - Floating Action Button for contextual help
 * Enhanced with modern design and module-specific content
 */
(function() {
  'use strict';

  // Module configurations with icons, colors, and detailed help
  var moduleConfig = {
    dashboard: {
      icon: 'dashboard',
      color: '#3b82f6',
      gradient: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)',
      title: 'Dashboard Overview',
      sections: [
        { icon: '📊', title: 'Statistics Cards', desc: 'View key metrics at a glance - users, proposals, projects, and pending extensions.' },
        { icon: '🗺️', title: 'Interactive Map', desc: 'See project locations on the map. Click markers for details. Use arrow keys to navigate.' },
        { icon: '📈', title: 'Charts & Analytics', desc: 'Visual breakdowns of project status, user roles, and trends over time.' },
        { icon: '🕐', title: 'Activity Feed', desc: 'Recent system activities and audit logs for quick monitoring.' }
      ],
      tip: 'Click on the map to find nearest projects. Toggle Simple Mode to focus on essentials.'
    },
    projects: {
      icon: 'folder_open',
      color: '#8b5cf6',
      gradient: 'linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%)',
      title: 'Projects Management',
      sections: [
        { icon: '📁', title: 'Project List', desc: 'View all projects with status, budget, and timeline information.' },
        { icon: '➕', title: 'Add Project', desc: 'Click the blue "Add Project" button to create a new project from an approved proposal.' },
        { icon: '✏️', title: 'Edit & Update', desc: 'Click Edit on any project to modify details, status, or assignments.' },
        { icon: '📋', title: 'Project Details', desc: 'Click on a project title to view full details, tasks, and documents.' }
      ],
      tip: 'Use filters to quickly find projects by status, municipality, or date range.'
    },
    proposals: {
      icon: 'description',
      color: '#10b981',
      gradient: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
      title: 'Proposals Management',
      sections: [
        { icon: '📝', title: 'Submit Proposals', desc: 'Create new project proposals for review and approval.' },
        { icon: '✅', title: 'Approve/Decline', desc: 'Review pending proposals and take action to approve or decline.' },
        { icon: '📎', title: 'Attachments', desc: 'Upload supporting documents for each proposal.' },
        { icon: '🔄', title: 'Status Tracking', desc: 'Monitor proposal status: Pending → Approved/Declined → Project' }
      ],
      tip: 'Approved proposals can be converted to projects with budget allocation.'
    },
    budgets: {
      icon: 'account_balance_wallet',
      color: '#f59e0b',
      gradient: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
      title: 'Budget Management',
      sections: [
        { icon: '💰', title: 'Budget Overview', desc: 'Track total equipment value, deliveries, and pending allocations.' },
        { icon: '📊', title: 'Fund Sources', desc: 'View breakdowns by fund source (GIA, SETUP, etc.) and fiscal year.' },
        { icon: '🎯', title: 'Allocations', desc: 'Click on budget cards to see detailed allocation breakdown.' },
        { icon: '📈', title: 'Utilization', desc: 'Monitor delivery rates and budget utilization across projects.' }
      ],
      tip: 'Use the fund filter to focus on specific budget sources.'
    },
    users: {
      icon: 'people',
      color: '#ec4899',
      gradient: 'linear-gradient(135deg, #ec4899 0%, #db2777 100%)',
      title: 'User Management',
      sections: [
        { icon: '👥', title: 'User Directory', desc: 'View all system users with their roles and status.' },
        { icon: '➕', title: 'Add User', desc: 'Create new accounts for administrators, staff, proponents, or beneficiaries.' },
        { icon: '🔑', title: 'Role Assignment', desc: 'Assign appropriate roles to control access and permissions.' },
        { icon: '🔒', title: 'Account Status', desc: 'Activate or deactivate user accounts as needed.' }
      ],
      tip: 'Each role has different access levels. Administrators have full access.'
    },
    tasks: {
      icon: 'task_alt',
      color: '#06b6d4',
      gradient: 'linear-gradient(135deg, #06b6d4 0%, #0891b2 100%)',
      title: 'Task Management',
      sections: [
        { icon: '✅', title: 'Task List', desc: 'View and manage tasks assigned to projects.' },
        { icon: '📅', title: 'Due Dates', desc: 'Track deadlines and prioritize work accordingly.' },
        { icon: '👤', title: 'Assignments', desc: 'Assign tasks to specific staff members.' },
        { icon: '📊', title: 'Progress', desc: 'Update task status: Pending → In Progress → Completed' }
      ],
      tip: 'Overdue tasks are highlighted in red. Keep tasks updated for accurate reporting.'
    },
    calendar: {
      icon: 'calendar_month',
      color: '#6366f1',
      gradient: 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)',
      title: 'Calendar & Events',
      sections: [
        { icon: '📅', title: 'Event View', desc: 'See all events, deadlines, and milestones in calendar format.' },
        { icon: '➕', title: 'Add Event', desc: 'Click on any date to add a new event.' },
        { icon: '🔔', title: 'Reminders', desc: 'Events appear as colored blocks. Click to view details.' },
        { icon: '📋', title: 'Event Types', desc: 'Different colors indicate different event categories.' }
      ],
      tip: 'Click on an event to view details or delete it. Use month/week navigation.'
    },
    reports: {
      icon: 'assessment',
      color: '#14b8a6',
      gradient: 'linear-gradient(135deg, #14b8a6 0%, #0d9488 100%)',
      title: 'Reports & Analytics',
      sections: [
        { icon: '📊', title: 'Generate Reports', desc: 'Create PDF and Excel reports for various data sets.' },
        { icon: '🔍', title: 'Filters', desc: 'Apply date range, status, and other filters before generating.' },
        { icon: '📥', title: 'Export', desc: 'Download reports in PDF or Excel format.' },
        { icon: '📈', title: 'Visualizations', desc: 'Reports include charts and summaries for easy analysis.' }
      ],
      tip: 'Use filters to narrow down data before exporting for more relevant reports.'
    },
    settings: {
      icon: 'settings',
      color: '#64748b',
      gradient: 'linear-gradient(135deg, #64748b 0%, #475569 100%)',
      title: 'Account Settings',
      sections: [
        { icon: '👤', title: 'Profile', desc: 'Update your personal information and profile picture.' },
        { icon: '🔐', title: 'Password', desc: 'Change your password for security.' },
        { icon: '✍️', title: 'Signature', desc: 'Upload or create your digital signature.' },
        { icon: '⚙️', title: 'Preferences', desc: 'Configure display and notification preferences.' }
      ],
      tip: 'Keep your profile updated and change passwords regularly for security.'
    },
    'extension-requests': {
      icon: 'schedule',
      color: '#f97316',
      gradient: 'linear-gradient(135deg, #f97316 0%, #ea580c 100%)',
      title: 'Extension Requests',
      sections: [
        { icon: '📅', title: 'Request Extensions', desc: 'Submit requests to extend project deadlines.' },
        { icon: '✅', title: 'Approve/Reject', desc: 'Review and process extension requests.' },
        { icon: '📝', title: 'Justification', desc: 'Provide reasons for extension requests.' },
        { icon: '📊', title: 'History', desc: 'View past extension requests and their status.' }
      ],
      tip: 'Provide detailed justification to increase approval chances.'
    },
    'communication': {
      icon: 'forum',
      color: '#8b5cf6',
      gradient: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
      title: 'Communication Hub',
      sections: [
        { icon: '💬', title: 'Messages', desc: 'Send and receive direct messages with other users.' },
        { icon: '👥', title: 'Group Chats', desc: 'Create and participate in group discussions.' },
        { icon: '📢', title: 'Announcements', desc: 'View and post system-wide announcements.' },
        { icon: '🔔', title: 'Notifications', desc: 'Stay updated with message notifications.' }
      ],
      tip: 'Use @mentions to notify specific users in messages.'
    }
  };

  var defaultConfig = {
    icon: 'help',
    color: '#3b82f6',
    gradient: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
    title: 'Quick Help',
    sections: [
      { icon: '🎯', title: 'Simple Mode', desc: 'Toggle to show only essential information and hide complex features.' },
      { icon: '🌙', title: 'Dark Mode', desc: 'Toggle for comfortable viewing in low-light environments.' },
      { icon: '🔍', title: 'Search', desc: 'Use the search bar to quickly find projects, users, or documents.' },
      { icon: '❓', title: 'Need Help?', desc: 'Click this button on any page for context-specific guidance.' }
    ],
    tip: 'Navigate using the sidebar menu. Each module has its own help content.'
  };

  function getModuleFromPath() {
    var path = window.location.pathname.toLowerCase();
    if (path.includes('/dashboard')) return 'dashboard';
    if (path.includes('/projects')) return 'projects';
    if (path.includes('/proposals')) return 'proposals';
    if (path.includes('/budgets')) return 'budgets';
    if (path.includes('/users')) return 'users';
    if (path.includes('/tasks')) return 'tasks';
    if (path.includes('/calendar')) return 'calendar';
    if (path.includes('/reports')) return 'reports';
    if (path.includes('/settings')) return 'settings';
    if (path.includes('/extension')) return 'extension-requests';
    if (path.includes('/communication') || path.includes('/messages') || path.includes('/announcements')) return 'communication';
    return null;
  }

  function getConfig() {
    var module = getModuleFromPath();
    return module && moduleConfig[module] ? moduleConfig[module] : defaultConfig;
  }

  function init() {
    if (document.getElementById('quickHelpFAB')) return;
    
    var config = getConfig();

    // Create FAB
    var fab = document.createElement('button');
    fab.id = 'quickHelpFAB';
    fab.setAttribute('aria-label', 'Quick Help');
    fab.innerHTML = '<span class="material-icons">' + config.icon + '</span>';
    fab.style.cssText = [
      'position: fixed',
      'bottom: 24px',
      'right: 24px',
      'width: 60px',
      'height: 60px',
      'border-radius: 50%',
      'background: ' + config.gradient,
      'color: white',
      'border: none',
      'cursor: pointer',
      'box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2), 0 0 0 0 ' + config.color + '40',
      'display: flex',
      'align-items: center',
      'justify-content: center',
      'z-index: 9990',
      'transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
      'animation: fabPulse 2s infinite'
    ].join(';');

    // Add pulse animation
    var style = document.createElement('style');
    style.textContent = '@keyframes fabPulse { 0%, 100% { box-shadow: 0 4px 15px rgba(0,0,0,0.2), 0 0 0 0 ' + config.color + '40; } 50% { box-shadow: 0 4px 15px rgba(0,0,0,0.2), 0 0 0 8px ' + config.color + '00; } }';
    document.head.appendChild(style);

    fab.onmouseenter = function() {
      fab.style.transform = 'scale(1.1) rotate(10deg)';
      fab.style.boxShadow = '0 8px 25px rgba(0,0,0,0.3)';
    };
    fab.onmouseleave = function() {
      fab.style.transform = 'scale(1) rotate(0deg)';
      fab.style.boxShadow = '0 4px 15px rgba(0,0,0,0.2)';
    };

    fab.onclick = openHelpModal;
    document.body.appendChild(fab);
    createModal();
  }

  function createModal() {
    if (document.getElementById('quickHelpModal')) return;

    var modal = document.createElement('div');
    modal.id = 'quickHelpModal';
    modal.style.cssText = 'display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.6);z-index:9999;align-items:center;justify-content:center;backdrop-filter:blur(4px);';

    var content = document.createElement('div');
    content.id = 'quickHelpContent';
    content.style.cssText = 'background:white;border-radius:20px;max-width:480px;width:90%;max-height:85vh;overflow:hidden;box-shadow:0 25px 50px -12px rgba(0,0,0,0.25);animation:modalSlideIn 0.3s ease-out;';

    // Add animation
    var animStyle = document.createElement('style');
    animStyle.textContent = '@keyframes modalSlideIn { from { opacity: 0; transform: translateY(20px) scale(0.95); } to { opacity: 1; transform: translateY(0) scale(1); } }';
    document.head.appendChild(animStyle);

    modal.appendChild(content);
    modal.onclick = function(e) { if (e.target === modal) closeHelpModal(); };
    document.addEventListener('keydown', function(e) { if (e.key === 'Escape') closeHelpModal(); });
    document.body.appendChild(modal);
  }

  function openHelpModal() {
    var modal = document.getElementById('quickHelpModal');
    var content = document.getElementById('quickHelpContent');
    if (!modal || !content) return;

    var config = getConfig();
    
    // Check for page-specific module-help div first
    var moduleHelpDiv = document.getElementById('module-help');
    var customContent = moduleHelpDiv ? moduleHelpDiv.innerHTML : null;

    var html = '';
    
    // Header
    html += '<div style="background:' + config.gradient + ';color:white;padding:24px;position:relative;">';
    html += '<div style="display:flex;align-items:center;gap:12px;">';
    html += '<span class="material-icons" style="font-size:32px;">' + config.icon + '</span>';
    html += '<div>';
    html += '<h3 style="margin:0;font-size:22px;font-weight:700;">' + config.title + '</h3>';
    html += '<p style="margin:4px 0 0;opacity:0.9;font-size:14px;">How to use this module</p>';
    html += '</div>';
    html += '</div>';
    html += '<button onclick="document.getElementById(\'quickHelpModal\').style.display=\'none\'" style="position:absolute;top:16px;right:16px;background:rgba(255,255,255,0.2);border:none;color:white;width:36px;height:36px;border-radius:50%;cursor:pointer;font-size:20px;display:flex;align-items:center;justify-content:center;transition:background 0.2s;" onmouseenter="this.style.background=\'rgba(255,255,255,0.3)\'" onmouseleave="this.style.background=\'rgba(255,255,255,0.2)\'">&times;</button>';
    html += '</div>';

    // Body
    html += '<div style="padding:20px;max-height:calc(85vh - 120px);overflow-y:auto;">';
    
    if (customContent) {
      html += '<div style="color:#374151;">' + customContent + '</div>';
    } else {
      // Sections
      config.sections.forEach(function(section) {
        html += '<div style="display:flex;gap:14px;padding:14px;margin-bottom:12px;background:#f8fafc;border-radius:12px;border:1px solid #e2e8f0;transition:all 0.2s;" onmouseenter="this.style.background=\'#f1f5f9\';this.style.transform=\'translateX(4px)\'" onmouseleave="this.style.background=\'#f8fafc\';this.style.transform=\'translateX(0)\'">';
        html += '<div style="font-size:24px;flex-shrink:0;">' + section.icon + '</div>';
        html += '<div>';
        html += '<div style="font-weight:600;color:#1e293b;margin-bottom:4px;">' + section.title + '</div>';
        html += '<div style="color:#64748b;font-size:14px;line-height:1.5;">' + section.desc + '</div>';
        html += '</div>';
        html += '</div>';
      });

      // Tip
      html += '<div style="margin-top:20px;padding:16px;background:linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);border-radius:12px;border-left:4px solid #f59e0b;">';
      html += '<div style="display:flex;align-items:flex-start;gap:10px;">';
      html += '<span style="font-size:20px;">💡</span>';
      html += '<div>';
      html += '<div style="font-weight:600;color:#92400e;margin-bottom:4px;">Pro Tip</div>';
      html += '<div style="color:#a16207;font-size:14px;">' + config.tip + '</div>';
      html += '</div>';
      html += '</div>';
      html += '</div>';
    }

    html += '</div>';

    content.innerHTML = html;
    modal.style.display = 'flex';
  }

  function closeHelpModal() {
    var modal = document.getElementById('quickHelpModal');
    if (modal) modal.style.display = 'none';
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  window.QuickHelp = { open: openHelpModal, close: closeHelpModal };
})();
