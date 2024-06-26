import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline, BitsAndBytesConfig
from langchain_core.prompts import PromptTemplate


class QuestionGenerator:
    def __init__(self):
        self.model_id = 'meta-llama/Meta-Llama-3-8B-Instruct'
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # Load the tokenizer and model from local path
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        self.pad_token = self.tokenizer.eos_token  # Set pad_token to eos_token

        # TODO: IT is probably not Llama's issues creating unreliable output. Running in Ollama is fine
        self.bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            device_map="auto",
            quantization_config=self.bnb_config
        )

        self.prompt_template = PromptTemplate.from_template(
            """
You are an English teacher having a conversation with a student. Ask 10 questions about {topic}.
Your format should be:
Questions:
1. ...
2. ...
            """
        )

    def extract_questions(self, text: str) -> str:
        lines = text.split('\n')
        questions = [line.strip() for line in lines if line.strip().endswith('?')]
        return '\n'.join(questions)

    def generate_question(self, topic: str) -> str:
        prompt = self.prompt_template.format(topic=topic)

        # Use the pipeline with the loaded model and tokenizer
        generator = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer
        )

        # Generate the response
        response = generator(prompt, max_new_tokens=1000)[0]['generated_text']
        questions = self.extract_questions(response)
        print(questions)
        return questions
