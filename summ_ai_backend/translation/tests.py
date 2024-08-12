import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from translation.models import Translation
from unittest.mock import patch
from translation.utils import translate_text, translate_html



@pytest.fixture
def api_client():
    """Fixture that provides a Django REST framework APIClient instance."""
    return APIClient()

@pytest.fixture
def create_user():
    """Fixture to create a regular or admin user."""
    def make_user(username="testuser", password="testpassword", is_admin=False):
        user = User.objects.create_user(username=username, password=password, is_staff=is_admin)
        return user
    return make_user

@pytest.fixture
def get_tokens_for_user(create_user):
    """Fixture to create a user and return JWT tokens (refresh and access)."""

    # Create user
    user = create_user()
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

@pytest.fixture
def get_tokens_for_admin(create_user):
    """Fixture to create an admin user and return JWT tokens (refresh and access)."""
    
    # Create admin
    admin = create_user(username="adminuser", password="adminpassword", is_admin=True)
    refresh = RefreshToken.for_user(admin)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

@pytest.mark.django_db
def test_register(api_client):
    """
    Test the user registration endpoint.
    It should create a new user and return a 201 status code.
    """
    url = '/api/register/'
    data = {
        'username': 'newuser',
        'password': 'newpassword',
        'email': 'newuser@example.com'
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == 201
    assert User.objects.filter(username='newuser').exists()

@pytest.mark.django_db
def test_login(api_client, create_user):
    """
    Test the user login endpoint.
    It should authenticate the user and return access and refresh tokens.
    """
    create_user(username="loginuser", password="loginpassword")
    url = '/api/login/'
    data = {
        'username': 'loginuser',
        'password': 'loginpassword'
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == 200
    assert 'access' in response.data
    assert 'refresh' in response.data

@pytest.mark.django_db
def test_token_refresh(api_client, get_tokens_for_user):
    """
    Test the token refresh endpoint.
    It should return a new access token when provided with a valid refresh token.
    """
    url = '/api/token/refresh/'
    data = {'refresh': get_tokens_for_user['refresh']}
    response = api_client.post(url, data, format='json')
    assert response.status_code == 200
    assert 'access' in response.data

@pytest.mark.django_db
def test_user_detail(api_client, get_tokens_for_user):
    """
    Test the user detail endpoint.
    It should return the details of the authenticated user.
    """
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {get_tokens_for_user['access']}")
    url = '/api/user/'
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.data['username'] == 'testuser'

@pytest.mark.django_db
def test_translation_create(api_client, get_tokens_for_user):
    """
    Test the translation creation endpoint.
    It should translate the provided German text into English and save the translation.
    """
    # Set the user's JWT token for authentication
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {get_tokens_for_user['access']}")

    # Define the URL and data for translation
    url = '/api/translate/'
    data = {
        "original_text": "Hallo, Welt!",
        "content_type": "plain",
        "dest_language": "EN-US"
    }

    # Send the translation request
    response = api_client.post(url, data, format='json')
    assert response.status_code == 201

    # Retrieve and verify the translation from the database
    translation = Translation.objects.filter(user__username='testuser').first()
    assert translation is not None
    assert translation.original_text == "Hallo, Welt!"

    # Check if the translation matches the expected result
    expected_translation = "Hello, world!"
    assert translation.translated_text == expected_translation

    # Output details if the translation is incorrect
    if translation.translated_text != expected_translation:
        print(f"Expected translation: {expected_translation}")
        print(f"Actual translation: {translation.translated_text}")


@pytest.mark.django_db
def test_translation_list(api_client, get_tokens_for_user, create_user):
    """
    Test the translation list endpoint.
    It should return a list of all translations associated with the authenticated user.
    """

    # Create additional users
    user1 = create_user(username="user1", password="password1")
    user2 = create_user(username="user2", password="password2")

    # Create translations for each user
    Translation.objects.create(user=user1, original_text="Hallo Welt", translated_text="Hello World", content_type="plain")
    Translation.objects.create(user=user1, original_text="Guten Morgen", translated_text="Good Morning", content_type="plain")
    Translation.objects.create(user=user2, original_text="Guten Tag", translated_text="Good Day", content_type="plain")
    Translation.objects.create(user=user2, original_text="Auf Wiedersehen", translated_text="Goodbye", content_type="plain")

    # Create translations for the test user
    user_test = User.objects.get(username="testuser")
    Translation.objects.create(user=user_test, original_text="Hallo", translated_text="Hello", content_type="plain")
    Translation.objects.create(user=user_test, original_text="Wie geht's?", translated_text="How are you?", content_type="plain")

    # Authenticate as the test user and retrieve their translations
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {get_tokens_for_user['access']}")
    url = '/api/translations/'
    response = api_client.get(url)

    # Ensure the response is correct
    assert response.status_code == 200
    assert len(response.data) == 2  # The test user has two translations

    # Check the contents of the returned translations
    returned_texts = [translation['original_text'] for translation in response.data]
    assert "Hallo" in returned_texts
    assert "Wie geht's?" in returned_texts

@pytest.mark.django_db
def test_translate_html_simple():
    """
    Test the HTML translation utility.
    It should translate German text inside simple HTML tags to English while preserving the structure.
    """

    # Original simple HTML with German text
    original_html = """
    <div>
        <h1>Willkommen auf unserer Webseite</h1>
        <p>Dies ist ein einfacher Absatz.</p>
    </div>
    """

    # Translate the HTML from German to English using DeepL
    translated_html = translate_html(original_html, dest_language='EN-US')

    # Expected translation in English
    expected_html = """
    <div>
        <h1>Welcome to our website</h1>
        <p>This is a simple paragraph.</p>
    </div>
    """

    # Clean up the HTML for comparison by stripping extra whitespace
    expected_html_cleaned = ' '.join(expected_html.split())
    translated_html_cleaned = ' '.join(translated_html.split())

    # Assert that the translation matches the expected result
    assert translated_html_cleaned == expected_html_cleaned, f"Expected: {expected_html_cleaned}, but got: {translated_html_cleaned}"


@pytest.mark.django_db
def test_admin_translation_list(api_client, get_tokens_for_admin, create_user):
    """
    Test the admin translation list endpoint.
    It should allow an admin to view all translations for a specific user.
    This test creates multiple users and their translations, then verifies
    that the admin can retrieve translations for one specific user.
    """

    # Create multiple users with translations
    user1 = create_user(username="user1", password="password1")
    user2 = create_user(username="user2", password="password2")
    user3 = create_user(username="user3", password="password3")

    Translation.objects.create(user=user1, original_text="Auf Wiedersehen", translated_text="Goodbye", content_type="plain")
    Translation.objects.create(user=user1, original_text="Guten Morgen", translated_text="Good Morning", content_type="plain")

    Translation.objects.create(user=user2, original_text="Guten Abend", translated_text="Good Evening", content_type="plain")
    Translation.objects.create(user=user2, original_text="Danke schön", translated_text="Thank you", content_type="plain")

    Translation.objects.create(user=user3, original_text="Bitte", translated_text="Please", content_type="plain")

    # Admin retrieves translations for user1
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {get_tokens_for_admin['access']}")
    url = f'/api/admin/translations/{user1.id}/'
    response = api_client.get(url)

    # Assertions for user1's translations
    assert response.status_code == 200
    assert len(response.data) == 2
    assert any(translation['original_text'] == "Auf Wiedersehen" for translation in response.data)
    assert any(translation['original_text'] == "Guten Morgen" for translation in response.data)

    # Admin retrieves translations for user2
    url = f'/api/admin/translations/{user2.id}/'
    response = api_client.get(url)

    # Assertions for user2's translations
    assert response.status_code == 200
    assert len(response.data) == 2
    assert any(translation['original_text'] == "Guten Abend" for translation in response.data)
    assert any(translation['original_text'] == "Danke schön" for translation in response.data)

    # Admin retrieves translations for user3
    url = f'/api/admin/translations/{user3.id}/'
    response = api_client.get(url)

    # Assertions for user3's translation
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['original_text'] == "Bitte"




@pytest.mark.django_db
def test_admin_user_list(api_client, get_tokens_for_admin, create_user):
    """
    Test the admin user list endpoint.
    It should return a list of all users, accessible only by admins.
    The test creates multiple users and verifies that they are all present in the admin's user list.
    """

    # Create multiple users
    create_user(username="testuser", password="testpassword")
    create_user(username="user1", password="password1")
    create_user(username="user2", password="password2")
    create_user(username="user3", password="password3")

    # Authenticate as an admin
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {get_tokens_for_admin['access']}")
    
    # Retrieve the list of users
    url = '/api/admin/users/'
    response = api_client.get(url)
    
    assert response.status_code == 200

    # Check if all created users are in the returned list
    returned_usernames = [user['username'] for user in response.data]
    expected_usernames = ["adminuser", "testuser", "user1", "user2", "user3"]
    for username in expected_usernames:
        assert username in returned_usernames


