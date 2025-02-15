from transformers import pipeline

# Load summarization model
summarizer = pipeline('summarization', model='facebook/bart-large-cnn')

def generate_summary(text, max_length=150):
    # Limit text length for the model
    text = text[:1024]  
    summary = summarizer(text, max_length=max_length, min_length=50, do_sample=False)
    return summary[0]['summary_text']
