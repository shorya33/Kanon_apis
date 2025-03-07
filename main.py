from flask import Flask, request, jsonify
from converter import generate_report_with_toc, get_user_inputs
import json
import base64
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure the upload folder exists

@app.route('/submit', methods=['POST'])
def submit_form():
    try:
        # Get JSON data
        form_data = json.loads(request.form.get("form_data", "{}"))
        user_data = get_user_inputs(form_data)

        # Process image if present
        if "logo" in request.files:
            logo_file = request.files["logo"]
            logo_path = os.path.join(UPLOAD_FOLDER, logo_file.filename)
            logo_file.save(logo_path)

            # Convert image to base64
            with open(logo_path, "rb") as img_file:
                user_data["logo_base64"] = base64.b64encode(img_file.read()).decode("utf-8")

        print(json.dumps(user_data, indent=4))

        # Generate PDF
        template_file = "template.html"
        toc_template = "toc_template.html"
        css_file = "style.css"
        output_pdf = "Dynamic_Project_Report.pdf"

        generated_pdf = generate_report_with_toc(user_data, template_file, output_pdf, css_file, toc_template)

        return jsonify({"message": "PDF generated successfully", "pdf_path": generated_pdf})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
