# SUMM AI Backend Translation API

## Overview

This project is a Django-based backend API that provides text translation services for both plain text and HTML content. The API interacts with a translation service to translate text from one language to another while preserving the HTML structure when needed. The API also supports user authentication and includes endpoints for admin users to view all translations associated with specific users.

## Table of Contents

1. [Setup](#setup)
2. [API Endpoints](#api-endpoints)
3. [Key Findings](#key-findings)
4. [Challenges](#challenges)
5. [Testing](#testing)
6. [Deployment](#deployment)

## Setup

### Installation

1. **Clone the Repository:**

   ```bash
   git clone <repository_url>
   cd summ-ai-backend
   ```

2. **Create a Virtual Environment:**

   ```bash
   python -m venv env
   source env/bin/activate
   ```

3. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables:**

   Create a `.env` file in the project root directory with the following variables:

   ```plaintext
   DJANGO_SECRET_KEY=your_secret_key
   DJANGO_SUPERUSER_USERNAME=your_admin
   DJANGO_SUPERUSER_EMAIL=your_admin_email
   DJANGO_SUPERUSER_PASSWORD=your_admin_password
   DJANGO_DEBUG=True
   DEEPL_API_KEY=your_deepl_api_key
   ```

5. **Run Migrations:**

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a Superuser:**

   ```bash
   python manage.py createsuperuser
   ```

7. **Start the Development Server:**

   ```bash
   python manage.py runserver
   ```

### Docker Setup

1. **Build and Run the Docker Containers:**

   ```bash
   docker-compose up --build
   ```

2. **Access the API:**

   The API will be available at `http://127.0.0.1:8000/`.

## API Endpoints

### User Endpoints

- **POST /api/register/**: Register a new user.
- **POST /api/login/**: Authenticate and obtain JWT tokens.
- **GET /api/user/**: Get details of the authenticated user.

### Translation Endpoints

- **POST /api/translate/**: Translate text or HTML content.
  - **Supported Language Tags**: Below are the top 5 most popular language tags:
  
    - **EN-GB** - English (British)
    - **EN-US** - English (American)
    - **ES** - Spanish
    - **FR** - French
    - **DE** - German
  
  For a full list of supported languages and specific details, refer to the [DeepL Target Language support documentation](https://developers.deepl.com/docs/resources/supported-languages).

- **GET /api/translations/**: Retrieve all translations for the authenticated user.

### Admin Endpoints

- **GET /api/admin/users/**: List all users (admin only).
- **GET /api/admin/translations/<user_id>/**: Retrieve all translations for a specific user (admin only).

## Key Findings

- **HTML Structure Preservation**: One of the key features of the API is its ability to translate only the text within HTML tags while preserving the structure. This ensures that the translated content maintains its formatting and appearance.
  
- **Chunk-Based Translation**: The API splits large text into smaller chunks before translation. This approach helps in handling large texts efficiently and avoids issues related to API limits.

- **Parallel Processing**: By using Python's `ThreadPoolExecutor`, the API translates chunks of text in parallel, significantly improving performance for large texts or HTML content.

## Challenges

1. **Preserving HTML Structure**:
   - **Problem**: Translating HTML content while maintaining the structure of the document was challenging, especially when dealing with complex nested tags.
   - **Solution**: By using `BeautifulSoup`, we effectively identified and translated only the inner text of tags, ensuring that the overall HTML structure was preserved.

2. **Finding a Suitable Translation API**:

   - **Problem**: Due to the prior utilization of my free trial for the `Google Cloud Translation` API in other research projects, I was unable to leverage it for this initiative. Early attempts with the `Googletrans` API revealed significant challenges, notably with missing punctuation in translations, particularly when targeting Spanish (ES).
   - **Solution**: Switched to the `DeepL` API, which provided better overall translation quality, though it still had some issues with capitalization and translating to certain languages like Arabic.

## Testing

### Running Tests

1. **Run All Tests:**

   ```bash
   pytest
   ```

2. **Running Tests with Docker:**

   After deploying the application with Docker, you can run the unit tests using `pytest` to ensure everything is working as expected:

   ```bash
   docker-compose exec web pytest
   ```

   This command runs the tests inside the Docker container.

3. **Sample Test Cases**:
   - Tests for registering users, logging in, and refreshing tokens.
   - Tests for translating plain text and HTML content.
   - Tests for admin-specific endpoints.

## Deployment

### Docker

1. **Build the Docker Image:**

   ```bash
   docker-compose build
   ```

2. **Start the Containers:**

   ```bash
   docker-compose up
   ```
