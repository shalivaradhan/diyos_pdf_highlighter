# from flask import Flask, request, send_file, jsonify
# from flask_cors import CORS
# import re
# import fitz  # PyMuPDF
# import io

# app = Flask(__name__)
# CORS(app)

# @app.route("/highlight", methods=["POST"])
# def highlight_text_in_pdf():
#     try:
#         # Check for required inputs
#         if "pdf" not in request.files or "search_text" not in request.form:
#             return jsonify({"error": "Please upload a PDF file and enter a search term."}), 400

#         pdf_file = request.files["pdf"]
#         search_text = request.form["search_text"]
#         search_texts = search_text.split("/")

#         # Get the original filename
#         original_filename = pdf_file.filename

#         # Load the PDF from the uploaded file
#         pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")

#         # Iterate through pages in reverse order for deletion safety
#         for page_num in range(len(pdf_document) - 1, -1, -1):
#             page = pdf_document[page_num]
#             page_text = page.get_text("text")

#             # Split text into sentences
#             sentences = re.split(r'(?<=[.!?])\s+', page_text)

#             # Collect all sentences containing any search term
#             sentences_to_highlight = [
#                 sentence
#                 for sentence in sentences
#                 if any(term.lower() in sentence.lower() for term in search_texts)
#             ]

#             if not sentences_to_highlight:
#                 pdf_document.delete_page(page_num)  # Delete page if no matches
#             else:
#                 # Highlight matching sentences
#                 for sentence in sentences_to_highlight:
#                     sentence_instances = page.search_for(sentence.strip())

#                     if sentence_instances:
#                         for inst in sentence_instances:
#                             highlight = page.add_highlight_annot(inst)
#                             highlight.update()

#         # Save the modified PDF to a new file in memory
#         output_pdf_stream = io.BytesIO()
#         pdf_document.save(output_pdf_stream)
#         pdf_document.close()
#         output_pdf_stream.seek(0)

#         # Send the modified file
#         return send_file(output_pdf_stream, as_attachment=True, download_name=original_filename, mimetype="application/pdf")

#     except Exception as e:
#         print(f"Error: {e}")
#         return jsonify({"error": f"An error occurred: {str(e)}"}), 500


# if __name__ == "__main__":
#     app.run(port=5000)

from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import fitz  # PyMuPDF
import io

app = Flask(__name__)
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

        return send_file(
            output_pdf_stream,
            as_attachment=True,
            download_name=original_filename,
            mimetype="application/pdf",
        )

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(port=5000)
