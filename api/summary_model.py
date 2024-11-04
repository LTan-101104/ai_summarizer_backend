from transformers import BartForConditionalGeneration, BartTokenizer

model_name = "facebook/bart-large-cnn"
model = BartForConditionalGeneration.from_pretrained(model_name) #create a new instance of model
tokenizer = BartTokenizer.from_pretrained(model_name)

def summarize_text(text, max_length = 150, min_length = 40) -> str:
    print("summarize called")
    inputs = tokenizer.encode("summarize: " + text, return_tensors = "pt", max_length = 1024, truncation=True)
    summary_ids = model.generate(inputs=inputs, max_length = max_length, min_length = min_length, length_penalty = 2.0, num_beams = 4, early_stopping = True) #!what the hell is all of these parameters
    summary = tokenizer.decode(summary_ids[0], skip_skeptical_tokens = True)
    return summary

