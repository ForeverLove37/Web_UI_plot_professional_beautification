from flask import Flask, render_template, request, jsonify, send_file
import os
import tempfile
import sys
from pathlib import Path
from werkzeug.utils import secure_filename

# Add the core module to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'core'))
from enhanced_agent import process_python_file, PAPER_FORMATS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
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

@app.route('/process', methods=['POST'])
def process_file():
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Only Python files (.py) are allowed'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Ensure upload directory exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file.save(filepath)
        
        # Get processing options from form
        options = {
            'beautify': request.form.get('beautify') == 'true',
            'academic_options': {
                'enabled': request.form.get('academic_mode') == 'true',
                'paper_format': request.form.get('paper_format', 'nature'),
                'layout': request.form.get('layout', 'single'),
                'vector_format': request.form.get('vector_format'),
                'dpi': int(request.form.get('dpi', 300)),
                'custom_mode': request.form.get('custom_mode') == 'true',
                'custom_params': {}
            }
        }
        
        # Add custom parameters if custom mode is enabled
        if options['academic_options']['custom_mode']:
            custom_params = {}
            if request.form.get('font_size'):
                custom_params['font_size'] = int(request.form.get('font_size'))
            if request.form.get('title_size'):
                custom_params['title_size'] = int(request.form.get('title_size'))
            if request.form.get('fig_width'):
                custom_params['fig_width'] = float(request.form.get('fig_width'))
            if request.form.get('fig_height'):
                custom_params['fig_height'] = float(request.form.get('fig_height'))
            if request.form.get('custom_dpi'):
                custom_params['dpi'] = int(request.form.get('custom_dpi'))
            
            options['academic_options']['custom_params'] = custom_params
        
        # Process the file
        try:
            process_python_file(filepath, **options)
        except Exception as e:
            return jsonify({'error': f'AI processing failed: {str(e)}'}), 500
        
        # Generate output filename
        base, ext = os.path.splitext(filename)
        output_filename = f"{base}_zh_revision{ext}"
        output_filepath = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        
        # Check if output file was created
        if not os.path.exists(output_filepath):
            return jsonify({'error': 'Processing failed - no output file generated. Please check if the input file contains valid matplotlib plotting code.'}), 500
        
        # Return success response with download link
        return jsonify({
            'success': True,
            'message': 'File processed successfully',
            'download_url': f'/download/{output_filename}'
        })
        
    except Exception as e:
        return jsonify({'error': f'Processing error: {str(e)}'}), 500

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