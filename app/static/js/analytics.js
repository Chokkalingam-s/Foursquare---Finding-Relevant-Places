// app/static/js/analytics.js
class Analytics {
    constructor() {
        this.init();
    }

    init() {
        this.trackPageView();
        this.bindAnalyticsEvents();
    }

    trackPageView() {
        this.sendEvent('page_view', {
            page: window.location.pathname,
            timestamp: new Date().toISOString(),
            user_agent: navigator.userAgent
        });
    }

    bindAnalyticsEvents() {
        // Track form interactions
        const locationForm = document.getElementById('location-form');
        if (locationForm) {
            locationForm.addEventListener('submit', () => {
                this.sendEvent('analysis_started', {
                    business_type: document.getElementById('business_type').value,
                    has_demographics: document.querySelectorAll('input[name="demographics"]:checked').length > 0
                });
            });
        }

        // Track feature card clicks
        document.querySelectorAll('.feature-card').forEach(card => {
            card.addEventListener('click', () => {
                this.sendEvent('feature_card_click', {
                    feature: card.querySelector('h3').textContent
                });
            });
        });
    }

    sendEvent(eventType, data) {
        // Send analytics to backend (non-blocking)
        fetch('/api/analytics', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                event_type: eventType,
                data: data
            })
        }).catch(error => {
            // Silently fail analytics - don't interrupt user experience
            console.debug('Analytics error:', error);
        });
    }
}

// Initialize analytics
document.addEventListener('DOMContentLoaded', function() {
    new Analytics();
});