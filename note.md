Next steps:
  1. Activate virtual environment:
       .venv\Scripts\activate

  2. Install dependencies:
       pip install -e .

  3. Open TWO terminal windows:

     Terminal 1 (Service):
       python src/service.py

     Terminal 2 (Schedule Agent):
       python src/schedule.py

  4. View UI in browser:
       http://localhost:5233

Tip: Run 'python dev_check.py' to verify everything is set up correctly
