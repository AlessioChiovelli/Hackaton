FROM python:3.12.9

WORKDIR /app

COPY requrements.txt            /app/requrements.txt
RUN pip install --no-cache-dir -r requrements.txt

COPY APIModules                 /app/APIModules
COPY APIModules/AIAgents        /app/APIModules/AIAgents
COPY APIModules/ObjectModels    /app/APIModules/ObjectModels
COPY APIModules/APIs            /app/APIModules/APIs

COPY frontend_pages             /app/frontend_pages
COPY static                     /app/static
COPY .streamlit                 /app/.streamlit
COPY streamlit_app.py           /app/streamlit_app.py
COPY app.py                     /app/app.py
COPY google_calendar.py         /app/google_calendar.py
COPY main.sh                    /app/main.sh

CMD ["streamlit", "run", "streamlit_app.py"]