// Digital FTE Dashboard - Real-time Updates

let updateInterval;
let chartInstances = {};

/**
 * Fetch status from API endpoint
 */
async function fetchStatus() {
    try {
        const response = await fetch('api/status.json');
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        updateDashboard(data);
    } catch (error) {
        console.error('Failed to fetch status:', error);
        document.getElementById('last-updated').textContent = 'Error loading data';
    }
}

/**
 * Update all dashboard elements with fresh data
 */
function updateDashboard(data) {
    // Update timestamp
    const date = new Date(data.timestamp);
    document.getElementById('last-updated').textContent = date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        timeZone: 'UTC'
    }) + ' UTC';

    // Update status cards
    const watchers = data.watchers;
    document.getElementById('watchers-count').textContent = `${watchers.online}/${watchers.total}`;
    document.getElementById('pending-count').textContent = data.pending_actions;
    document.getElementById('approval-count').textContent = data.pending_approvals;
    document.getElementById('completed-count').textContent = data.completed_today;

    // Update FTE metrics
    if (data.fte_metrics) {
        updateFTEMetrics(data.fte_metrics);
    }

    // Update activity timeline
    if (data.recent_activity) {
        updateActivityTimeline(data.recent_activity);
    }

    // Update charts
    if (data.fte_metrics) {
        updateCharts(data.fte_metrics);
    }
}

/**
 * Update FTE performance metrics display
 */
function updateFTEMetrics(metrics) {
    // Gmail FTE
    if (metrics.gmail) {
        document.getElementById('gmail-processed').textContent = metrics.gmail.emails_processed || 0;
        document.getElementById('gmail-rate').textContent =
            Math.round((metrics.gmail.auto_draft_rate || 0) * 100) + '%';
        document.getElementById('gmail-time').textContent =
            Math.round(metrics.gmail.avg_response_time_minutes || 0);
    }

    // WhatsApp FTE
    if (metrics.whatsapp) {
        document.getElementById('whatsapp-processed').textContent = metrics.whatsapp.messages_processed || 0;
        document.getElementById('whatsapp-urgent').textContent = metrics.whatsapp.urgent_flags || 0;
        document.getElementById('whatsapp-rate').textContent =
            Math.round((metrics.whatsapp.escalation_rate || 0) * 100) + '%';
    }

    // Calendar FTE
    if (metrics.calendar) {
        document.getElementById('calendar-processed').textContent = metrics.calendar.events_processed || 0;
        document.getElementById('calendar-conflicts').textContent = metrics.calendar.conflicts_resolved || 0;
        document.getElementById('calendar-briefings').textContent = metrics.calendar.briefings_generated || 0;
    }
}

/**
 * Update activity timeline with recent actions
 */
function updateActivityTimeline(activities) {
    const timeline = document.getElementById('activity-timeline');

    if (!activities || activities.length === 0) {
        timeline.innerHTML = '<div class="text-center text-gray-500 py-8">No activity recorded yet</div>';
        return;
    }

    timeline.innerHTML = activities.slice(0, 10).map(activity => {
        const iconMap = {
            'email': '📧',
            'whatsapp': '💬',
            'file': '📁',
            'calendar': '📅',
            'approval': '✅',
            'error': '⚠️'
        };

        const type = activity.type || 'general';
        const icon = iconMap[type] || '•';

        return `
            <div class="flex items-start gap-3 border-l-2 border-blue-500 pl-4 py-2 hover:bg-gray-700 rounded transition">
                <span class="text-2xl">${icon}</span>
                <div class="flex-1 min-w-0">
                    <p class="text-sm font-medium text-gray-200">${escapeHtml(activity.action)}</p>
                    <p class="text-xs text-gray-400">${escapeHtml(activity.details || '')}</p>
                </div>
                <span class="text-xs text-gray-500 whitespace-nowrap">${activity.timestamp}</span>
            </div>
        `;
    }).join('');
}

/**
 * Update chart visualizations
 */
function updateCharts(metrics) {
    // Gmail Chart
    if (metrics.gmail) {
        updateChart('gmail-chart', 'Gmail FTE', {
            labels: ['Processed', 'Drafted', 'Approved', 'Pending'],
            data: [
                metrics.gmail.emails_processed || 0,
                Math.round((metrics.gmail.emails_processed || 0) * (metrics.gmail.auto_draft_rate || 0)),
                Math.round((metrics.gmail.emails_processed || 0) * (metrics.gmail.auto_draft_rate || 0) * 0.9),
                Math.round((metrics.gmail.emails_processed || 0) * (1 - (metrics.gmail.auto_draft_rate || 0)))
            ]
        });
    }

    // WhatsApp Chart
    if (metrics.whatsapp) {
        updateChart('whatsapp-chart', 'WhatsApp FTE', {
            labels: ['Processed', 'Urgent', 'Escalated', 'Auto-Reply'],
            data: [
                metrics.whatsapp.messages_processed || 0,
                metrics.whatsapp.urgent_flags || 0,
                Math.round((metrics.whatsapp.messages_processed || 0) * (metrics.whatsapp.escalation_rate || 0)),
                Math.round((metrics.whatsapp.messages_processed || 0) * 0.3)
            ]
        });
    }

    // Calendar Chart
    if (metrics.calendar) {
        updateChart('calendar-chart', 'Calendar FTE', {
            labels: ['Processed', 'Conflicts', 'Resolved', 'Briefings'],
            data: [
                metrics.calendar.events_processed || 0,
                metrics.calendar.conflicts_resolved || 0,
                Math.round((metrics.calendar.conflicts_resolved || 0) * 1.2),
                metrics.calendar.briefings_generated || 0
            ]
        });
    }
}

/**
 * Create or update a Chart.js instance
 */
function updateChart(canvasId, label, config) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    const colors = {
        'Gmail FTE': '#3b82f6',
        'WhatsApp FTE': '#10b981',
        'Calendar FTE': '#a855f7'
    };

    // Destroy existing chart if it exists
    if (chartInstances[canvasId]) {
        chartInstances[canvasId].destroy();
    }

    // Create new chart
    chartInstances[canvasId] = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: config.labels,
            datasets: [{
                label: label,
                data: config.data,
                backgroundColor: [
                    colors[label],
                    'rgba(75, 192, 192, 0.6)',
                    'rgba(255, 193, 7, 0.6)',
                    'rgba(244, 67, 54, 0.6)'
                ],
                borderColor: '#1f2937',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#9ca3af',
                        font: { size: 11 }
                    }
                }
            }
        }
    });
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Quick action: Restart all watchers
 */
async function restartWatchers() {
    const confirmed = confirm('Restart all watchers? This will briefly interrupt monitoring.');
    if (!confirmed) return;

    try {
        const response = await fetch('api/restart-watchers', { method: 'POST' });
        if (response.ok) {
            alert('✅ Watchers restarted successfully');
            setTimeout(fetchStatus, 1000);
        } else {
            alert('❌ Failed to restart watchers');
        }
    } catch (error) {
        alert('❌ Error: ' + error.message);
    }
}

/**
 * Quick action: Open Obsidian vault
 */
function openVault() {
    window.location.href = 'obsidian://open?vault=AI_Employee_Vault&file=Pending_Approval';
}

/**
 * Quick action: Generate CEO briefing
 */
async function generateBriefing() {
    if (!confirm('Generate CEO briefing? This may take 30-60 seconds.')) return;

    try {
        const response = await fetch('api/generate-briefing', { method: 'POST' });
        if (response.ok) {
            alert('✅ Briefing generation started. Check /Plans folder in 60 seconds.');
            setTimeout(fetchStatus, 2000);
        } else {
            alert('❌ Failed to generate briefing');
        }
    } catch (error) {
        alert('❌ Error: ' + error.message);
    }
}

/**
 * Quick action: View Constitution
 */
function viewConstitution() {
    window.location.href = 'obsidian://open?vault=AI_Employee_Vault&file=.specify/memory/constitution';
}

/**
 * Initialize dashboard on page load
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Digital FTE Dashboard initialized');

    // Fetch status immediately
    fetchStatus();

    // Set up auto-refresh every 5 seconds
    updateInterval = setInterval(fetchStatus, 5000);

    // Log when page is closed
    window.addEventListener('beforeunload', function() {
        if (updateInterval) clearInterval(updateInterval);
    });
});
