from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import shutil
import os
import tempfile
import zipfile
import pandas as pd
import openai
from dotenv import load_dotenv
import json
import re

# Load environment variables
load_dotenv()

# Get OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=openai_api_key)

app = FastAPI(title="TDS Solver API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def process_file(file_path):
    """Process file based on file type."""
    file_ext = os.path.splitext(file_path)[1].lower()
    
    # Handle ZIP files
    if file_ext == '.zip':
        extract_dir = tempfile.mkdtemp()
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        # Look for CSV files in the extracted directory
        for root, _, files in os.walk(extract_dir):
            for file in files:
                if file.endswith('.csv'):
                    csv_path = os.path.join(root, file)
                    df = pd.read_csv(csv_path)
                    return df
    
    # Handle CSV files directly
    elif file_ext == '.csv':
        return pd.read_csv(file_path)
    
    # Handle Excel files
    elif file_ext in ['.xlsx', '.xls']:
        return pd.read_excel(file_path)
    
    # Handle text files
    elif file_ext == '.txt':
        with open(file_path, 'r') as f:
            return f.read()
    
    return None

def analyze_question(question):
    """Identify the type of question and determine required processing."""
    # Check for CSV-related questions
    if re.search(r'(csv|CSV|extract.csv)', question):
        return "csv_processing"
    
    # Check for calculation questions
    if re.search(r'(calculate|sum|average|mean|median|compute)', question):
        return "calculation"
    
    # Default to general question
    return "general"

def get_answer_from_llm(question, file_data=None):
    """Get answer from LLM based on question and file data."""
    messages = [{"role": "system", "content": "You are a helpful assistant for the Tools in Data Science course. Answer questions directly and concisely, providing only the exact answer that should be entered in the assignment."}]
    
    if file_data is not None:
        if isinstance(file_data, pd.DataFrame):
            # If dealing with a DataFrame, convert to string representation
            file_content = f"DataFrame Information:\nShape: {file_data.shape}\nColumns: {', '.join(file_data.columns)}\n"
            file_content += "Sample Data:\n" + file_data.head().to_string()
            
            # Check for "answer" column specifically
            if "answer" in file_data.columns:
                file_content += f"\n\nValue in 'answer' column: {file_data['answer'].iloc[0]}"
        else:
            # For text data
            file_content = f"File content:\n{file_data}"
        
        messages.append({"role": "user", "content": f"Question: {question}\n\n{file_content}"})
    else:
        messages.append({"role": "user", "content": f"Question: {question}"})
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.1,
    )
    
    return response.choices[0].message.content.strip()

@app.post("/api/")
async def process_question(
    question: str = Form(...),
    file: UploadFile = File(None)
):
    """Process the question and return the answer."""
    file_data = None
    
    # Process file if provided
    if file:
        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        try:
            # Write the file content to the temporary file
            with open(temp_file.name, "wb") as f:
                shutil.copyfileobj(file.file, f)
            
            # Process the file
            file_data = process_file(temp_file.name)
        finally:
            # Clean up
            os.unlink(temp_file.name)
    
    # Analyze question type
    question_type = analyze_question(question)
    
    # Handle specific question types
    if question_type == "csv_processing" and isinstance(file_data, pd.DataFrame):
        # Check if the question is asking for the value in the "answer" column
        if "answer" in file_data.columns and "answer column" in question.lower():
            answer = str(file_data["answer"].iloc[0])
        else:
            # Use LLM to interpret more complex CSV questions
            answer = get_answer_from_llm(question, file_data)
    else:
        # General questions or other file types
        answer = get_answer_from_llm(question, file_data)
    
    return {"answer": answer}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)