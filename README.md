# PDF Heading Extractor

This tool extracts hierarchical headings from PDF documents using font size and layout-based heuristics. It is optimized for use in document understanding tasks such as summarization, search indexing, and metadata extraction.

## Features

- Identifies the title (`H0`) and heading levels (`H1`, `H2`, `H3`) based on font size
- Merges headings that are close in proximity and level
- Outputs structured JSON for each PDF document
- Runs entirely on CPU using PyMuPDF

## Input/Output

- **Input Directory**: `/app/input` — Place your `.pdf` files here
- **Output Directory**: `/app/output` — Extracted JSON files are saved here

### Sample Output
```json
{
  "title": "Document Title",
  "outline": [
    {
      "level": "H1",
      "text": "Introduction",
      "page": 0
    },
    {
      "level": "H2",
      "text": "Motivation",
      "page": 1
    }
  ]
}
```

## Run Instructions (Docker)

A Dockerfile is provided. To build and run the container:

```bash
docker build -t pdf-header-extractor .
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output pdf-header-extractor
```

Ensure the `input/` directory contains PDF files, and the `output/` directory exists or will be created.

## Run Instructions (Local Python)

```bash
pip install pymupdf
python process_pdfs.py
```

## Project Structure

```
.
├── process_pdfs.py     # Main script to process PDFs and extract headings
├── Dockerfile          # Container setup
├── sample_dataset      # sample dataset provided to us
```
