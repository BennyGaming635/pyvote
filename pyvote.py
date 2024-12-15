from flask import Flask, request, jsonify, render_template
import threading
import socket

app = Flask(__name__)

# Poll data structure
polls = {}

@app.route('/')
def index():
    return render_template('index.html', polls=polls)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/create_poll', methods=['POST'])
def create_poll():
    question = request.form.get('question')
    options = request.form.get('options').split(',')

    if not question or not options:
        return jsonify({"error": "Question and options are required."}), 400

    poll_id = len(polls) + 1
    polls[poll_id] = {
        "question": question,
        "options": {option.strip(): 0 for option in options},
        "votes": []
    }
    return render_template('index.html', polls=polls)

@app.route('/get_polls', methods=['GET'])
def get_polls():
    return jsonify(polls)

@app.route('/submit_vote/<int:poll_id>', methods=['POST'])
def submit_vote(poll_id):
    selected_option = request.form.get('option')

    if poll_id in polls and selected_option in polls[poll_id]["options"]:
        # Increment the vote for the selected option
        polls[poll_id]["options"][selected_option] += 1
        return render_template('index.html', polls=polls)
    
    return jsonify({"error": "Invalid poll ID or option."}), 400

@app.route('/results/<int:poll_id>')
def results(poll_id):
    if poll_id in polls:
        return jsonify(polls[poll_id])
    return jsonify({"error": "Poll not found."}), 404

def socket_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 5001))
    server_socket.listen(5)
    while True:
        client_socket, addr = server_socket.accept()
        threading.Thread(target=handle_client, args=(client_socket,)).start()

def handle_client(client_socket):
    client_socket.sendall(b"Welcome to the PyVote App!")
    client_socket.close()

if __name__ == "__main__":
    threading.Thread(target=socket_server, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
