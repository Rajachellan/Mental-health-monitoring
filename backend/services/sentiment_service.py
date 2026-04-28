from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_analyzer = SentimentIntensityAnalyzer()


def analyze_text(text):
    """
    Run VADER sentiment on English text from a call transcript.
    Returns compound in [-1, 1], pos/neg/neu proportions, and a coarse label.
    """
    if not text or not str(text).strip():
        return {
            'compound': 0.0,
            'pos': 0.0,
            'neg': 0.0,
            'neu': 1.0,
            'label': 'neutral',
        }
    scores = _analyzer.polarity_scores(str(text).strip())
    compound = scores['compound']
    if compound >= 0.05:
        label = 'positive'
    elif compound <= -0.05:
        label = 'negative'
    else:
        label = 'neutral'
    return {
        'compound': compound,
        'pos': scores['pos'],
        'neg': scores['neg'],
        'neu': scores['neu'],
        'label': label,
    }


def compound_to_wellbeing_score(compound):
    """Map VADER compound [-1, 1] to a 0–100 wellbeing-style score."""
    return round(max(0.0, min(100.0, (compound + 1.0) * 50.0)), 2)


def score_to_status(score):
    """Align with INDEX.md buckets."""
    if score >= 85:
        return 'good'
    if score >= 65:
        return 'fair'
    if score >= 40:
        return 'poor'
    return 'critical'


def build_summary_and_recommendations(label, compound, score):
    summary = (
        f'Sentiment analysis of the call transcript indicates an overall {label} tone '
        f'(compound={compound:.3f}). Mapped wellbeing score: {score:.1f}/100.'
    )
    rec = []
    if label == 'negative' or score < 65:
        rec.append('Consider a follow-up wellness check or confidential counselling resources.')
    if score < 40:
        rec.append('Priority: connect the employee with HR or a mental health professional.')
    if not rec:
        rec.append('Continue regular check-ins and maintain supportive team culture.')
    return summary, '\n'.join(rec)
