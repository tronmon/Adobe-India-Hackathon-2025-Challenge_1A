import json
from pathlib import Path

import pymupdf


def get_raw_lines(blocks, clip, tolerance=3):
    """
    Modified from: https://github.com/mckeown12/pymupdf4llm/blob/main/pymupdf4llm/pymupdf4llm/helpers/get_text_lines.py#L30-L153
    """
    y_delta = tolerance

    def sanitize_spans(line):
        line.sort(key=lambda s: s["bbox"].x0)
        for i in range(len(line) - 1, 0, -1):
            s0, s1 = line[i - 1], line[i]
            delta = s1["size"] * 0.1
            if s0["bbox"].x1 + delta < s1["bbox"].x0:
                continue
            if s0["text"] != s1["text"] or s0["bbox"] != s1["bbox"]:
                s0["text"] += s1["text"]
            s0["bbox"] |= s1["bbox"]
            del line[i]
            line[i - 1] = s0
        return line

    spans = []
    for bno, b in enumerate(blocks):
        for lno, line in enumerate(b["lines"]):
            for s in line["spans"]:
                sbbox = pymupdf.Rect(s["bbox"])
                if ((sbbox.tl + sbbox.br) / 2) not in clip:
                    continue
                if s["text"].isspace():
                    continue
                s["bbox"] = sbbox
                s["line"] = lno
                s["block"] = bno
                spans.append(s)

    if not spans:
        return []

    spans.sort(key=lambda s: s["bbox"].y1)
    nlines = []
    line = [spans[0]]
    lrect = spans[0]["bbox"]

    for s in spans[1:]:
        sbbox = s["bbox"]
        prev_bbox = line[-1]["bbox"]
        if (
            abs(sbbox.y1 - prev_bbox.y1) <= y_delta
            or abs(sbbox.y0 - prev_bbox.y0) <= y_delta
        ):
            line.append(s)
            lrect |= sbbox
        else:
            nlines.append([lrect, sanitize_spans(line)])
            line = [s]
            lrect = sbbox

    nlines.append([lrect, sanitize_spans(line)])
    return nlines


class HeaderExtractor:
    """
    Modified from: https://github.com/mckeown12/pymupdf4llm/blob/main/pymupdf4llm/pymupdf4llm/helpers/pymupdf_rag.py#L55-L131
    """

    def __init__(self, doc, pages=None):
        if isinstance(doc, str):
            doc = pymupdf.open(doc)

        self.doc = doc
        self.blocks = []
        self.header_map = self._build_header_map()

    def _build_header_map(self):
        fontsizes = {}
        for page in self.doc:
            blocks = [
                b
                for b in page.get_text("dict")["blocks"]
                if b["type"] == 0 and not pymupdf.Rect(b["bbox"]).is_empty
            ]
            self.blocks.append(blocks)

            for span in [s for b in blocks for l in b["lines"] for s in l["spans"]]:
                size = round(span["size"])
                fontsizes[size] = fontsizes.get(size, 0) + len(span["text"].strip())

        if not fontsizes:
            return {}

        most_common = max(fontsizes.items(), key=lambda x: x[1])[0]
        min_occurrences = 1
        min_size_delta = 1

        header_sizes = [
            size
            for size, count in fontsizes.items()
            if size > most_common + min_size_delta and count >= min_occurrences
        ]
        header_sizes.sort(reverse=True)

        header_map = {}
        for i, size in enumerate(header_sizes[:4]):
            header_map[size] = f"H{i}"

        return header_map

    def get_header_level(self, span):
        return self.header_map.get(round(span["size"]))


def extract_headings(doc_path):
    doc = pymupdf.open(doc_path)
    extractor = HeaderExtractor(doc)
    tolerance = 3

    title = ""

    headings = []
    last_heading = None

    for page_no, page in enumerate(doc):
        lines = get_raw_lines(extractor.blocks[page_no], clip=pymupdf.Rect(page.rect))
        for lrect, spans in lines:
            if not spans:
                continue
            level = extractor.get_header_level(spans[0])
            if level:
                text = " ".join(span["text"] for span in spans)
                if level == "H0":
                    title += text + " "
                else:
                    # Merge with previous if:
                    # - same level
                    # - same page
                    # - close vertical position (optional)
                    if (
                        last_heading is not None
                        and last_heading["level"] == level
                        and last_heading["page"] == page_no
                        and abs(last_heading.get("y1", 0) - lrect.y0) <= tolerance
                    ):
                        last_heading["text"] += " " + text.strip()
                        last_heading["y1"] = lrect.y1
                    else:
                        last_heading = {
                            "level": level,
                            "text": text,
                            "page": page_no,
                            "y1": lrect.y1,
                        }
                        headings.append(last_heading)

    for h in headings:
        h.pop("y1", None)

    return {
        "title": title,
        "outline": headings,
    }


def process_pdfs():
    # Get input and output directories
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")

    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    # Get all PDF files
    pdf_files = list(input_dir.glob("*.pdf"))

    for pdf_file in pdf_files:
        headers = extract_headings(pdf_file)

        # Create output JSON file
        output_file = output_dir / f"{pdf_file.stem}.json"
        with open(output_file, "w") as f:
            json.dump(headers, f, indent=2)

        print(f"Processed {pdf_file.name} -> {output_file.name}")


if __name__ == "__main__":
    print("Starting processing pdfs")
    process_pdfs()
    print("completed processing pdfs")
