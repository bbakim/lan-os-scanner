# lan_os_scanner
Program that finds OS's of devices on the same LAN
Make sure you have nmap on your computer before running the project.
Download the libraries related to pip install. (pip install python-nmap etc.)
Enter the os_scanner folder to run the project.
Open a terminal with root privileges in Directory. (root privileges required to run nmap)
Run "python lan_os_scanner.py 10.0.2.0/24" in the terminal that opens. (set the IP range here according to your own LAN)
In a few seconds (nmap's runtime) you can view the results at http://127.0.0.1:5000.
You can click the "Download Results" button to download the current results, the results will be downloaded to the downloads folder.
