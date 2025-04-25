1. Install dependencies via apt
Run this in your terminal:

bash
Copy
Edit
sudo apt update
sudo apt install default-libmysqlclient-dev build-essential python3-dev
This gives you everything mysqlclient and flask-mysqldb need to compile.

2. Activate your virtual environment (if not already)
bash
Copy
Edit
source venv/bin/activate
3. Now install the Python packages:
bash
Copy
Edit
pip install flask flask-bcrypt flask-cors requests flask-mysqldb
If this runs without errors, you're golden.

🧪 Still Not Working?
Here’s how to isolate and test it step-by-step:

✅ Test 1: Try installing mysqlclient directly
bash
Copy
Edit
pip install mysqlclient
If this fails, post the error here so I can analyze it.

