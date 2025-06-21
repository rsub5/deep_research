import markdown2
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
import re
from datetime import datetime
import os

def clean_html_text(html_text):
    """Clean HTML text by removing problematic tags and entities"""
    # Remove HTML tags but keep basic formatting
    text = re.sub(r'<[^>]+>', '', html_text)
    # Decode common HTML entities
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&quot;', '"')
    text = text.replace('&#39;', "'")
    return text.strip()

def markdown_to_pdf_elements(markdown_text):
    """Convert markdown text to ReportLab elements"""
    # Convert markdown to HTML first
    html_content = markdown2.markdown(markdown_text, extras=['tables', 'fenced-code-blocks', 'code-friendly'])
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=HexColor('#2c3e50'),
        borderWidth=1,
        borderColor=HexColor('#3498db'),
        borderPadding=10,
        borderRadius=5
    )
    
    heading1_style = ParagraphStyle(
        'CustomHeading1',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=20,
        textColor=HexColor('#2c3e50'),
        borderWidth=0,
        borderPadding=5,
        leftIndent=0
    )
    
    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=15,
        textColor=HexColor('#2c3e50'),
        borderWidth=0,
        borderPadding=5,
        leftIndent=0
    )
    
    heading3_style = ParagraphStyle(
        'CustomHeading3',
        parent=styles['Heading3'],
        fontSize=14,
        spaceAfter=10,
        textColor=HexColor('#2c3e50'),
        borderWidth=0,
        borderPadding=5,
        leftIndent=0
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=12,
        textColor=HexColor('#333333'),
        leftIndent=0
    )
    
    code_style = ParagraphStyle(
        'CustomCode',
        parent=styles['Code'],
        fontSize=9,
        fontName='Courier',
        spaceAfter=12,
        leftIndent=20,
        rightIndent=20,
        backColor=HexColor('#f8f9fa'),
        borderWidth=1,
        borderColor=HexColor('#dee2e6'),
        borderPadding=10,
        borderRadius=3
    )
    
    elements = []
    
    # Process the entire HTML content more comprehensively
    # First, handle code blocks (they need special treatment)
    code_blocks = re.findall(r'<pre><code>(.*?)</code></pre>', html_content, re.DOTALL)
    for code_block in code_blocks:
        clean_code = clean_html_text(code_block)
        if clean_code:
            elements.append(Preformatted(clean_code, code_style))
            elements.append(Spacer(1, 12))
    
    # Remove code blocks from HTML content for further processing
    html_content = re.sub(r'<pre><code>.*?</code></pre>', '', html_content, flags=re.DOTALL)
    
    # Split remaining content into sections
    sections = re.split(r'(<h[1-6]>.*?</h[1-6]>)', html_content, flags=re.DOTALL)
    
    for section in sections:
        section = section.strip()
        if not section:
            continue
            
        # Handle headings
        if section.startswith('<h1>'):
            text = re.search(r'<h1>(.*?)</h1>', section, re.DOTALL)
            if text:
                clean_text = clean_html_text(text.group(1))
                if clean_text:
                    elements.append(Paragraph(clean_text, title_style))
                    elements.append(Spacer(1, 20))
        
        elif section.startswith('<h2>'):
            text = re.search(r'<h2>(.*?)</h2>', section, re.DOTALL)
            if text:
                clean_text = clean_html_text(text.group(1))
                if clean_text:
                    elements.append(Paragraph(clean_text, heading1_style))
                    elements.append(Spacer(1, 15))
        
        elif section.startswith('<h3>'):
            text = re.search(r'<h3>(.*?)</h3>', section, re.DOTALL)
            if text:
                clean_text = clean_html_text(text.group(1))
                if clean_text:
                    elements.append(Paragraph(clean_text, heading2_style))
                    elements.append(Spacer(1, 10))
        
        elif section.startswith('<h4>'):
            text = re.search(r'<h4>(.*?)</h4>', section, re.DOTALL)
            if text:
                clean_text = clean_html_text(text.group(1))
                if clean_text:
                    elements.append(Paragraph(clean_text, heading3_style))
                    elements.append(Spacer(1, 8))
        
        elif section.startswith('<h5>'):
            text = re.search(r'<h5>(.*?)</h5>', section, re.DOTALL)
            if text:
                clean_text = clean_html_text(text.group(1))
                if clean_text:
                    elements.append(Paragraph(clean_text, heading3_style))
                    elements.append(Spacer(1, 8))
        
        elif section.startswith('<h6>'):
            text = re.search(r'<h6>(.*?)</h6>', section, re.DOTALL)
            if text:
                clean_text = clean_html_text(text.group(1))
                if clean_text:
                    elements.append(Paragraph(clean_text, heading3_style))
                    elements.append(Spacer(1, 8))
        
        else:
            # Handle content sections (paragraphs, lists, etc.)
            # Remove any remaining HTML tags and process as text
            clean_text = clean_html_text(section)
            if clean_text:
                # Split into paragraphs and process each
                paragraphs = clean_text.split('\n\n')
                for para in paragraphs:
                    para = para.strip()
                    if para:
                        elements.append(Paragraph(para, normal_style))
                        elements.append(Spacer(1, 8))
    
    return elements

def convert_markdown_to_pdf(markdown_content, output_filename=None):
    """
    Convert markdown content to PDF
    
    Args:
        markdown_content (str): The markdown text to convert
        output_filename (str, optional): Output filename. If None, generates timestamped filename
    
    Returns:
        str: The filename of the created PDF, or None if conversion failed
    """
    if not markdown_content:
        print("Error: No markdown content provided")
        return None
    
    try:
        # Generate filename if not provided
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"research_report_{timestamp}.pdf"
        # Ensure output is in the output folder inside deep_research
        output_dir = os.path.join(os.path.dirname(__file__), 'output')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, output_filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(output_path, pagesize=A4, 
                              rightMargin=72, leftMargin=72, 
                              topMargin=72, bottomMargin=72)
        
        # Convert markdown to PDF elements
        elements = markdown_to_pdf_elements(markdown_content)
        
        # Build PDF
        doc.build(elements)
        
        print(f"PDF created successfully: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"Error creating PDF: {e}")
        return None

def test_conversion():
    """Test function to validate the markdown to PDF conversion"""
    test_markdown = """
# Test Research Report

## Introduction
This is a test report to validate the markdown to PDF conversion functionality.

### Key Points
- Point 1: Testing basic functionality
- Point 2: Testing code blocks
- Point 3: Testing formatting

## Code Example
Here's some example code:

```python
def hello_world():
    print("Hello, World!")
    return "Success"
```

## Blockquote Test
> This is a blockquote to test the formatting.

## Conclusion
This test validates that the PDF conversion is working correctly.
"""
    
    print("Testing markdown to PDF conversion...")
    result = convert_markdown_to_pdf(test_markdown, "test_report.pdf")
    
    if result:
        print("✅ Test passed! PDF created successfully.")
        return True
    else:
        print("❌ Test failed! PDF creation failed.")
        return False

if __name__ == "__main__":
    # Run test when script is executed directly
    test_conversion()
    # pass 