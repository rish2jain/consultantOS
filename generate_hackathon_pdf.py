#!/usr/bin/env python3
"""
Generate Combined PDF for Hackathon Submission

This script combines all hackathon-related markdown files into a single PDF
with diagrams converted to images.
"""

import os
import re
from pathlib import Path
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Preformatted, Image as RLImage, Table, TableStyle
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.lib import colors
from PIL import Image, ImageDraw, ImageFont
import io


class HackathonPDFGenerator:
    """Generate PDF from hackathon markdown files."""

    def __init__(self, output_file="ConsultantOS_Hackathon_Complete.pdf"):
        self.output_file = output_file
        self.doc = SimpleDocTemplate(
            output_file,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18,
        )
        self.story = []
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Set up custom paragraph styles."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Heading 2
        self.styles.add(ParagraphStyle(
            name='CustomH2',
            parent=self.styles['Heading2'],
            fontSize=18,
            textColor=colors.HexColor('#2c5aa0'),
            spaceBefore=20,
            spaceAfter=12,
            fontName='Helvetica-Bold'
        ))

        # Heading 3
        self.styles.add(ParagraphStyle(
            name='CustomH3',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#2c5aa0'),
            spaceBefore=15,
            spaceAfter=10,
            fontName='Helvetica-Bold'
        ))

        # Code block
        self.styles.add(ParagraphStyle(
            name='CodeBlock',
            parent=self.styles['Code'],
            fontSize=9,
            fontName='Courier',
            textColor=colors.HexColor('#333333'),
            backColor=colors.HexColor('#f5f5f5'),
            leftIndent=20,
            rightIndent=20,
            spaceBefore=10,
            spaceAfter=10
        ))

        # Body text
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=11,
            leading=16,
            alignment=TA_JUSTIFY,
            spaceAfter=12
        ))

        # Bullet list
        self.styles.add(ParagraphStyle(
            name='BulletList',
            parent=self.styles['BodyText'],
            fontSize=11,
            leftIndent=30,
            bulletIndent=10,
            spaceAfter=8
        ))

    def _convert_diagram_to_image(self, diagram_text, width=600, height=400):
        """Convert ASCII diagram to image."""
        # Create image with white background
        img = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(img)

        # Try to use a monospace font
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Courier.dfont", 12)
        except:
            font = ImageFont.load_default()

        # Draw the diagram text
        lines = diagram_text.split('\n')
        y_offset = 20
        for line in lines:
            draw.text((20, y_offset), line, fill='black', font=font)
            y_offset += 18

        # Save to BytesIO
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)

        return img_buffer

    def _process_markdown_line(self, line):
        """Process a single markdown line and convert to ReportLab elements."""
        line = line.rstrip()

        # Skip empty lines
        if not line:
            return [Spacer(1, 6)]

        # Headers
        if line.startswith('# '):
            text = line[2:].strip()
            return [Spacer(1, 12), Paragraph(text, self.styles['CustomTitle'])]
        elif line.startswith('## '):
            text = line[3:].strip()
            return [Spacer(1, 12), Paragraph(text, self.styles['CustomH2'])]
        elif line.startswith('### '):
            text = line[4:].strip()
            return [Spacer(1, 10), Paragraph(text, self.styles['CustomH3'])]

        # Bullet points
        if line.startswith('- ') or line.startswith('* '):
            text = '• ' + line[2:].strip()
            return [Paragraph(text, self.styles['BulletList'])]

        # Numbered lists
        if re.match(r'^\d+\. ', line):
            return [Paragraph(line, self.styles['BulletList'])]

        # Horizontal rule
        if line.strip() in ['---', '***', '___']:
            return [Spacer(1, 12)]

        # Bold and emphasis (simple conversion)
        text = line
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
        text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
        text = re.sub(r'`(.+?)`', r'<font name="Courier">\1</font>', text)

        # Regular paragraph
        return [Paragraph(text, self.styles['CustomBody'])]

    def _process_code_block(self, lines):
        """Process a code block."""
        code_text = '\n'.join(lines)
        return [Preformatted(code_text, self.styles['CodeBlock'])]

    def _extract_diagrams(self, content):
        """Extract ASCII diagrams from content."""
        diagrams = []
        lines = content.split('\n')
        in_code_block = False
        current_block = []

        i = 0
        while i < len(lines):
            line = lines[i]

            # Check for code block markers
            if line.strip().startswith('```'):
                if in_code_block:
                    # End of code block - check if it's a diagram
                    block_text = '\n'.join(current_block)
                    if self._is_diagram(block_text):
                        diagrams.append({
                            'start': i - len(current_block) - 1,
                            'end': i,
                            'content': block_text
                        })
                    current_block = []
                    in_code_block = False
                else:
                    # Start of code block
                    in_code_block = True
            elif in_code_block:
                current_block.append(line)

            i += 1

        return diagrams

    def _is_diagram(self, text):
        """Check if text contains diagram-like patterns."""
        diagram_patterns = [
            r'┌.*┐',  # Box drawing characters
            r'│.*│',
            r'└.*┘',
            r'[▼▲►◄→←↓↑]',  # Arrows
            r'[┬┴├┤┼]',  # Box drawing
            r'\+[-─]+\+',  # ASCII boxes
            r'\|.*\|'  # Pipes
        ]

        for pattern in diagram_patterns:
            if re.search(pattern, text):
                return True
        return False

    def process_markdown_file(self, filepath):
        """Process a markdown file and add to PDF."""
        print(f"Processing: {filepath}")

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Add file title
        filename = os.path.basename(filepath)
        self.story.append(PageBreak())
        self.story.append(Spacer(1, 20))
        self.story.append(Paragraph(
            f"<b>{filename}</b>",
            self.styles['CustomTitle']
        ))
        self.story.append(Spacer(1, 20))

        # Process content
        lines = content.split('\n')
        i = 0
        in_code_block = False
        code_block_lines = []

        while i < len(lines):
            line = lines[i]

            # Handle code blocks
            if line.strip().startswith('```'):
                if in_code_block:
                    # End of code block
                    block_text = '\n'.join(code_block_lines)

                    # Check if it's a diagram
                    if self._is_diagram(block_text):
                        # Convert diagram to image
                        try:
                            img_buffer = self._convert_diagram_to_image(block_text)
                            img = RLImage(img_buffer, width=5*inch, height=3*inch)
                            self.story.append(img)
                            self.story.append(Spacer(1, 12))
                        except Exception as e:
                            print(f"Error converting diagram: {e}")
                            # Fallback to code block
                            self.story.extend(self._process_code_block(code_block_lines))
                    else:
                        # Regular code block
                        self.story.extend(self._process_code_block(code_block_lines))

                    code_block_lines = []
                    in_code_block = False
                else:
                    in_code_block = True
            elif in_code_block:
                code_block_lines.append(line)
            else:
                # Regular markdown line
                elements = self._process_markdown_line(line)
                self.story.extend(elements)

            i += 1

    def generate(self, markdown_files):
        """Generate the PDF from markdown files."""
        # Add cover page
        self.story.append(Spacer(1, 2*inch))
        self.story.append(Paragraph(
            "<b>ConsultantOS</b>",
            self.styles['CustomTitle']
        ))
        self.story.append(Spacer(1, 0.3*inch))
        self.story.append(Paragraph(
            "Hackathon Submission - Complete Documentation",
            self.styles['CustomH2']
        ))
        self.story.append(Spacer(1, 0.2*inch))
        self.story.append(Paragraph(
            "Professional-grade strategic analysis in minutes, not days",
            self.styles['CustomBody']
        ))
        self.story.append(Spacer(1, 1*inch))
        self.story.append(Paragraph(
            f"Generated: {Path(self.output_file).stem}",
            self.styles['CustomBody']
        ))

        # Process each markdown file
        for md_file in markdown_files:
            if os.path.exists(md_file):
                self.process_markdown_file(md_file)

        # Build PDF
        print(f"\nGenerating PDF: {self.output_file}")
        self.doc.build(self.story)
        print(f"✅ PDF generated successfully: {self.output_file}")


def main():
    """Main function to generate hackathon PDF."""
    # List of hackathon markdown files in order
    markdown_files = [
        'HACKATHON_SUBMISSION.md',
        'HACKATHON_GUIDE.md',
        'HACKATHON_BONUS_POINTS.md',
        'PITCH.md',
        'PROJECT_STORY.md',
        'VIDEO_SCRIPT.md',
        'DEMO_GUIDE.md',
        'DEMO_QUICKSTART.md',
        'DEMO_READY_CHECKLIST.md',
        'EXECUTIVE_SUMMARY.md',
        'HACKATHON_READY.md',
        'INNOVATION_IMPACT.md'
    ]

    # Get absolute paths
    base_dir = Path(__file__).parent
    md_files = [str(base_dir / f) for f in markdown_files]

    # Generate PDF
    generator = HackathonPDFGenerator("ConsultantOS_Hackathon_Complete.pdf")
    generator.generate(md_files)


if __name__ == '__main__':
    main()
