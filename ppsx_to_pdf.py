from flask import Flask, request, jsonify
import os
import subprocess
import tempfile
import uuid
from waitress import serve

app = Flask(__name__)

@app.route('/convert', methods=['POST'])
def convert():
    # Check if a file was uploaded
    if 'file' not in request.files:
        return jsonify({"message": "PPSX not uploaded."}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"message": "No file selected."}), 400

    try:
        # Generate a unique ID for the PPSX file
        file_id = uuid.uuid4().hex

        # Generate file paths
        ppsx_path = os.path.join(tempfile.gettempdir(), f"{file_id}.ppsx")
        pdf_path = os.path.join(os.getcwd(), f"{file_id}.pdf")

        # Save the uploaded PPSX file
        file.save(ppsx_path)

        # Run LibreOffice command to convert PPSX to PDF
        command = [
            'soffice',
            '--headless',
            '--convert-to', 'pdf',
            '--outdir', os.getcwd(),
            ppsx_path
        ]
        subprocess.run(command)

        # Return the generated PDF path
        return jsonify({"message": "Conversion successful.", "pdf_path": pdf_path}), 200

    except Exception as e:
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500

    finally:
        # Clean up the temporary PPSX file
        try:
            if os.path.exists(ppsx_path):
                os.remove(ppsx_path)
        except Exception as e:
            return jsonify({"message": f"Error in cleanup: {str(e)}"}), 500

if __name__ == '__main__':
    serve(app, host="0.0.0.0", port=8080)
