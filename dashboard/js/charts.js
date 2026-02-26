// FTE Performance Charts Visualization
// Uses Chart.js for real-time performance metrics

let gmailChart, whatsappChart, calendarChart;

function initializeCharts() {
    const chartConfig = {
        type: 'doughnut',
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        font: { size: 11 },
                        padding: 15,
                        color: '#9CA3AF'
                    }
                }
            }
        }
    };

    // Gmail FTE Chart
    const gmailCtx = document.getElementById('gmail-chart');
    if (gmailCtx) {
        gmailChart = new Chart(gmailCtx, {
            ...chartConfig,
            data: {
                labels: ['Auto-Draft', 'Manual Review', 'Escalated'],
                datasets: [{
                    data: [73, 22, 5],
                    backgroundColor: [
                        'rgba(59, 130, 246, 0.8)',
                        'rgba(247, 144, 9, 0.8)',
                        'rgba(239, 68, 68, 0.8)'
                    ],
                    borderColor: ['#1E3A8A', '#92400E', '#7F1D1D'],
                    borderWidth: 2
                }]
            }
        });
    }

    // WhatsApp FTE Chart
    const whatsappCtx = document.getElementById('whatsapp-chart');
    if (whatsappCtx) {
        whatsappChart = new Chart(whatsappCtx, {
            ...chartConfig,
            data: {
                labels: ['Acknowledged', 'Escalated', 'Pending'],
                datasets: [{
                    data: [85, 10, 5],
                    backgroundColor: [
                        'rgba(34, 197, 94, 0.8)',
                        'rgba(239, 68, 68, 0.8)',
                        'rgba(107, 114, 128, 0.8)'
                    ],
                    borderColor: ['#15803D', '#7F1D1D', '#374151'],
                    borderWidth: 2
                }]
            }
        });
    }

    // Calendar FTE Chart
    const calendarCtx = document.getElementById('calendar-chart');
    if (calendarCtx) {
        calendarChart = new Chart(calendarCtx, {
            ...chartConfig,
            data: {
                labels: ['Scheduled', 'Conflicts', 'Briefings'],
                datasets: [{
                    data: [88, 8, 4],
                    backgroundColor: [
                        'rgba(139, 92, 246, 0.8)',
                        'rgba(239, 68, 68, 0.8)',
                        'rgba(34, 197, 94, 0.8)'
                    ],
                    borderColor: ['#5B21B6', '#7F1D1D', '#15803D'],
                    borderWidth: 2
                }]
            }
        });
    }
}

// Initialize charts when document loads
document.addEventListener('DOMContentLoaded', initializeCharts);

// Update charts with real data
function updateCharts(data) {
    if (gmailChart && data.fte_metrics?.gmail) {
        const gmail = data.fte_metrics.gmail;
        gmailChart.data.datasets[0].data = [
            Math.round(gmail.auto_draft_rate * 100),
            Math.round((1 - gmail.auto_draft_rate) * 100 * 0.8),
            Math.round((1 - gmail.auto_draft_rate) * 100 * 0.2)
        ];
        gmailChart.update();
    }

    if (whatsappChart && data.fte_metrics?.whatsapp) {
        const wa = data.fte_metrics.whatsapp;
        whatsappChart.data.datasets[0].data = [
            Math.round((1 - wa.escalation_rate) * 100),
            Math.round(wa.escalation_rate * 100),
            5
        ];
        whatsappChart.update();
    }

    if (calendarChart && data.fte_metrics?.calendar) {
        const cal = data.fte_metrics.calendar;
        calendarChart.data.datasets[0].data = [
            Math.round((cal.events_processed - cal.conflicts_resolved) / cal.events_processed * 100),
            cal.conflicts_resolved,
            cal.briefings_generated
        ];
        calendarChart.update();
    }
}
