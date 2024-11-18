import os
from flask import Flask, render_template_string, request
from groq import Groq
from pyngrok import ngrok

# Define your ngrok authentication token here
ngrok_auth_token = '1PPhv9GYhJ1odvj2Z3G2boBNOsQ_28K33M2wVmQpC9y5ZLRsT'

# Initialize Groq client
client = Groq(api_key="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")

# Set ngrok authentication token
os.environ["NGROK_AUTH_TOKEN"] = ngrok_auth_token
ngrok.set_auth_token(ngrok_auth_token)

# Start an HTTP tunnel on a specific port (e.g., 5000)
http_tunnel = ngrok.connect(5000)
print(f"Ngrok tunnel \"http://127.0.0.1:5000\" is available at: {http_tunnel.public_url}")

# Initialize Flask app
app = Flask(__name__)

# Initialize conversation history
conversation_history = []

# HTML template embedded directly into the script
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Groq Chat</title>
</head>
<body>
    <h1>Chat with Groq Model</h1>
    <form action="/" method="POST">
        <textarea name="user_input" rows="4" cols="50" placeholder="Enter your message here..."></textarea><br><br>
        <button type="submit">Send</button>
    </form>

    {% if conversation %}
    <h2>Conversation:</h2>
    <ul>
        {% for message in conversation %}
            <li><strong>{{ message.role }}:</strong> {{ message.content }}</li>
        {% endfor %}
    </ul>
    {% endif %}

    {% if response %}
    <h2>Response from Groq:</h2>
    <p>{{ response }}</p>
    {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def chat():
    global conversation_history

    if request.method == "POST":
        user_input = request.form["user_input"]

        # Add the user's input to the conversation history
        conversation_history.append({"role": "user", "content": user_input})

        # Send the conversation history to the Groq API and get a response
        completion = client.chat.completions.create(
            model="llama-3.2-90b-vision-preview",  # Ensure this model is valid for Groq
            messages=conversation_history,  # Pass the full conversation history
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=True,
            stop=None,
        )

        # Initialize the response content
        response = ""

        # Get the response from the model and add it to the response content
        for chunk in completion:
            response += chunk.choices[0].delta.content or ""

        # Add the model's response to the conversation history
        conversation_history.append({"role": "assistant", "content": response})

        return render_template_string(html_template, response=response, conversation=conversation_history)
    return render_template_string(html_template, response=None, conversation=conversation_history)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
