# Use the official Python image as the base image
FROM --platform=linux/amd64 python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . .
ENV OPENAI_API_KEY="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"
ENV OPENAI_ASSISTANT_ID="asst_VJZ2bkhVvyXUgzPkkvJ2Y5us"

# Expose the port that Streamlit will run on
EXPOSE 8501

# Run the Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
