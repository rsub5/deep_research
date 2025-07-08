import markdown
import re

def create_html_documentation():
    # Read the markdown file
    with open('Deep_Research_Assistant_Technical_Documentation.md', 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convert markdown to HTML
    html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code', 'codehilite'])
    
    # Create the full HTML document with styling
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Deep Research Assistant - Technical Documentation</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
            min-height: 100vh;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            text-align: center;
        }}

        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}

        .header p {{
            font-size: 1.2rem;
            opacity: 0.9;
        }}

        .nav {{
            background: #2c3e50;
            padding: 1rem 2rem;
            position: sticky;
            top: 0;
            z-index: 100;
        }}

        .nav ul {{
            list-style: none;
            display: flex;
            flex-wrap: wrap;
            gap: 2rem;
        }}

        .nav a {{
            color: white;
            text-decoration: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            transition: background 0.3s;
        }}

        .nav a:hover {{
            background: #34495e;
        }}

        .content {{
            padding: 2rem;
        }}

        .section {{
            margin-bottom: 3rem;
            padding: 2rem;
            background: #f8f9fa;
            border-radius: 10px;
            border-left: 5px solid #667eea;
        }}

        .section h2 {{
            color: #2c3e50;
            font-size: 2rem;
            margin-bottom: 1rem;
            border-bottom: 2px solid #667eea;
            padding-bottom: 0.5rem;
        }}

        .section h3 {{
            color: #34495e;
            font-size: 1.5rem;
            margin: 1.5rem 0 1rem 0;
        }}

        .section h4 {{
            color: #2c3e50;
            font-size: 1.2rem;
            margin: 1rem 0 0.5rem 0;
        }}

        .code-block {{
            background: #2c3e50;
            color: #ecf0f1;
            padding: 1.5rem;
            border-radius: 8px;
            overflow-x: auto;
            margin: 1rem 0;
            font-family: 'Courier New', monospace;
        }}

        .flow-diagram {{
            background: #ecf0f1;
            border: 2px solid #bdc3c7;
            border-radius: 8px;
            padding: 1.5rem;
            margin: 1rem 0;
            font-family: 'Courier New', monospace;
            white-space: pre-wrap;
        }}

        .architecture-diagram {{
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            padding: 1.5rem;
            border-radius: 8px;
            margin: 1rem 0;
            font-family: 'Courier New', monospace;
            white-space: pre-wrap;
        }}

        .feature-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin: 1rem 0;
        }}

        .feature-card {{
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            border: 1px solid #ddd;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .feature-card h4 {{
            color: #667eea;
            margin-bottom: 0.5rem;
        }}

        .tech-stack {{
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
            margin: 1rem 0;
        }}

        .tech-item {{
            background: #667eea;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.9rem;
        }}

        .file-structure {{
            background: #f1f2f6;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 1.5rem;
            margin: 1rem 0;
            font-family: 'Courier New', monospace;
        }}

        .highlight {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 5px;
            padding: 1rem;
            margin: 1rem 0;
        }}

        .warning {{
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            border-radius: 5px;
            padding: 1rem;
            margin: 1rem 0;
        }}

        .success {{
            background: #d4edda;
            border: 1px solid #c3e6cb;
            border-radius: 5px;
            padding: 1rem;
            margin: 1rem 0;
        }}

        .table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
        }}

        .table th, .table td {{
            border: 1px solid #ddd;
            padding: 0.75rem;
            text-align: left;
        }}

        .table th {{
            background: #667eea;
            color: white;
        }}

        .table tr:nth-child(even) {{
            background: #f8f9fa;
        }}

        .footer {{
            background: #2c3e50;
            color: white;
            text-align: center;
            padding: 2rem;
            margin-top: 3rem;
        }}

        @media (max-width: 768px) {{
            .nav ul {{
                flex-direction: column;
                gap: 1rem;
            }}
            
            .header h1 {{
                font-size: 2rem;
            }}
            
            .content {{
                padding: 1rem;
            }}
            
            .section {{
                padding: 1rem;
            }}
        }}

        .toc {{
            background: #f8f9fa;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 1.5rem;
            margin: 2rem 0;
        }}

        .toc h3 {{
            margin-bottom: 1rem;
            color: #2c3e50;
        }}

        .toc ul {{
            list-style: none;
        }}

        .toc li {{
            margin: 0.5rem 0;
        }}

        .toc a {{
            color: #667eea;
            text-decoration: none;
            padding: 0.25rem 0;
            display: block;
        }}

        .toc a:hover {{
            text-decoration: underline;
        }}

        /* Enhance code blocks */
        pre {{
            background: #2c3e50;
            color: #ecf0f1;
            padding: 1.5rem;
            border-radius: 8px;
            overflow-x: auto;
            margin: 1rem 0;
        }}

        code {{
            background: #f1f2f6;
            padding: 0.2rem 0.4rem;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}

        pre code {{
            background: none;
            padding: 0;
        }}

        /* Enhance lists */
        ul, ol {{
            margin-left: 2rem;
            margin-bottom: 1rem;
        }}

        li {{
            margin-bottom: 0.5rem;
        }}

        /* Enhance links */
        a {{
            color: #667eea;
            text-decoration: none;
        }}

        a:hover {{
            text-decoration: underline;
        }}

        /* Enhance blockquotes */
        blockquote {{
            border-left: 4px solid #667eea;
            padding-left: 1rem;
            margin: 1rem 0;
            font-style: italic;
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 0 5px 5px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔬 Deep Research Assistant</h1>
            <p>Technical Documentation & System Architecture</p>
        </div>

        <nav class="nav">
            <ul>
                <li><a href="#project-overview">Overview</a></li>
                <li><a href="#system-architecture">Architecture</a></li>
                <li><a href="#component-details">Components</a></li>
                <li><a href="#deployment-architecture">Deployment</a></li>
                <li><a href="#security-implementation">Security</a></li>
                <li><a href="#api-integration">API Integration</a></li>
                <li><a href="#user-interface">User Interface</a></li>
                <li><a href="#future-enhancements">Future Plans</a></li>
            </ul>
        </nav>

        <div class="content">
            {html_content}
        </div>

        <div class="footer">
            <p><strong>Document Version:</strong> 1.0</p>
            <p><strong>Last Updated:</strong> December 2024</p>
            <p><strong>Author:</strong> Deep Research Assistant Development Team</p>
        </div>
    </div>
</body>
</html>"""
    
    # Write the HTML file
    with open('Deep_Research_Assistant_Technical_Documentation.html', 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    print("✅ HTML documentation created successfully!")
    print("📄 File: Deep_Research_Assistant_Technical_Documentation.html")

if __name__ == "__main__":
    create_html_documentation() 