test_markdown = '''
# Deep Research Report

## Table of Contents
1. **Introduction**
2. **Defining Agentic AI**
    1. **Subsection A**
    2. **Subsection B**
3. **Applications**
    1. **Industry**
    2. **Academia**
4. **Conclusion**

## Introduction
This is the introduction.

## Defining Agentic AI
Content about agentic AI.

### Subsection A
Details for A.

### Subsection B
Details for B.

## Applications
Applications content.

### Industry
Industry details.

### Academia
Academia details.

## Conclusion
Summary and conclusion.
'''

with open('test_report.md', 'w', encoding='utf-8') as f:
    f.write(test_markdown)

from markdown_to_docx import convert_markdown_to_docx

# Read the test markdown file
with open('2_openai/deep_research/research_report_20250618_193430.md', 'r', encoding='utf-8') as f:
    markdown_content = f.read()

print("Converting test markdown to DOCX...")
print("Markdown content preview:")
print(markdown_content[:500] + "...\n")

# Convert to DOCX
docx_file = convert_markdown_to_docx(markdown_content)

print(f"DOCX file generated: {docx_file}")
print("Please open the DOCX file and check the table of contents for proper numbering.") 