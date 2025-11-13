# -*- coding: utf-8 -*-
"""
API Web pour le scraper - Port 8014
Usage: python api_server.py
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
import os
from datetime import datetime
from pathlib import Path
import sys

# Ajouter le chemin du projet
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from add_job import add_job as add_job_func

app = Flask(__name__)
CORS(app)  # Permettre les requêtes cross-origin

# Configuration
API_PORT = 8014
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/health', methods=['GET'])
def health():
    """Endpoint de santé"""
    return jsonify({
        'status': 'ok',
        'service': 'Scraper API',
        'port': API_PORT,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/upload', methods=['POST'])
def upload_csv():
    """Upload un fichier CSV"""
    if 'file' not in request.files:
        return jsonify({'error': 'Aucun fichier fourni'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'Nom de fichier vide'}), 400
    
    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'Le fichier doit être un CSV'}), 400
    
    # Sauvegarder le fichier
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{timestamp}_{file.filename}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    return jsonify({
        'success': True,
        'filename': filename,
        'path': filepath
    })


@app.route('/job', methods=['POST'])
def create_job():
    """Créer un job de scraping"""
    data = request.get_json()
    
    csv_file = data.get('csv_file')
    priority = data.get('priority', 5)
    user = data.get('user', 'API')
    
    if not csv_file:
        return jsonify({'error': 'csv_file requis'}), 400
    
    # Ajouter le job
    try:
        success = add_job_func(csv_file, priority, user)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Job ajouté à la queue',
                'csv_file': csv_file,
                'priority': priority,
                'user': user
            })
        else:
            return jsonify({'error': 'Erreur lors de l\'ajout du job'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/queue', methods=['GET'])
def get_queue_status():
    """Obtenir l'état de la queue"""
    try:
        # Compter les jobs
        pending = len([f for f in os.listdir('queue/pending') if f.endswith('.json')]) if os.path.exists('queue/pending') else 0
        processing = len([f for f in os.listdir('queue/processing') if f.endswith('.json')]) if os.path.exists('queue/processing') else 0
        completed = len([f for f in os.listdir('queue/completed') if f.endswith('.json')]) if os.path.exists('queue/completed') else 0
        
        # Jobs en attente
        pending_jobs = []
        if os.path.exists('queue/pending'):
            for filename in os.listdir('queue/pending'):
                if filename.endswith('.json'):
                    with open(os.path.join('queue/pending', filename), 'r', encoding='utf-8') as f:
                        job = json.load(f)
                        pending_jobs.append({
                            'id': job['id'],
                            'csv_file': Path(job['csv_file']).name,
                            'user': job['user'],
                            'priority': job['priority'],
                            'created_at': job['created_at']
                        })
        
        # Trier par priorité
        pending_jobs.sort(key=lambda j: (j['priority'], j['created_at']))
        
        return jsonify({
            'pending': pending,
            'processing': processing,
            'completed': completed,
            'pending_jobs': pending_jobs
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/results', methods=['GET'])
def list_results():
    """Liste tous les résultats disponibles"""
    try:
        results = []
        
        if os.path.exists('results'):
            for filename in os.listdir('results'):
                if filename.endswith('.json') and filename != '.gitkeep':
                    filepath = os.path.join('results', filename)
                    stats = os.stat(filepath)
                    
                    results.append({
                        'filename': filename,
                        'size': stats.st_size,
                        'created': datetime.fromtimestamp(stats.st_mtime).isoformat()
                    })
        
        # Trier par date (plus récent en premier)
        results.sort(key=lambda r: r['created'], reverse=True)
        
        return jsonify({
            'count': len(results),
            'results': results
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/results/<filename>', methods=['GET'])
def download_result(filename):
    """Télécharger un résultat"""
    try:
        filepath = os.path.join('results', filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'Fichier introuvable'}), 404
        
        return send_file(filepath, as_attachment=True)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/job/upload-and-start', methods=['POST'])
def upload_and_start():
    """Upload CSV et démarre le job immédiatement"""
    if 'file' not in request.files:
        return jsonify({'error': 'Aucun fichier fourni'}), 400
    
    file = request.files['file']
    priority = request.form.get('priority', 5, type=int)
    user = request.form.get('user', 'API')
    
    if file.filename == '' or not file.filename.endswith('.csv'):
        return jsonify({'error': 'Fichier CSV valide requis'}), 400
    
    try:
        # Sauvegarder le fichier
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{file.filename}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Ajouter le job
        success = add_job_func(filepath, priority, user)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'CSV uploadé et job ajouté',
                'filename': filename,
                'priority': priority
            })
        else:
            return jsonify({'error': 'Erreur lors de l\'ajout du job'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print(f"\n{'='*80}")
    print(f"API SCRAPER - DEMARRAGE")
    print(f"{'='*80}")
    print(f"Port: {API_PORT}")
    print(f"Endpoints:")
    print(f"  GET  /health               - Statut de l'API")
    print(f"  POST /upload               - Upload CSV")
    print(f"  POST /job                  - Créer job")
    print(f"  POST /job/upload-and-start - Upload + Démarrer job")
    print(f"  GET  /queue                - État de la queue")
    print(f"  GET  /results              - Liste des résultats")
    print(f"  GET  /results/<filename>   - Télécharger résultat")
    print(f"{'='*80}\n")
    
    app.run(host='0.0.0.0', port=API_PORT, debug=False)

