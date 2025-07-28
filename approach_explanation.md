# Approach

## Methodology

The system identifies document structure using layout-based heuristics with `PyMuPDF`. The goal is to extract the title and hierarchical headings without relying on OCR or large models.

### Text Extraction

Each page is parsed using PyMuPDF to extract blocks of text, each containing lines and spans. Every text span is annotated with its font size and position, allowing analysis of the visual hierarchy of the document.

### Heuristic-Based Heading Detection

1. **Font Size Analysis**: The most common font size is inferred as the body text size.
2. **Heading Identification**: Font sizes significantly larger than the body text size are classified as potential headings.
3. **Level Assignment**: The top four unique heading sizes are mapped to `H0`, `H1`, `H2`, and `H3`, with `H0` reserved for the document title.

This approach avoids deep learning, making the process fast and lightweight.

### Heading Merging

To avoid fragmented heading detection:
- Headings at the same level on the same page that are close vertically are merged
- This helps unify headings that span multiple lines or were broken by layout artifacts

### Output Construction

Each processed document results in a JSON with:
- A `title` string composed of all `H0` text
- An `outline` list with heading `level`, `text`, and `page` number

This structure allows easy integration into downstream pipelines.

## Deployment

The system is containerized using a Dockerfile that installs dependencies and executes the parser script. It mounts an `input/` and `output/` volume to work with user-supplied PDFs and write results back to the host.

## Strengths

- Lightweight and fast (CPU-only)
- No need for cloud APIs or internet access
- Handles diverse PDFs with simple heuristics

## Limitations

- Heuristic-based heading detection may not work well on documents with inconsistent formatting
- Does not capture section nesting or inline formatting beyond headings


