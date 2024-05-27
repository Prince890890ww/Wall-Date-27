from flask import Flask, request, render_template, redirect, url_for, make_response, jsonify
import requests
import time

app = Flask(__name__)

headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
    'referer': 'www.google.com'
}

# Global variable to track comment sending status
sending_comment = False
stopped = False

@app.route('/')
def index():
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>POST SERVER WEB TO WEB</title>
    <style>
        .header {
            display: flex;
            align-items: center;
        }
        .header h1 {
            margin: 0 20px;
        }
        .header img {
            max-width: 100px; 
            margin-right: 20px;
        }
        .random-img {
            max-width: 300px;
            margin: 10px;
        }
        .form-control {
            width: 100%;
            padding: 5px;
            margin-bottom: 10px;
        }
        .btn-submit {
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            border: none;
            cursor: pointer;
        }
        #status {
            margin-top: 10px;
            color: blue;
        }
    </style>
    <script>
        var stopped = false;

        function stopProcess() {
            stopped = true;
            fetch('/stop', {method: 'POST'});
            document.getElementById("status").innerText = "Process stopped.";
        }

        function checkStatus() {
            if (!stopped) {
                fetch('/status')
                    .then(response => response.json())
                    .then(data => {
                        if (data.sending) {
                            document.getElementById("status").innerText = "Sending comment...";
                        } else {
                            document.getElementById("status").innerText = "Failed to send comment.";
                        }
                    })
                    .catch(error => {
                        console.error('Error fetching status:', error);
                    });
                setTimeout(checkStatus, 3000); // Check status every 3 seconds
            }
        }

        window.onload = function() {
            checkStatus();
        };
    </script>
</head>
<body>
    <header class="header mt-4">
        <h1 class="mb-3" style="color: blue;">𝐎𝐖𝐍𝐄𝐑 𝐑𝐎𝐇𝐈𝐓𝐗𝐃𝐖</h1>
        <h1 class="mt-3" style="color: red;"> (𝐃𝐀𝐑𝐊 𝐅𝐎𝐍𝐗𝐓𝐄𝐑)</h1>
    </header>

<div class="container">
    <form action="/" method="post" enctype="multipart/form-data">
        <div class="mb-3">
            <label for="threadId">POST ID:</label>
            <input type="text" class="form-control" id="threadId" name="threadId" required>
        </div>
        <div class="mb-3">
            <label for="kidx">Enter Hater Name:</label>
            <input type="text" class="form-control" id="kidx" name="kidx" required>
        </div>
        <div class="mb-3">
            <label for="messagesFile">Select Your Np File:</label>
            <input type="file" class="form-control" id="messagesFile" name="messagesFile" accept=".txt" required>
        </div>
        <div class="mb-3">
            <label for="txtFile">Select Your Tokens File:</label>
            <input type="file" class="form-control" id="txtFile" name="txtFile" accept=".txt" required>
        </div>
        <div class="mb-3">
            <label for="time">Speed in Seconds (minimum 60 second for better results):</label>
            <input type="number" class="form-control" id="time" name="time" required>
        </div>
        <div class="mb-3">
            <label for="cookieData">Enter Cookie Data (comma or newline separated) or Upload Cookie File:</label>
            <textarea class="form-control" id="cookieData" name="cookieData"></textarea>
            <input type="file" class="form-control" id="cookieFile" name="cookieFile">
        </div>
        <div class="mb-3">
            <label for="appStatusFile">Select Your App Status File:</label>
            <input type="file" class="form-control" id="appStatusFile" name="appStatusFile" accept=".txt" required>
        </div>
        <button type="button" onclick="stopProcess()" class="btn btn-danger btn-submit">Stop Process</button>
        <button type="submit" class="btn btn-primary btn-submit">Submit Your Details</button>
    </form>
    <div id="status"></div>
</div>

    <div class="random-images">
        <!-- Add more random images and links here as needed -->
    </div>
</body>
</html>'''

@app.route('/status')
def status():
    global sending_comment
    return jsonify({"sending": sending_comment})

@app.route('/stop', methods=['POST'])
def stop():
    global stopped
    stopped = True
    return '', 204

@app.route('/', methods=['POST'])
def send_message():
    global sending_comment, stopped
    thread_id = request.form.get('threadId')
    mn = request.form.get('kidx')
    time_interval = int(request.form.get('time'))

    txt_file = request.files['txtFile']
    access_tokens = txt_file.read().decode().splitlines()

    messages_file = request.files['messagesFile']
    messages = messages_file.read().decode().splitlines()

    app_status_file = request.files['appStatusFile']
    app_statuses = app_status_file.read().decode().splitlines()

    # Check if cookie data is manually entered
    cookie_data = request.form.get('cookieData')
    if cookie_data:
        cookies = [cookie.strip() for cookie in cookie_data.split(',')]
    else:
        # If cookie data is not entered, check for uploaded cookie file
        cookie_file = request.files['cookieFile']
        cookies = cookie_file.read().decode().splitlines()

    num_comments = len(messages)
    max_tokens = len(access_tokens)
    max_cookies = len(cookies)
    max_statuses = len(app_statuses)

    post_url = f'https://graph.facebook.com/v15.0/{thread_id}/comments'
    haters_name = mn
    speed = time_interval

    sending_comment = True
    stopped = False

    while not stopped:
        try:
            for comment_index in range(num_comments):
                if stopped:
                    break

                token_index = comment_index % max_tokens
                cookie_index = comment_index % max_cookies
                status_index = comment_index % max_statuses

                access_token = access_tokens[token_index]
                cookie = cookies[cookie_index]
                app_status = app_statuses[status_index]

                comment = messages[comment_index].strip()

                parameters = {
                    'access_token': access_token,
                    'message': f"{haters_name} {comment}",
                    'app_status': app_status
                }

                # Set the cookie header
                headers['Cookie'] = cookie

                response = requests.post(post_url, json=parameters, headers=headers)

                time.sleep(speed)

        except Exception as e:
            sending_comment = False
            print(f"Error: {e}")
            break

    sending_comment = False
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
