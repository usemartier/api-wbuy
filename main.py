from flask import Flask, request, jsonify
import requests
import os
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

WBUY_TOKEN = "Bearer N2Y3ODFjZjgtZmQyMi00NWZkLWFjZjctZjIwOTVkYzBkN2QyOjk4ODg5YWJlOGI5NDQ3YmZhOTkxNzhkZGE2MjJkMGVm"

# Rota de monitoramento
@app.route("/", methods=["GET", "HEAD"])
def health_check():
    return "OK", 200

# Consulta por CPF
@app.route("/consulta-pedido", methods=["POST"])
def consulta_pedido():
    try:
        data = request.json
        cpf = data.get("cpf", "").replace(".", "").replace("-", "").strip()

        if not cpf:
            return jsonify({"erro": "CPF não informado"}), 400

        url = "https://sistema.sistemawbuy.com.br/api/v1/order/"
        headers = {
            "Authorization": WBUY_TOKEN,
            "Content-Type": "application/json"
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            pedidos = response.json().get("data", [])
            pedidos_do_cpf = [
                p for p in pedidos
                if p.get("cliente", {}).get("doc1", "").replace(".", "").replace("-", "") == cpf
            ]

            pedidos_do_cpf.sort(key=lambda x: x.get("data", ""), reverse=True)
            pedidos_do_cpf = pedidos_do_cpf[:2]

            if pedidos_do_cpf:
                return jsonify({
                    "quantidade": len(pedidos_do_cpf),
                    "pedidos": pedidos_do_cpf
                })
            else:
                return jsonify({"mensagem": "Nenhum pedido encontrado para o CPF."}), 404
        else:
            return jsonify({
                "erro": "Erro ao consultar WBuy",
                "status": response.status_code,
                "resposta": response.text
            }), 500

    except Exception as e:
        return jsonify({"erro": "Erro interno", "detalhes": str(e)}), 500

# Consulta por número do pedido
@app.route("/consulta-por-pedido", methods=["POST"])
def consulta_por_pedido():
    try:
        data = request.json
        pedido_id = str(data.get("pedido_id", "")).strip()

        if not pedido_id:
            return jsonify({"erro": "Número do pedido não informado"}), 400

        url = "https://sistema.sistemawbuy.com.br/api/v1/order/"
        headers = {
            "Authorization": WBUY_TOKEN,
            "Content-Type": "application/json"
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            pedidos = response.json().get("data", [])
            pedido = next((p for p in pedidos if str(p.get("id")) == pedido_id), None)

            if pedido:
                return jsonify({
                    "pedidos": [pedido]
                })
            else:
                return jsonify({"mensagem": "Pedido não encontrado"}), 404
        else:
            return jsonify({
                "erro": "Erro ao consultar WBuy",
                "status": response.status_code,
                "resposta": response.text
            }), 500

    except Exception as e:
        return jsonify({"erro": "Erro interno", "detalhes": str(e)}), 500

# Porta obrigatória para funcionar na Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
