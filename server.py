from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
from automation import run_automation
import os

app = Flask(__name__)

# Configuração do CORS para permitir que apenas o seu GitHub Pages acesse este backend
# Pode usar "*" para permitir qualquer origem durante os testes iniciais, mas para produção, restrinja.
origins = [
    "https://miguellimadossantos2704-cmyk.github.io",
    "http://localhost:5173", # Vite default
    "http://localhost:3000"  # React default
]

CORS(app, resources={r"/*": {"origins": origins}})

@app.route('/', methods=['GET'])
def health_check():
    """Rota simples para o Render/Railway saberem que a API está viva."""
    return jsonify({"status": "online", "message": "JobHunter Automation Server is running!"}), 200

@app.route('/start-automation', methods=['POST'])
def start_automation_route():
    try:
        data = request.get_json()
        
        if not data or 'keywords' not in data:
            return jsonify({"error": "Keywords are required"}), 400
            
        keywords = data['keywords']
        
        # Como o Selenium é bloqueante e demorado, executamos a automação numa thread separada
        # Para que a API responda imediatamente ao Frontend dizendo que começou
        thread = threading.Thread(target=run_automation, args=(keywords,))
        thread.start()
        
        return jsonify({
            "status": "success", 
            "message": f"Automation sequence initiated for keywords: {keywords}"
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Usar a porta fornecida pelo ambiente (Render/Railway fornecem a variável PORT)
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
