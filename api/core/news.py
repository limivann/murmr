
import numpy as np
from transformers import TokenClassificationPipeline, AutoModelForTokenClassification, AutoTokenizer
from transformers.pipelines import AggregationStrategy
import requests
from summarizer import Summarizer
import csv
import urllib.parse

NEWS_API_KEY = ""
NEWS_API_URL = "https://newsapi.org/v2/everything"

# Load BERT Summarization Model
summarizer = Summarizer()

# Load Keyphrase Extraction Model
class KeyphraseExtractionPipeline(TokenClassificationPipeline):
  def __init__(self, model, *args, **kwargs):
    super().__init__(
      model=AutoModelForTokenClassification.from_pretrained(model),
      tokenizer=AutoTokenizer.from_pretrained(model),
      *args,
      **kwargs
    )

  def postprocess(self, all_outputs):
    results = super().postprocess(
      all_outputs=all_outputs,
      aggregation_strategy=AggregationStrategy.SIMPLE,
    )
    return np.unique([result.get("word").strip() for result in results])
    
# Initialize Keyphrase Extractor
model_name = "ml6team/keyphrase-extraction-kbir-inspec"
extractor = KeyphraseExtractionPipeline(model=model_name)

import re
def clean_text(text):
  """
  Removes special characters, numbers, and keeps only readable text.
  """
  text = re.sub(r"[^a-zA-Z\s]", "", text)  # Remove special characters and numbers
  text = re.sub(r"\s+", " ", text).strip()  # Remove extra spaces
  return text


def get_health_news(output_file, country: str = "us", page_size: int = 5):
  
  with open(output_file, mode="a", newline="", encoding="utf-8") as file:
    writer = csv.writer(file, delimiter=",")
    writer.writerow(["Title", "Keywords", "Paraphrased Summary"])  # CSV Headers
    temp = []
    keywords = ["fitness", "nutrition", "aging", "diet", "mindfulness"]
    
    for keyword in keywords:
      encoded_query = urllib.parse.quote(keyword)
    
      params = {
        "q": encoded_query,
        "apiKey": NEWS_API_KEY,
        "pageSize": page_size,
      }
    
      response = requests.get(NEWS_API_URL, params=params)
      data = response.json()
      print("Got news data")
      print(data)
      for article in data["articles"]:
        title = clean_text(article["title"].strip())
        if (article["description"] is None or article["title"] is None):
          continue
        if (article["description"].strip() == ""):
          continue
        if (article["title"].strip() == ""):
          continue
        # keypharses = extractor(article["title"])
        summary = clean_text(summarizer(article["description"]).strip())
        temp.append([title,  summary])
    print(temp)
    writer.writerows(temp)

  print(f"Saved health news to {output_file}")
  
  
  if "articles" in data:
    return {"status": "success", "articles": data["articles"]}
  return {"status": "error", "message": "Failed to fetch news"}


def get_health_news_from_csv(csv_file):
  with open(csv_file, mode="r", encoding="utf-8") as file:
    reader = csv.reader(file, delimiter=",")  
    headers = next(reader)  # Read headers
    data = [row for row in reader]  # Read all rows

  return headers, data