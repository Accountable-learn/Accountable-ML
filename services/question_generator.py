import torch
from langchain.chains.llm import LLMChain
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline, BitsAndBytesConfig
from langchain.prompts import PromptTemplate


# Entire model is reloaded everytime some files are changed (Wondering if there is a better approaches)


class QuestionGenerator:
    def __init__(self):
        self.model_id = 'meta-llama/Meta-Llama-3-8B-Instruct'
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # Load the tokenizer and model from local path
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        self.pad_token = self.tokenizer.eos_token  # Set pad_token to eos_token

        self.bnb_config  = BitsAndBytesConfig(
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

        # TODO: Use PromptTemplate to give some examples
        self.prompt_template = PromptTemplate(
            input_variables=["topic"],
            template=(
                "You are an English teacher. Generate 10 open-ended questions for new English learners about the topic: {topic}.\n\n"
                "Don't include the answers, only generate the questions. \n\n"
                "Questions:\n"
                "1. "
            )
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
        response = generator(prompt)[0]['generated_text']
        questions = self.extract_questions(response)
        print("Response:", response)
        return questions

# Apple Silicon doesn't work with quantization, maybe try this
# python -m mlx_lm.generate --help
# self.tokenizer = load("mlx-community/Meta-Llama-3–8B-Instruct-4bit")
# self.model = load("mlx-community/Meta-Llama-3–8B-Instruct-4bit")
# response = generate(self.model, self.tokenizer, prompt="Who are you")
# print(response)
