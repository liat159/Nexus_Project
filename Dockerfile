# שימוש בתמונת פייתון רשמית וקלה
FROM python:3.10-slim

# הגדרת תיקיית העבודה בתוך הקונטיינר
WORKDIR /app

# העתקת קובץ הדרישות והתקנתן (נעשה בנפרד כדי לנצל את מנגנון ה-Cache של דוקר)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# העתקת שאר קבצי הפרויקט (main.py, models.py, services.py וכו')
COPY . .

# חשיפת הפורט שבו האפליקציה רצה
EXPOSE 8000

# הפקודה שתריץ את השרת כשהקונטיינר עולה
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]