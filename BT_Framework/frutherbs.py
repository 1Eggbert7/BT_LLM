# furtherbs.py
# Alexander Leszczynski
# 11-06-2024
from transformers import pipeline

# Load sentiment-analysis pipeline with a specified model
sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

# Load sentiment-analysis pipeline with an alternative model
#sentiment_analyzer = pipeline("sentiment-analysis", model="albert-base-v2")

intent_text = "Yes, but not really"
result = sentiment_analyzer(intent_text)
print(result)
