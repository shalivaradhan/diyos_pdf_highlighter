from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import fitz  
import io

app = Flask(__name__)
CORS(app)

@app.route("/highlight", methods=["POST"])
def highlight_text_in_pdf():
    try:
        if "pdf" not in request.files or "search_text" not in request.form:
            return jsonify({"error": "Please upload a PDF file and enter a search term."}), 400

        pdf_file = request.files["pdf"]
        search_string = request.form["search_text"]


        search_texts =search_string.split("/")
        print(search_texts) 

        original_filename = pdf_file.filename

        
        pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")

        for search_text in search_texts:
            for page in pdf_document:
                text_instances = page.search_for(search_text)
                for inst in text_instances:
                    highlight = page.add_highlight_annot(inst)
                    highlight.update()

        
        output_pdf_stream = io.BytesIO()
        pdf_document.save(output_pdf_stream)
        pdf_document.close()
        output_pdf_stream.seek(0)

        return send_file(output_pdf_stream, as_attachment=True, download_name=original_filename, mimetype="application/pdf")
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred while processing the PDF file."}), 500

if __name__ == "__main__":
    app.run(port=5000)
