from pathlib import Path
import os
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
import markdown


# Function to get user inputs from form data
def get_user_inputs(form_data):
    inputs = {
        "project_name": form_data.get("project_name", ""),
        "student_name": form_data.get("student_name", ""),
        "guide_name": form_data.get("guide_name", ""),
        "college_name": form_data.get("college_name", ""),
        "college_address": form_data.get("college_address", ""),
        "department_name": form_data.get("department_name", ""),
        "academic_year": form_data.get("academic_year", ""),
        "hod_name": form_data.get("hod_name", ""),  # Standardized variable name
        "principal_name": form_data.get("principal_name", ""),
        "college_logo": form_data.get("college_logo", ""),  # Placeholder for dynamic base64 logo

        "abstract": form_data.get("abstract", ""),
        "tools_list": form_data.get("tools_list", []),
        "introduction": form_data.get("introduction", ""),
        "objectives": form_data.get("objectives", ""),
        "scope": form_data.get("scope", ""),
        "tools": form_data.get("tools", ""),

        # Methodology Section (Handles Sub-Fields)
        "methodology": {
            "development_process": form_data.get("methodology", {}).get("development_process", ""),
            "tools_platforms": form_data.get("methodology", {}).get("tools_platforms", ""),
            "er_diagram": form_data.get("methodology", {}).get("er_diagram", None),
        },

        # Timeline Section (Handles Sub-Fields)
        "timeline": {
            "gantt_chart": form_data.get("timeline", {}).get("gantt_chart", None),
            "milestones": form_data.get("timeline", {}).get("milestones", ""),
        },

        "resources": form_data.get("resources", ""),
        
        # Expected Outcomes (Handles Sub-Fields)
        "expected_outcomes": {
            "functional": form_data.get("expected_outcomes", {}).get("functional", ""),
            "ui": form_data.get("expected_outcomes", {}).get("ui", ""),
            "project_structure": form_data.get("expected_outcomes", {}).get("project_structure", ""),
            "source_code": form_data.get("expected_outcomes", {}).get("source_code", ""),
        },

        "references": form_data.get("references", [])
    }
    return inputs

def generate_report_with_toc(data, main_template_path, output_pdf_path, css_path, toc_template_path):
    """
    Generates a PDF report with a dynamically generated table of contents.

    Args:
        data (dict): Data to be used in the report templates.
        main_template_path (str): Path to the main report template.
        output_pdf_path (str): Path to save the generated PDF.
        css_path (str): Path to the CSS file for styling.
        toc_template_path (str): Path to the table of contents template.
    """
    try:
        # 1. Load Templates and Render Main Report
        template_dir = os.path.dirname(main_template_path)
        env = Environment(loader=FileSystemLoader(template_dir))
        env.filters['markdown'] = markdown.markdown
        main_template = env.get_template(os.path.basename(main_template_path))
        rendered_main_html = main_template.render(data)

        # 2. Load CSS and Render Main Report to PDF
        css = CSS(filename=css_path)
        main_document = HTML(string=rendered_main_html).render(stylesheets=[css], presentational_hints=True)

        # 3. Extract Section Page Numbers
        section_page_map = _extract_section_pages(main_document, data)
        # 4. Render Table of ContentsS
        toc_data = {
            "project_name": data['project_name'],
            "section_pages": section_page_map,
            "tools_list": data["tools_list"]
        }
        print(toc_data)

        toc_template = env.get_template(os.path.basename(toc_template_path))
        rendered_toc_html = toc_template.render(toc_data)
        toc_document = HTML(string=rendered_toc_html).render(stylesheets=[css], presentational_hints=True)

        # 5. Combine Pages and Save PDF
        ordered_pages = _reorder_pages_with_toc(main_document.pages, toc_document.pages[0])
        main_document.copy(ordered_pages).write_pdf(output_pdf_path)

        print(f"✅ Report generated: {output_pdf_path}")

    except Exception as e:
        print(f"❌ Error generating report: {e}")



def _extract_section_pages(document, data):
    """Extracts page numbers for specific sections in the document."""
    tracked_sections = {"introduction", "objectives", "scope", "references", "resources"}
    section_pages = {}
    for page_number, page in enumerate(document.pages, start=1):
        page_text = " ".join(box.text for box in page._page_box.descendants() if hasattr(box, "text"))
        for section in data:
            marker = f"##{section}##"
            if marker in page_text:
                section_pages[section] = page_number + 1
    return section_pages

def _reorder_pages_with_toc(main_pages, toc_page):
    """Reorders pages in the document, inserting the TOC at the 6th position."""
    ordered_pages = list(main_pages) #make a copy to avoid changing the original list.
    ordered_pages.insert(5, toc_page) #insert at the 6th position.
    return ordered_pages