import re
import PyPDF2
import markdown
from typing import List, Tuple
from app.models.document import Section


class DocumentProcessor:
    """Process and extract text from PDF and Markdown files"""

    @staticmethod
    def extract_text_from_pdf(file_path: str) -> Tuple[str, int]:
        """Extract text from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)

                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n\n"

                return text.strip(), total_pages
        except Exception as e:
            raise Exception(f"Error extracting PDF: {str(e)}")

    @staticmethod
    def extract_text_from_markdown(file_path: str) -> str:
        """Extract text from Markdown file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                md_text = file.read()
                # Keep markdown format for better section detection
                return md_text.strip()
        except Exception as e:
            raise Exception(f"Error reading Markdown: {str(e)}")

    @staticmethod
    def split_into_sections(text: str, is_markdown: bool = False) -> List[Section]:
        """Split text into meaningful sections based on headings"""
        sections = []

        if is_markdown:
            # Parse markdown headings
            lines = text.split('\n')
            current_section = {"title": "Introduction", "content": "", "level": 1, "start": 0}
            current_index = 0

            for i, line in enumerate(lines):
                # Detect markdown headings (# ## ### etc)
                heading_match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())

                if heading_match:
                    # Save previous section
                    if current_section["content"].strip():
                        current_section["end"] = current_index
                        current_section["topics"] = DocumentProcessor.extract_topics(current_section["content"])
                        sections.append(Section(
                            title=current_section["title"],
                            content=current_section["content"].strip(),
                            level=current_section["level"],
                            start_index=current_section["start"],
                            end_index=current_section["end"],
                            topics=current_section["topics"]
                        ))

                    # Start new section
                    level = len(heading_match.group(1))
                    title = heading_match.group(2).strip()
                    current_section = {
                        "title": title,
                        "content": "",
                        "level": level,
                        "start": current_index
                    }
                else:
                    current_section["content"] += line + "\n"
                    current_index += len(line) + 1

            # Add last section
            if current_section["content"].strip():
                current_section["end"] = current_index
                current_section["topics"] = DocumentProcessor.extract_topics(current_section["content"])
                sections.append(Section(
                    title=current_section["title"],
                    content=current_section["content"].strip(),
                    level=current_section["level"],
                    start_index=current_section["start"],
                    end_index=current_section["end"],
                    topics=current_section["topics"]
                ))
        else:
            # For PDFs, use heuristics to detect sections
            # Split by double newlines and capital text patterns
            paragraphs = re.split(r'\n\s*\n', text)
            current_section = {"title": "Introduction", "content": "", "level": 1, "start": 0}
            current_index = 0

            for para in paragraphs:
                para = para.strip()
                if not para:
                    continue

                # Check if paragraph looks like a heading (short, capitalized, no period at end)
                is_heading = (
                    len(para) < 100 and
                    para[0].isupper() and
                    not para.endswith('.') and
                    not para.endswith(',') and
                    '\n' not in para
                )

                if is_heading and len(current_section["content"]) > 100:
                    # Save previous section
                    current_section["end"] = current_index
                    current_section["topics"] = DocumentProcessor.extract_topics(current_section["content"])
                    sections.append(Section(
                        title=current_section["title"],
                        content=current_section["content"].strip(),
                        level=current_section["level"],
                        start_index=current_section["start"],
                        end_index=current_section["end"],
                        topics=current_section["topics"]
                    ))

                    # Start new section
                    current_section = {
                        "title": para,
                        "content": "",
                        "level": 2,
                        "start": current_index
                    }
                else:
                    current_section["content"] += para + "\n\n"

                current_index += len(para) + 2

            # Add last section
            if current_section["content"].strip():
                current_section["end"] = current_index
                current_section["topics"] = DocumentProcessor.extract_topics(current_section["content"])
                sections.append(Section(
                    title=current_section["title"],
                    content=current_section["content"].strip(),
                    level=current_section["level"],
                    start_index=current_section["start"],
                    end_index=current_section["end"],
                    topics=current_section["topics"]
                ))

        return sections

    @staticmethod
    def extract_topics(text: str) -> List[str]:
        """Extract key topics/keywords from text using simple NLP"""
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                      'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
                      'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
                      'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'}

        # Extract potential keywords (capitalized words, technical terms)
        words = re.findall(r'\b[A-Z][a-z]+\b|\b[a-z]+\b', text.lower())

        # Count word frequency
        word_freq = {}
        for word in words:
            if word not in stop_words and len(word) > 3:
                word_freq[word] = word_freq.get(word, 0) + 1

        # Get top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        topics = [word for word, freq in sorted_words[:10]]

        return topics

    @staticmethod
    def count_words(text: str) -> int:
        """Count words in text"""
        words = re.findall(r'\b\w+\b', text)
        return len(words)
