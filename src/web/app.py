from flask import Flask, logging, render_template, request, jsonify, send_file, Response
import json
import os
import tempfile
import sys
from pathlib import Path
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- safe cast assistant function ---
def safe_cast(value, cast_type, default=None):
    """Safely cast a value to the specified type, returning default on failure."""
    if value is None or value == '':
        return default
    try:
        return cast_type(value)
    except (ValueError, TypeError):
        return default
# ----------------------------

# Add the core module to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'core'))
from core.enhanced_agent import process_python_file, process_python_file_streaming, PAPER_FORMATS

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')
app.config['UPLOAD_FOLDER'] = str(Path(__file__).parent.parent.parent / 'uploads' / 'temp')
app.config['OUTPUT_FOLDER'] = str(Path(__file__).parent.parent.parent / 'uploads' / 'outputs')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Allowed file extensions
ALLOWED_EXTENSIONS = {'py'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html', paper_formats=PAPER_FORMATS)

# ... other routes and functions ...

@app.route('/process', methods=['POST'])
def process_file():
    # check the existence of the file
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({"error": "Only Python files (.py) are allowed"}), 400

    # 1. Immediately save the file to a temporary path instead of passing the file stream object
    filename = secure_filename(file.filename)
    # Ensure the upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Extract all processing options from the form
    options = {
        'beautify': request.form.get('beautify') == 'true',
        'academic_options': {
            'enabled': request.form.get('academic_mode') == 'true',
            'paper_format': request.form.get('paper_format', 'nature'),
            'layout': request.form.get('layout', 'single'),
            'vector_format': request.form.get('vector_format'),
            'dpi': safe_cast(request.form.get('dpi'), int, 300),
            'custom_mode': request.form.get('custom_mode') == 'true',
            'custom_params': {}
        }
    }
    if options['academic_options']['custom_mode']:
        custom_params = {
            'font_size': safe_cast(request.form.get('font_size'), int, None),
            'title_size': safe_cast(request.form.get('title_size'), int, None),
            'fig_width': safe_cast(request.form.get('fig_width'), float, None),
            'fig_height': safe_cast(request.form.get('fig_height'), float, None),
            'dpi': safe_cast(request.form.get('custom_dpi'), int, None)
        }
        options['academic_options']['custom_params'] = {k: v for k, v in custom_params.items() if v is not None}

    # ------------------ Definition of output filepath and the generator ------------------
    # Note that generate now takes filepath (string path) instead of file_storage (file object)
    def generate(saved_filepath, opts):
        try:
            # 2. The generator now directly uses the saved file path for processing
            output_folder = app.config['OUTPUT_FOLDER']
            for status in process_python_file_streaming(saved_filepath, output_folder, **opts):
                if status.startswith("SUCCESS:"):
                    output_filename = status.split(":", 1)[1].strip()
                    success_data = {"success": True, "message": "处理完成", "download_url": f"/download/{output_filename}"}
                    yield f'data: {json.dumps(success_data, ensure_ascii=False)}\n\n'
                else:
                    status_data = {"status": status}
                    yield f'data: {json.dumps(status_data, ensure_ascii=False)}\n\n'
            
        except Exception as e:
            # 3. Ensure that the standard logging module is used here
            logging.error(f"An error occurred during streaming: {e}", exc_info=True)
            error_data = {"error": f"An unexpected error occurred in the stream: {str(e)}"}
            yield f'data: {json.dumps(error_data)}\n\n'

    # ------------------ Start the generator and return streaming response ------------------
    # Pass the saved file path and options as arguments to generate
    return Response(generate(filepath, options), mimetype='text/event-stream')

@app.route('/download/<filename>')
def download_file(filename):
    try:
        filepath = os.path.join(app.config['OUTPUT_FOLDER'], secure_filename(filename))
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(filepath, as_attachment=True, download_name=filename)
    except Exception as e:
        return jsonify({'error': f'Download error: {str(e)}'}), 500

@app.route('/api/paper_formats')
def get_paper_formats():
    return jsonify(PAPER_FORMATS)

if __name__ == '__main__':
    # Ensure directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)