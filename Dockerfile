FROM --platform=linux/amd64 python:3.10

# Set working directory
WORKDIR /app

# Copy all files
COPY . .

# Use the venv Python to run the script
RUN pip install .

CMD ["python", "process_pdfs.py"]
