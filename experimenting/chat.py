from agno.agent import Agent
from agno.models.ollama import Ollama
import pymupdf4llm
import os

FILE_PATH = "src/assets/"

def read_pdf(file_name: str) -> str:
    """
    Always pass the name of the file with .pdf extension.
    Always use this tool to read PDF files and return its content in markdown for analysis.
    use his tool to gain insights from legal documents, contracts, or case studies the user sent.
    """
    caminho_completo = os.path.join(FILE_PATH, file_name)

    if not os.path.exists(caminho_completo):
        erro_msg = f"Erro: O arquivo {file_name} não foi encontrado na pasta {FILE_PATH}."
        return erro_msg
    
    texto = pymupdf4llm.to_markdown(caminho_completo)
        
    return texto

law_agent = Agent(
    model=Ollama(id="qwen3.5:2b", options={
            "num_gpu": 99,        
            "num_ctx": 4096,
            "num_thread": 8,
            "low_vram": False,
            "temperature": 0
        }),
    tools=[read_pdf],
    description="""A legal assistant that can answer questions about the law and provide legal advice.""",
    markdown=True,
    add_history_to_context=True
)

if __name__ == "__main__":
    law_agent.cli_app(stream=True, markdown=True)