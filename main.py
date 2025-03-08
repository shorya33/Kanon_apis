from flask import Flask, request, jsonify, send_file
from converter import generate_report_with_toc, get_user_inputs
import json
import base64
import io

app = Flask(__name__)

@app.route('/submit', methods=['POST'])
def submit_form():
    try:
        # Get JSON data directly as a dictionary
        data = request.get_json()

        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400

        # Use the dictionary directly instead of json.loads()
        form_data = data.get("form_data", {})
        user_data = get_user_inputs(form_data)

        # Process Base64 Image if present
        if "logo_base64" in data:
            logo_base64 = data["logo_base64"]
            
            # Decode base64 image
            logo_bytes = base64.b64decode(logo_base64)
            logo_io = io.BytesIO(logo_bytes)

            # Add image bytes to user data
            user_data["logo_bytes"] = logo_io.getvalue()

        print(json.dumps(user_data, indent=4))

        # Generate PDF in memory
        template_file = "template.html"
        toc_template = "toc_template.html"
        css_file = "style.css"

        pdf_io = io.BytesIO()  # Create an in-memory file object
        generate_report_with_toc(user_data, template_file, pdf_io, css_file, toc_template)  # Pass BytesIO

        # Return PDF for download
        pdf_io.seek(0)  # Reset file pointer
        return send_file(pdf_io, as_attachment=True, download_name="Dynamic_Project_Report.pdf", mimetype="application/pdf")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Use Render's PORT if available
    app.run(host="0.0.0.0", port=port)
