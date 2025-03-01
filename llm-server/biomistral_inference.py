import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

def inference(health_data):
  device = torch.device("cuda:1" if torch.cuda.is_available() else "cpu")

  # Load model directly
  biomistral_tokenizer = AutoTokenizer.from_pretrained("BioMistral/BioMistral-7B-AWQ-QGS128-W4-GEMM")
  biomistral_model = AutoModelForCausalLM.from_pretrained("BioMistral/BioMistral-7B-AWQ-QGS128-W4-GEMM").to(device)

  question = (
      "You are a medical assistant. Based on the health data, detect patterns, identify potential diseases, and suggest preventive measures. \
      Provide a summary of the above in 250 words or fewer. Avoid unnecessary repetition. Here are the health data of a person:\n\n{}".format(health_data)
  )

  input_text = f"Question: {question}\n\nAnswer:"

  # Tokenize input
  inputs = biomistral_tokenizer(input_text, return_tensors="pt").to(device)
      
  # Generate response
  output = biomistral_model.generate(
      **inputs, 
      max_new_tokens=512,  # Ensures only the output is capped, not input + output
      do_sample=True,  
      temperature=0.7,  
      top_p=0.9,  
      repetition_penalty=1.2
  )
  # Decode and print the answer
  biomistral_answer = biomistral_tokenizer.decode(output[0], skip_special_tokens=True)[9:]

  return biomistral_answer