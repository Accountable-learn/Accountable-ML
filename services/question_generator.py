import torch
from langchain.chains.llm import LLMChain
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from langchain.prompts import PromptTemplate


# question_prompt_template = PromptTemplate(
#     input_variables=["topic"],
#     template="You are an English teacher. Generate a simple question for new English learners about the topic: {topic}.\n\nQuestion:"
# )


# Entire model is reloaded everytime some files are changed (Wondering if there is a better approaches)
class QuestionGenerator:
    def __init__(self):
        self.model_path = 'meta-llama/Meta-Llama-3-8B-Instruct'
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # Load the tokenizer and model from local path
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        self.pad_token = self.tokenizer.eos_token  # Set pad_token to eos_token
        self.model = AutoModelForCausalLM.from_pretrained(self.model_path).to(self.device)

    def generate_question(self, topic: str) -> str:
        prompt = f"You are an English teacher. Generate a simple question for new English learners about the topic: {topic}.\n\nQuestion:"

        # Use the pipeline with the loaded model and tokenizer
        pipe = pipeline("text-generation",
                        model=self.model,
                        tokenizer=self.tokenizer,
                        device=0 if self.device == "cuda" else -1)

        # Generate the response
        response = pipe(prompt, max_length=50, truncation=True, pad_token_id=self.pad_token)[0]['generated_text']
        print("Generated Response:", response)
        return response



# Apple Silicon won't work with quantization, maybe try this
# python -m mlx_lm.generate --help
# self.tokenizer = load("mlx-community/Meta-Llama-3–8B-Instruct-4bit")
# self.model = load("mlx-community/Meta-Llama-3–8B-Instruct-4bit")
# response = generate(self.model, self.tokenizer, prompt="Who are you")
# print(response)


# Pipeline
# messages = [
#     {"role": "user", "content": "Do you like baseball"},
# ]
# pipe = pipeline("text-generation", model=self.model_path)
# pipe(messages)

# prompt = question_prompt_template.format(topic=topic)
# inputs = self.tokenizer(prompt, return_tensors="pt", padding=True)
# inputs = inputs.to(self.device)
#
# # Generate output with attention mask and pad token id set
# outputs = self.model.generate(
#     inputs["input_ids"],
#     attention_mask=inputs["attention_mask"],
#     max_length=50,
#     pad_token_id=self.pad_token_id
# )
# question = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
# return question.split("Question:")[-1].strip()