from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain_experimental.utilities import PythonREPL
from langchain_core.tools import tool
import json
import PyPDF2
from fpdf import FPDF
import uuid
import os

@tool
def calculator(expression: str) -> str:
    """Calculate the result of a mathematical expression."""
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def web_search(query: str) -> str:
    """Search the web for information using DuckDuckGo. Returns a JSON string with results."""
    try:
        wrapper = DuckDuckGoSearchAPIWrapper(max_results=5)
        results = wrapper.results(query, max_results=5)
        return json.dumps(results)
    except Exception as e:
        return json.dumps([{"error": str(e)}])

@tool
def code_executor(code: str) -> str:
    """Execute Python code and return the output. Use this for complex calculations or data processing."""
    try:
        repl = PythonREPL()
        return repl.run(code)
    except Exception as e:
        return f"Execution failed: {str(e)}"

@tool
def pdf_summarizer(file_path: str) -> str:
    """Extract text from a PDF file for summarization. The input should be the internal file path of the uploaded PDF."""
    try:
        text = ""
        with open(file_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
        
        # Limit text size to avoid token overflow, the LLM will summarize it
        return text[:10000] if len(text) > 10000 else text
    except Exception as e:
        return f"Failed to read PDF: {str(e)}"

@tool
def pdf_generator(content: str, filename: str) -> str:
    """Generate a PDF file with the given content. Returns the URL to the generated PDF. filename should not have spaces."""
    try:
        if not filename.endswith(".pdf"):
            filename += ".pdf"
        
        # Avoid spaces and special chars in filename
        clean_filename = "".join(c for c in filename if c.isalnum() or c in "._-")
        unique_filename = f"{uuid.uuid4()}_{clean_filename}"
        file_path = os.path.join("uploads", unique_filename)
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # Handle multi-line content
        for line in content.split("\n"):
            pdf.cell(200, 10, txt=line, ln=True)
            
        pdf.output(file_path)
        
        # Return the relative URL as seen by the frontend
        # The frontend knows the backend base URL
        return f"/uploads/{unique_filename}"
    except Exception as e:
        return f"Failed to generate PDF: {str(e)}"

def get_tools_for_agent(tools_config: list) -> list:
    tools = []
    if "calculator" in tools_config:
        tools.append(calculator)
    if "web_search" in tools_config:
        tools.append(web_search)
    if "code_executor" in tools_config:
        tools.append(code_executor)
    if "pdf_summarizer" in tools_config:
        tools.append(pdf_summarizer)
    if "pdf_generator" in tools_config:
        tools.append(pdf_generator)
    return tools
