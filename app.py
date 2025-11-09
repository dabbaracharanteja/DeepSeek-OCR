from flask import Flask, render_template, request, jsonify, send_from_directory
import os
from werkzeug.utils import secure_filename
import torch
from transformers import AutoModel, AutoTokenizer
import traceback
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Global variables for model (lazy loading)
model = None
tokenizer = None
model_loaded = False

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_model():
    """Load the DeepSeek-OCR model"""
    global model, tokenizer, model_loaded
    
    if model_loaded:
        return True
    
    try:
        print("Loading DeepSeek-OCR model...")
        model_name = 'deepseek-ai/DeepSeek-OCR'
        
        # Check if CUDA is available
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"Using device: {device}")
        
        tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        
        if device == 'cuda':
            model = AutoModel.from_pretrained(
                model_name, 
                _attn_implementation='flash_attention_2', 
                trust_remote_code=True, 
                use_safetensors=True
            )
            model = model.eval().cuda().to(torch.bfloat16)
        else:
            # CPU fallback
            model = AutoModel.from_pretrained(
                model_name, 
                trust_remote_code=True, 
                use_safetensors=True
            )
            model = model.eval()
        
        model_loaded = True
        print("Model loaded successfully!")
        return True
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        traceback.print_exc()
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/demo')
def demo():
    return render_template('demo.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/api/model-status')
def model_status():
    """Check if model is loaded"""
    return jsonify({
        'loaded': model_loaded,
        'cuda_available': torch.cuda.is_available(),
        'device': 'cuda' if torch.cuda.is_available() else 'cpu'
    })

@app.route('/api/load-model', methods=['POST'])
def api_load_model():
    """Endpoint to trigger model loading"""
    success = load_model()
    return jsonify({
        'success': success,
        'loaded': model_loaded,
        'message': 'Model loaded successfully!' if success else 'Failed to load model'
    })

@app.route('/api/ocr', methods=['POST'])
def perform_ocr():
    """Perform OCR on uploaded image"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Allowed: PNG, JPG, JPEG, PDF'}), 400
    
    try:
        # Load model if not already loaded
        if not model_loaded:
            success = load_model()
            if not success:
                return jsonify({'error': 'Failed to load OCR model. Please check server logs.'}), 500
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        
        # Get OCR mode from request
        ocr_mode = request.form.get('mode', 'markdown')
        
        # Set prompt based on mode
        if ocr_mode == 'markdown':
            prompt = "<image>\n<|grounding|>Convert the document to markdown."
        elif ocr_mode == 'free':
            prompt = "<image>\nFree OCR."
        elif ocr_mode == 'detailed':
            prompt = "<image>\nDescribe this image in detail."
        else:
            prompt = "<image>\n<|grounding|>OCR this image."
        
        # Prepare output path
        output_dir = os.path.join(app.config['OUTPUT_FOLDER'], timestamp)
        os.makedirs(output_dir, exist_ok=True)
        
        # Perform OCR inference
        print(f"Processing file: {filepath}")
        print(f"Prompt: {prompt}")
        
        result = model.infer(
            tokenizer, 
            prompt=prompt, 
            image_file=filepath, 
            output_path=output_dir,
            base_size=1024, 
            image_size=640, 
            crop_mode=True,
            save_results=True, 
            test_compress=True
        )
        
        return jsonify({
            'success': True,
            'result': result,
            'filename': unique_filename,
            'mode': ocr_mode
        })
    
    except Exception as e:
        print(f"Error during OCR: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': f'OCR processing failed: {str(e)}'}), 500

@app.route('/outputs/<path:filename>')
def download_output(filename):
    """Serve output files"""
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

@app.route('/uploads/<path:filename>')
def download_upload(filename):
    """Serve uploaded files"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    print("=" * 60)
    print("DeepSeek-OCR Web Application")
    print("=" * 60)
    print(f"CUDA Available: {torch.cuda.is_available()}")
    print(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
    print(f"Output folder: {app.config['OUTPUT_FOLDER']}")
    print("=" * 60)
    print("\nStarting Flask server...")
    print("Access the application at: http://localhost:5000")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
