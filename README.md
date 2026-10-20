# AI Health Report Analyzer

An AI-powered Flask web app that reads medical PDF reports and presents health information in simpler language.

*Disclaimer: This app is for informational purposes only and is not a substitute for professional medical advice, diagnosis, or treatment.*

## Run locally

1. Install Python 3.10 or newer.
2. Clone the repository and open its folder:

   ```bash
   git clone https://github.com/avanishrai19/ai-health-report-agent.git
   cd ai-health-report-agent
   ```

3. Install the Python dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Set the Gemini API key. You can put it in a local `.env` file (do not commit this file):

   ```env
   GENAI_API_KEY=your_gemini_api_key
   SECRET_KEY=replace_with_a_long_random_value
   ```

5. Start the app:

   ```bash
   python app.py
   ```

   Open <http://127.0.0.1:5000>.

The app uses a local SQLite database by default. Set `DATABASE_URL` to a PostgreSQL connection URL when using a hosted database.

## Deploy on Render

This is a Flask/Python application, so GitHub Pages cannot run it. Create a **Web Service** on Render and connect this repository:

- **Build command:** `pip install -r requirements.txt`
- **Start command:** `gunicorn app:app`
- Add `GENAI_API_KEY` and `SECRET_KEY` under the service's environment variables.
- For persistent user accounts, add a PostgreSQL database and set `DATABASE_URL` to its internal connection URL.

Render will provide a service URL for the live app. The GitHub repository URL itself displays the README and is not the app URL. After pushing changes, trigger a new deployment on the hosting service.
