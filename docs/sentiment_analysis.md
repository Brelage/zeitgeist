There are several approaches to calculate sentiment scores, from simple to sophisticated. Here are the main methods:

## 1. TextBlob (Simplest - Good Starting Point)

```python
from textblob import TextBlob

def calculate_sentiment_textblob(text):
    """Returns polarity (-1 to 1) and subjectivity (0 to 1)"""
    blob = TextBlob(text)
    return {
        'polarity': blob.sentiment.polarity,      # -1 (negative) to 1 (positive)
        'subjectivity': blob.sentiment.subjectivity  # 0 (objective) to 1 (subjective)
    }

# Example
text = "Die neue Politik ist wirklich enttäuschend und schlecht durchdacht."
sentiment = calculate_sentiment_textblob(text)
print(sentiment)  # {'polarity': -0.5, 'subjectivity': 0.8}
```

**Pros**: Easy to use, works out of the box
**Cons**: English-focused, may not work well with German

## 2. VADER (Good for Social Media/News)

```python
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def calculate_sentiment_vader(text):
    """VADER sentiment analysis"""
    analyzer = SentimentIntensityAnalyzer()
    scores = analyzer.polarity_scores(text)
    return {
        'compound': scores['compound'],  # Overall score (-1 to 1)
        'positive': scores['pos'],
        'neutral': scores['neu'], 
        'negative': scores['neg']
    }

# Example
text = "This policy is absolutely terrible and disappointing!"
sentiment = calculate_sentiment_vader(text)
print(sentiment)  # {'compound': -0.8, 'positive': 0.0, 'neutral': 0.3, 'negative': 0.7}
```

**Pros**: Handles intensifiers ("very bad" vs "bad"), punctuation, capitalization
**Cons**: Also English-focused

## 3. Transformers (Most Accurate - Recommended)

```python
from transformers import pipeline

# For German text (recommended for your use case)
def setup_german_sentiment():
    """Setup German sentiment analysis pipeline"""
    return pipeline(
        "sentiment-analysis",
        model="oliverguhr/german-sentiment-bert",
        return_all_scores=True
    )

def calculate_sentiment_transformers(text, classifier):
    """Calculate sentiment using German BERT model"""
    results = classifier(text)[0]  # Get first result
    
    # Convert to standardized format
    sentiment_map = {'POSITIVE': 1, 'NEGATIVE': -1, 'NEUTRAL': 0}
    
    scores = {}
    for result in results:
        label = result['label']
        score = result['score']
        scores[label.lower()] = score
    
    # Calculate compound score
    compound = (scores.get('positive', 0) * 1 + 
                scores.get('negative', 0) * -1 + 
                scores.get('neutral', 0) * 0)
    
    return {
        'compound': compound,
        'positive': scores.get('positive', 0),
        'negative': scores.get('negative', 0),
        'neutral': scores.get('neutral', 0)
    }

# Usage
classifier = setup_german_sentiment()
text = "Diese Politik ist wirklich enttäuschend und schlecht durchdacht."
sentiment = calculate_sentiment_transformers(text, classifier)
```

## 4. Complete Sentiment Analysis System

```python
import json
from datetime import datetime

class SentimentAnalyzer:
    def __init__(self, method='transformers'):
        self.method = method
        
        if method == 'transformers':
            self.classifier = pipeline(
                "sentiment-analysis",
                model="oliverguhr/german-sentiment-bert",
                return_all_scores=True
            )
    
    def analyze_article(self, article):
        """Add sentiment scores to article"""
        text = f"{article['title']} {article['content']}"
        
        if self.method == 'transformers':
            sentiment = self.calculate_transformers_sentiment(text)
        elif self.method == 'textblob':
            sentiment = self.calculate_textblob_sentiment(text)
        else:
            sentiment = {'compound': 0, 'positive': 0, 'negative': 0, 'neutral': 1}
        
        # Add sentiment to article
        article['sentiment'] = sentiment
        article['sentiment_analyzed_date'] = datetime.now().isoformat()
        
        return article
    
    def calculate_transformers_sentiment(self, text):
        """German BERT sentiment analysis"""
        # Truncate text if too long (BERT has token limits)
        if len(text) > 512:
            text = text[:512]
        
        results = self.classifier(text)[0]
        
        scores = {}
        for result in results:
            scores[result['label'].lower()] = result['score']
        
        # Calculate compound score
        compound = (scores.get('positive', 0) - scores.get('negative', 0))
        
        return {
            'compound': round(compound, 3),
            'positive': round(scores.get('positive', 0), 3),
            'negative': round(scores.get('negative', 0), 3),
            'neutral': round(scores.get('neutral', 0), 3)
        }
    
    def process_jsonl_file(self, input_file, output_file):
        """Process entire JSONL file and add sentiment scores"""
        with open(input_file, 'r', encoding='utf-8') as infile, \
             open(output_file, 'w', encoding='utf-8') as outfile:
            
            for line_num, line in enumerate(infile, 1):
                try:
                    article = json.loads(line)
                    article_with_sentiment = self.analyze_article(article)
                    outfile.write(json.dumps(article_with_sentiment, ensure_ascii=False) + '\n')
                    
                    if line_num % 100 == 0:
                        print(f"Processed {line_num} articles...")
                        
                except Exception as e:
                    print(f"Error processing line {line_num}: {e}")

# Usage
analyzer = SentimentAnalyzer(method='transformers')

# Process your entire dataset
analyzer.process_jsonl_file('news_dataset.jsonl', 'news_with_sentiment.jsonl')

# Or analyze single articles
article = {
    "title": "Neue Steuerreform sorgt für Kontroversen",
    "content": "Die geplante Steuerreform stößt auf heftige Kritik..."
}
article_with_sentiment = analyzer.analyze_article(article)
print(article_with_sentiment['sentiment'])
```

## 5. Batch Processing for Performance

```python
def batch_sentiment_analysis(articles, batch_size=32):
    """Process articles in batches for better performance"""
    classifier = pipeline(
        "sentiment-analysis",
        model="oliverguhr/german-sentiment-bert",
        return_all_scores=True
    )
    
    results = []
    
    for i in range(0, len(articles), batch_size):
        batch = articles[i:i + batch_size]
        texts = [f"{a['title']} {a['content'][:500]}" for a in batch]  # Limit length
        
        # Process batch
        batch_results = classifier(texts)
        
        # Add results to articles
        for article, sentiment_result in zip(batch, batch_results):
            article['sentiment'] = process_sentiment_result(sentiment_result)
            results.append(article)
    
    return results
```

## Recommendation for Your German News

**Use the Transformers approach** with the German BERT model (`oliverguhr/german-sentiment-bert`). It's specifically trained on German text and will give you much more accurate results than English-focused tools.

**Installation:**
```bash
pip install transformers torch
```

This will give you sentiment scores that you can use for temporal analysis, source comparison, and topic-based sentiment tracking in your German news dataset.