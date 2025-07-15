# RNP Traffic Fine Checker (Dockerized)

This application automatically checks the Rwanda National Police (RNP) traffic fines portal for any outstanding fines associated with a specific vehicle. If a fine is found, it sends a detailed email notification.

The application is designed to run continuously inside a Docker container on a server or VPS, performing the check once every day.

## Features

-   **Modular Design**: Code is separated by responsibility (Scraping, Notifying, Configuration).
-   **Automated Daily Checks**: Uses a scheduler to run at a configurable time.
-   **Email Notifications**: Sends a well-formatted HTML email if a fine is detected.
-   **Dockerized Deployment**: Encapsulated for easy, reliable deployment on any system with Docker.
-   **Resilient**: Designed to auto-restart if the server reboots or the application crashes.
-   **Secure Configuration**: Sensitive data like passwords are kept in a `.env` file, separate from the main configuration and source code.

## Project Structure

```
traffic-fine-checker/
├── main.py                 # Main entry point: handles CLI args and scheduling
├── scraper.py              # Scraper class for all web interactions
├── notifier.py             # Notifier class for sending emails
├── config.py               # Module for loading all configuration
├── Dockerfile              # Instructions to build the Docker image
├── .dockerignore           # Specifies files to exclude from the image
├── config.ini              # Vehicle and email settings
├── .env                    # Secret email password
└── requirements.txt        # Python library dependencies
```

## Prerequisites

-   A VPS or server with Docker and Docker Compose installed.
-   Git (for cloning the repository).
-   An email account (e.g., Gmail) to send notifications from.

## Setup and Deployment on a VPS

Follow these steps to get the application running on your server.

### 1. Clone the Repository

Log into your VPS via SSH and clone the project:

```bash
git clone <your-repository-url>
cd traffic-fine-checker
```

### 2. Configure the Application

You need to create two configuration files.

**A. Create `config.ini` for vehicle and email settings:**

Create the file `config.ini` and add your details.

```ini
[VEHICLE]
PLATE_NUMBER = RXXXXX
TIN_NUMBER = 1XXXXX

[EMAIL]
# Example for Gmail. Use your email provider's SMTP details.
SMTP_SERVER = smtp.gmail.com
SMTP_PORT = 465
SENDER_EMAIL = your_email@gmail.com
RECEIVER_EMAIL = email_to_notify@example.com
```

**B. Create `.env` for your secret password:**

Create the file `.env` to store your email password securely.

```
EMAIL_PASSWORD="YOUR_EMAIL_APP_PASSWORD"
```

**IMPORTANT: Using Gmail App Passwords**
If you use Gmail with 2-Factor Authentication (2FA), you **must** generate an "App Password". You cannot use your regular account password.
1.  Go to your Google Account settings: [https://myaccount.google.com/](https://myaccount.google.com/)
2.  Go to **Security**.
3.  Under "Signing in to Google," ensure 2-Step Verification is ON.
4.  Click on **App Passwords**.
5.  Select "Mail" for the app and "Other (Custom name)" for the device. Name it something like "VPS Fines Checker".
6.  Google will generate a 16-character password. Use **this password** in your `.env` file.

### 3. Build the Docker Image

From the project's root directory, run the build command. This will create a Docker image named `fine-checker-app` based on the `Dockerfile`.

```bash
docker build -t fine-checker-app .
```

### 4. Run the Container

To start the application, run the following command. This will start the container in detached mode and ensure it restarts automatically.

```bash
docker run -d \
  --name traffic-checker \
  --restart always \
  -v $(pwd)/config.ini:/app/config.ini \
  -v $(pwd)/.env:/app/.env \
  fine-checker-app
```
*   `-d`: Runs the container in the background.
*   `--name traffic-checker`: Assigns a convenient name to the container.
*   `--restart always`: Ensures the container starts on system reboot.
*   `-v`: Mounts your local config files into the container, allowing you to change them without rebuilding the image.

The application will perform an initial check on startup and then run daily at 9:00 AM (as scheduled in `main.py`).

## Managing the Application

Here are the most common Docker commands for managing your running container.

-   **Check the logs:**
    ```bash
    docker logs traffic-checker
    ```
    To follow the logs in real-time:
    ```bash
    docker logs -f traffic-checker
    ```

-   **Stop the application:**
    ```bash
    docker stop traffic-checker
    ```

-   **Start the application:**
    ```bash
    docker start traffic-checker
    ```

-   **Restart the application** (useful after changing `config.ini` or `.env`):
    ```bash
    docker restart traffic-checker
    ```

-   **Remove the container** (must be stopped first):
    ```bash
    docker rm traffic-checker
    ```

## Testing Commands

Before deploying the scheduler, you can test parts of the application.

-   **Test a single fine check:**
    ```bash
    docker run --rm \
      -v $(pwd)/config.ini:/app/config.ini \
      -v $(pwd)/.env:/app/.env \
      fine-checker-app python main.py --run-once
    ```

-   **Test the email notification:**
    ```bash
    docker run --rm \
      -v $(pwd)/config.ini:/app/config.ini \
      -v $(pwd)/.env:/app/.env \
      fine-checker-app python main.py --test-email
    ```
    *The `--rm` flag automatically cleans up the container after it exits.*