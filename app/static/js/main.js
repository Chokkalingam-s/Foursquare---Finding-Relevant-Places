// app/static/js/main.js
class ChoksApp {
    constructor() {
        this.init();
    }

    init() {
        this.bindEvents();
        this.setupFormHandlers();
    }

    bindEvents() {
        // Handle location form submission
        const locationForm = document.getElementById('location-form');
        if (locationForm) {
            locationForm.addEventListener('submit', this.handleLocationAnalysis.bind(this));
        }
    }

    setupFormHandlers() {
        // Add real-time validation
        const locationInput = document.getElementById('location');
        if (locationInput) {
            locationInput.addEventListener('input', this.validateLocation.bind(this));
        }
    }

    async handleLocationAnalysis(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const location = formData.get('location');
        const businessType = formData.get('business_type');
        
        // Get selected demographics
        const demographicsCheckboxes = document.querySelectorAll('input[name="demographics"]:checked');
        const targetDemographics = Array.from(demographicsCheckboxes).map(cb => cb.value);

        if (!location || !businessType) {
            this.showError('Please fill in all required fields');
            return;
        }

        this.showLoading();

        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    location: location,
                    business_type: businessType,
                    target_demographics: targetDemographics
                })
            });

            const result = await response.json();

            if (response.ok && result.success) {
                this.displayResults(result);
            } else {
                this.showError(result.error || 'Analysis failed');
            }
        } catch (error) {
            this.showError('Network error: Please check your connection');
        } finally {
            this.hideLoading();
        }
    }

    validateLocation(event) {
        const value = event.target.value;
        const isValid = value.length > 3;
        
        event.target.style.borderColor = isValid ? 'var(--success-color)' : 'var(--border-color)';
    }

    showLoading() {
        const modal = document.getElementById('loading-modal');
        if (modal) {
            modal.classList.remove('hidden');
        }
    }

    hideLoading() {
        const modal = document.getElementById('loading-modal');
        if (modal) {
            modal.classList.add('hidden');
        }
    }

    displayResults(result) {
        const resultsSection = document.getElementById('results-section');
        const resultsContent = document.getElementById('results-content');
        
        if (!resultsSection || !resultsContent) return;

        const recommendation = result.recommendation;
        const insights = recommendation.insights;

        const html = `
            <div class="recommendation-card">
                <div class="recommendation-header">
                    <h2>Location Analysis Results</h2>
                    <span class="confidence-score ${this.getConfidenceClass(recommendation.confidence_score)}">
                        ${Math.round(recommendation.confidence_score)}% Confidence
                    </span>
                </div>

                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-value">${Math.round(insights.foot_traffic_score)}</div>
                        <div class="metric-label">Foot Traffic Score</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${Math.round(insights.competition_density)}</div>
                        <div class="metric-label">Market Opportunity</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${Math.round(insights.demographic_match)}</div>
                        <div class="metric-label">Demographic Match</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${insights.category_gaps.length}</div>
                        <div class="metric-label">Market Gaps</div>
                    </div>
                </div>

                <div class="analysis-details">
                    <h3>Key Insights</h3>
                    <p class="reasoning">${recommendation.reasoning}</p>

                    <div class="revenue-estimate">
                        <h4><i class="fas fa-dollar-sign"></i> Revenue Potential</h4>
                        <p>${recommendation.estimated_revenue_potential}</p>
                    </div>

                    <div class="optimal-hours">
                        <h4><i class="fas fa-clock"></i> Recommended Hours</h4>
                        <p>${insights.optimal_hours.join(', ')}</p>
                    </div>

                    ${insights.category_gaps.length > 0 ? `
                    <div class="category-gaps">
                        <h4><i class="fas fa-gap"></i> Market Opportunities</h4>
                        <p>Underserved categories: ${insights.category_gaps.join(', ')}</p>
                    </div>
                    ` : ''}

                    ${insights.nearby_attractions.length > 0 ? `
                    <div class="attractions">
                        <h4><i class="fas fa-star"></i> Nearby Attractions</h4>
                        <p>${insights.nearby_attractions.join(', ')}</p>
                    </div>
                    ` : ''}

                    ${insights.risk_factors.length > 0 ? `
                    <div class="risk-factors">
                        <h4><i class="fas fa-exclamation-triangle"></i> Risk Factors</h4>
                        <ul>
                            ${insights.risk_factors.map(risk => `<li>${risk}</li>`).join('')}
                        </ul>
                    </div>
                    ` : ''}

                    <div class="setup-requirements">
                        <h4><i class="fas fa-list-check"></i> Setup Requirements</h4>
                        <ul class="insights-list">
                            ${recommendation.setup_requirements.map(req => `<li>${req}</li>`).join('')}
                        </ul>
                    </div>

                    <div class="duration-recommendation">
                        <h4><i class="fas fa-calendar"></i> Recommended Duration</h4>
                        <p>${recommendation.recommended_duration}</p>
                    </div>
                </div>

                <div class="action-buttons">
                    <button class="btn btn-primary" onclick="choksApp.saveAnalysis('${result.analysis_id}')">
                        <i class="fas fa-save"></i> Save Analysis
                    </button>
                    <button class="btn btn-secondary" onclick="choksApp.newAnalysis()">
                        <i class="fas fa-plus"></i> New Analysis
                    </button>
                </div>
            </div>
        `;

        resultsContent.innerHTML = html;
        resultsSection.classList.remove('hidden');
        
        // Scroll to results
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    getConfidenceClass(score) {
        if (score >= 70) return 'confidence-high';
        if (score >= 50) return 'confidence-medium';
        return 'confidence-low';
    }

    showError(message) {
        const errorHtml = `
            <div class="error-message" style="background: #fef2f2; border: 1px solid #fecaca; color: #dc2626; padding: 1rem; border-radius: 8px; margin: 1rem 0;">
                <i class="fas fa-exclamation-circle"></i> ${message}
            </div>
        `;
        
        const resultsContent = document.getElementById('results-content');
        if (resultsContent) {
            resultsContent.innerHTML = errorHtml;
            document.getElementById('results-section').classList.remove('hidden');
        }
    }

    saveAnalysis(analysisId) {
        // Save analysis ID to browser for later reference
        const savedAnalyses = JSON.parse(localStorage.getItem('savedAnalyses') || '[]');
        savedAnalyses.push({
            id: analysisId,
            timestamp: new Date().toISOString(),
            location: document.getElementById('location').value
        });
        localStorage.setItem('savedAnalyses', JSON.stringify(savedAnalyses));
        
        this.showSuccess('Analysis saved successfully!');
    }

    newAnalysis() {
        // Reset form and hide results
        document.getElementById('location-form').reset();
        document.getElementById('results-section').classList.add('hidden');
        document.getElementById('location').focus();
    }

    showSuccess(message) {
        const successHtml = `
            <div class="success-message" style="background: #f0fdf4; border: 1px solid #bbf7d0; color: #166534; padding: 1rem; border-radius: 8px; margin: 1rem 0;">
                <i class="fas fa-check-circle"></i> ${message}
            </div>
        `;
        
        const resultsContent = document.getElementById('results-content');
        if (resultsContent) {
            resultsContent.innerHTML = successHtml + resultsContent.innerHTML;
        }
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.choksApp = new ChoksApp();
});