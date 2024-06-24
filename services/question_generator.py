import torch
from langchain.chains.llm import LLMChain
from transformers import AutoModelForCausalLM, AutoTokenizer
from langchain.prompts import PromptTemplate


question_prompt_template = PromptTemplate(
    input_variables=["topic"],
    template="You are an English teacher. Generate a simple question for new English learners about the topic: {topic}.\n\nQuestion:"
)


# Entire model is reloaded everytime some files are changed (Wondering if there is a better approaches)
class QuestionGenerator:
    def __init__(self):
        self.model_path = './app/models/Meta-Llama-3-8B-Instruct'
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # Load the tokenizer and model from local path
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        self.tokenizer.pad_token = self.tokenizer.eos_token  # Set pad_token to eos_token
        self.model = AutoModelForCausalLM.from_pretrained(self.model_path).to(self.device)
        self.pad_token_id = self.tokenizer.pad_token_id  # Use the eos token as pad token

    def generate_question(self, topic: str) -> str:
        prompt = "You are an English teacher. Generate a simple question for new English learners about the topic: {topic}.\n\nQuestion:"
        # prompt = question_prompt_template.format(topic=topic)
        inputs = self.tokenizer(prompt, return_tensors="pt", padding=True)
        inputs = inputs.to(self.device)

        # Generate output with attention mask and pad token id set
        outputs = self.model.generate(
            inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            max_length=50,
            pad_token_id=self.pad_token_id
        )
        question = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return question.split("Question:")[-1].strip()