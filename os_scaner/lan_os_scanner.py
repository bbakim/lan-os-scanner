# app.py
import sys
import logging
from flask import Flask, render_template, send_file, make_response
import threading
import time
import nmap
import subprocess
from io import BytesIO

app = Flask(__name__)

# Disable Flask's default logger to prevent INFO level log messages from appearing on the terminal
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Initialize os_info_list before the first request
@app.before_first_request
def before_first_request():
    app.config['os_info_list'] = []
    app.config['result_file'] = None

# Function to update the list of OS information and store it in the application context
def update_os_info(subnet):
    while True:
        app.app_context().push()
        app.config['os_info_list'] = get_os_info_list(subnet)
        # Save the results to a file
        with open('results.txt', 'w') as f:
            for device_ip, os_info in app.config['os_info_list']:
                f.write(f"{device_ip}: {os_info}\n")
        app.config['result_file'] = 'results.txt'
        time.sleep(7)

def get_os_info_list(subnet):
    os_info_list = []
    nm = nmap.PortScanner()

    # Perform host discovery to find active devices on the subnet
    nm.scan(hosts=subnet, arguments='-sn')

    # Loop through all discovered hosts and check if they are up
    for host in nm.all_hosts():
        if nm[host].state() == 'up':
            os_info_list.append(run_nmap_os_detection(host))
        else:
            os_info_list.append((host, "Device is down."))

    return os_info_list

def run_nmap_os_detection(target_ip):
    try:
        # Construct the Nmap command for OS detection
        nmap_cmd = ["nmap", target_ip, "-O"]

        # Run the Nmap command as a subprocess and capture the output
        output = subprocess.check_output(nmap_cmd, universal_newlines=True)

        # Extract the OS information from the output
        os_start = output.find("OS details:") + len("OS details:")
        os_end = output.find("Service detection performed. Please report any incorrect results")
        os_info = output[os_start:os_end].strip()

        return (target_ip, os_info)

    except subprocess.CalledProcessError as e:
        # If the Nmap command returns a non-zero exit code, handle the error
        print(f"Error executing Nmap command: {e}")
        return (target_ip, "Error executing Nmap command.")

msg = ""

# Start the thread to update the list of OS information in the background
update_thread = threading.Thread(target=update_os_info)
update_thread.daemon = True
update_thread.start()

# Route to serve the HTML page
@app.route('/')
def index():
    return render_template('index.html')

# Route to serve the updated list of OS information to the HTML page
@app.route('/os_info')
def os_info():
    return render_template('os_info.html', os_info_list=app.config['os_info_list'])
    
# Route to download the results file
@app.route('/download_results')
def download_results():
    if app.config['result_file']:
        # Read the contents of the results file
        with open(app.config['result_file'], 'r') as f:
            contents = f.read()

        # Create a BytesIO object to serve as an in-memory file
        file_data = BytesIO(contents.encode())

        # Create a response and set the Content-Disposition header
        response = make_response(file_data.getvalue())
        response.headers.set('Content-Disposition', 'attachment', filename='results.txt')
        response.headers.set('Content-Type', 'text/plain')

        return response
    else:
        return "No results file available."


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Please provide a subnet argument in CIDR notation.")
        sys.exit(1)

    subnet_arg = sys.argv[1]
    app.config['os_info_list'] = get_os_info_list(subnet_arg)

    print(" * Running on http://127.0.0.1:5000")
    print(" * Press CTRL+C to quit")

    # Start the background thread to update the list of OS information
    update_thread = threading.Thread(target=update_os_info, args=(subnet_arg,))
    update_thread.daemon = True
    update_thread.start()

    # Start the Flask application
    app.run(debug=True)
