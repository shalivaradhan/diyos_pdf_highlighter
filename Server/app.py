from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import fitz  # PyMuPDF
import io
import re

app = Flask(name)
CORS(app)

@app.route("/highlight", methods=["POST"])
def highlight_text_in_pdf():
    try:
        if "pdf" not in request.files or "search_text" not in request.form:
            return jsonify({"error": "Please upload a PDF file and enter a search term."}), 400

        pdf_file = request.files["pdf"]
        search_text = request.form["search_text"]
        search_texts = search_text.lower().split("/")  # Convert to lowercase for case-insensitive search

        original_filename = pdf_file.filename
        pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")

        # Iterate through pages in reverse order for safe deletion
        for page_num in range(len(pdf_document) - 1, -1, -1):
            page = pdf_document[page_num]
            page_text = page.get_text("text").lower()  # Convert page text to lowercase

            # Track if any term is found on this page
            term_found = False

            for term in search_texts:
                instances = page.search_for(term, quads=False)  # Case-insensitive search
                if instances:
                    term_found = True
                    # Highlight each found instance
                    for inst in instances:
                        highlight = page.add_highlight_annot(inst)
                        highlight.update()

            # Delete the page if no term is found
            if not term_found:
                pdf_document.delete_page(page_num)

        # Save the modified PDF to a new file in memory
        output_pdf_stream = io.BytesIO()
        pdf_document.save(output_pdf_stream)
        pdf_document.close()
        output_pdf_stream.seek(0)

        # Use send_file with the original filename set via download_name
        return send_file(output_pdf_stream, as_attachment=True, attachment_filename=original_filename, mimetype="application/pdf")
    
    except Exception as e:
        print("Error: {}".format(e))
        return jsonify({"error": "An error occurred while processing the PDF file."}), 500

if name == "main":
    app.run(host='0.0.0.0', port=4000)