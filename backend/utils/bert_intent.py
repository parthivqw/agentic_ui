# utils/bert_intent.py

import os
import torch
from transformers import BertTokenizerFast, BertForSequenceClassification

# Load model from correct path
model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'models', 'bert_sales_intent_model'))

tokenizer = BertTokenizerFast.from_pretrained(model_path)
model = BertForSequenceClassification.from_pretrained(model_path)
model.eval()

# Class index to label mapping
label_map = {
    0: 'Enrolled',
    1: 'Ghosted',
    2: 'Information Gathering',
    3: 'Interested',
    4: 'Meeting Scheduled',
    5: 'Not Interested',
    6: 'Price Concern',
    7: 'Wants Demo'
}

def predict_sales_intent(text: str) -> str:
    """Given a conversation string, return the predicted sales intent."""
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    probs = torch.softmax(outputs.logits, dim=1)
    pred_class = torch.argmax(probs, dim=1).item()
    return label_map[pred_class]
