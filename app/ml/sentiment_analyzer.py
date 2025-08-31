# app/ml/sentiment_analyzer.py
import nltk
from textblob import TextBlob
from typing import List, Dict, Tuple
import re

class SentimentAnalyzer:
    def __init__(self):
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)
        
        try:
            nltk.data.find('corpora/vader_lexicon')
        except LookupError:
            nltk.download('vader_lexicon', quiet=True)
    
    def analyze_tips_sentiment(self, tips: List[Dict]) -> Dict:
        """Analyze sentiment of place tips/reviews"""
        if not tips:
            return {'sentiment_score': 0.5, 'insights': []}
        
        sentiments = []
        positive_keywords = []
        negative_keywords = []
        
        for tip in tips:
            text = tip.get('text', '')
            if text:
                blob = TextBlob(text)
                sentiment = blob.sentiment.polarity
                sentiments.append(sentiment)
                
                # Extract keywords
                if sentiment > 0.1:
                    positive_keywords.extend(self._extract_keywords(text))
                elif sentiment < -0.1:
                    negative_keywords.extend(self._extract_keywords(text))
        
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
        
        # Normalize to 0-1 scale
        sentiment_score = (avg_sentiment + 1) / 2
        
        # Generate insights
        insights = self._generate_sentiment_insights(
            sentiment_score, positive_keywords, negative_keywords
        )
        
        return {
            'sentiment_score': sentiment_score,
            'total_tips': len(tips),
            'insights': insights,
            'positive_keywords': list(set(positive_keywords)),
            'negative_keywords': list(set(negative_keywords))
        }
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from text"""
        # Simple keyword extraction
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filter out common words
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'was', 'are', 'were', 'a', 'an'}
        keywords = [word for word in words if len(word) > 3 and word not in stop_words]
        
        return keywords[:5]  # Return top 5 keywords
    
    def _generate_sentiment_insights(self, sentiment_score: float, 
                                   positive_keywords: List[str], 
                                   negative_keywords: List[str]) -> List[str]:
        """Generate insights from sentiment analysis"""
        insights = []
        
        if sentiment_score > 0.7:
            insights.append("Very positive customer sentiment in the area")
        elif sentiment_score > 0.5:
            insights.append("Generally positive customer sentiment")
        elif sentiment_score < 0.3:
            insights.append("Some negative sentiment - investigate common complaints")
        
        if positive_keywords:
            common_positive = [word for word in positive_keywords if positive_keywords.count(word) > 1]
            if common_positive:
                insights.append(f"Customers appreciate: {', '.join(common_positive[:3])}")
        
        if negative_keywords:
            common_negative = [word for word in negative_keywords if negative_keywords.count(word) > 1]
            if common_negative:
                insights.append(f"Common concerns: {', '.join(common_negative[:3])}")
        
        return insights