from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import fitz  # PyMuPDF
import io

app = Flask(name)
CORS(app)

@app.route("/highlight", methods=["POST"])
def highlight_text_in_pdf():
    try:
        if "pdf" not in request.files or "search_text" not in request.form:
            return jsonify({"error": "Please upload a PDF file and enter a search term."}), 400

        pdf_file = request.files["pdf"]
        search_text = request.form["search_text"]

        search_texts =search_text.split("/")
        # Get the original filename of the uploaded file
        original_filename = pdf_file.filename

        # Load the PDF from the uploaded file
        pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")

        for page_num in range(len(pdf_document)-1,-1,-1):
            page = pdf_document[page_num]

            page_text = page.get_text("text")

            # Split text into sentences (basic splitting by '.', '!', or '?')
            sentences = re.split(r'(?<=[.!?])\s+', page_text)

            # Collect all sentences containing any of the search words
            sentences_to_highlight = [
                sentence
                for sentence in sentences
                if any(search_text.lower() in sentence.lower() for search_text in search_texts)
            ]
            
            if not sentences_to_highlight:
                pdf_document.delete_page(page_num)
            else:
                # Highlight the sentences
                for sentence in sentences_to_highlight:
                    sentence_instances = page.search_for(sentence)

                    if sentence_instances:
                        highlights = [page.add_highlight_annot(inst) for inst in sentence_instances]
                        for highlight in highlights:
                            highlight.update()

        # Save highlighted PDF to a new file in memory
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