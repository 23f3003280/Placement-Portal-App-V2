# Student-Placement-Portal-Mad-2

This project is a web-based application designed to manage and streamline the student placement process within an educational institution. It provides a platform for students to create profiles, search for job opportunities, and apply for them. It also allows companies to post job listings and review student applications, and for administrators to oversee the entire process.

## Installation

To get a local copy up and running, follow these simple installation steps.

### Prerequisites

Before you begin, ensure you have the following installed:
*   Python 3.x & pip (for the backend)
*   Node.js & npm (for the frontend)

### Backend Setup

1.  Navigate to the backend directory from the project root:
    ```sh
    cd backend
    ```

2.  (Recommended) Create and activate a virtual environment:
    ```sh
    # Create the virtual environment
    python -m venv venv
    # Activate on Windows
    .\venv\Scripts\activate
    # Activate on macOS/Linux
    source venv/bin/activate
    ```

3.  Install the required Python packages:
    ```sh
    pip install -r requirements.txt
    ```

4.  Start the backend server (you may need to adjust the command based on your project's entry point):
    ```sh
    python app.py
    ```

### Frontend Setup

1.  In a new terminal, navigate to the frontend directory from the project root:
    ```sh
    cd frontend
    ```

2.  Install the required packages:
    ```sh
    npm install
    ```

3.  Start the frontend development server:
    ```sh
    npm start
    ```

Your application's frontend should now be running and accessible in your web browser, connected to the running backend.