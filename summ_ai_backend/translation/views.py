from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import RegisterSerializer, UserSerializer
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Translation
from .serializers import TranslationSerializer
from .utils import translate_text, translate_html
from django.shortcuts import render

def documentation_view(request):
    """ 
    Renders the main documentation page.
    
    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: The rendered HTML for 'index.html'.
    """
    return render(request, 'index.html')

class RegisterView(generics.CreateAPIView):
    """ 
    View for registering a new user. Allows any visitor to create a user account.
    """
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class UserDetailView(generics.RetrieveAPIView):
    """ 
    Provides detail view for the currently authenticated user.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """ Returns the user from the current request context. """
        return self.request.user

class TranslationCreateView(APIView):
    """ 
    Handles the creation of new translations. Requires user authentication.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Receives and processes a translation request based on the content type.
        
        Args:
            request: The HTTP request object containing 'original_text', 'content_type', and 'dest_language'.
            args: Additional arguments.
            kwargs: Keyword arguments.

        Returns:
            Response: Serialized data of the created translation or error message.
        """
        try:
            original_text = request.data.get('original_text')
            content_type = request.data.get('content_type')
            dest_language = request.data.get('dest_language')

            # Validation checks for request data
            if not original_text:
                return Response({"error": "original_text is required."}, status=status.HTTP_400_BAD_REQUEST)
            if not content_type:
                return Response({"error": "content_type is required."}, status=status.HTTP_400_BAD_REQUEST)
            if content_type not in ['plain', 'html']:
                return Response({"error": "content_type must be 'plain' or 'html'."}, status=status.HTTP_400_BAD_REQUEST)
            if not dest_language:
                return Response({"error": "dest_language is required."}, status=status.HTTP_400_BAD_REQUEST)

            # Process translation based on content type
            if content_type == 'html':
                translated_text = translate_html(original_text, dest_language)
                print(f'Translated HTML: {translated_text}')
            else:
                translated_text = translate_text(original_text, dest_language)
                print(f'Translated Text: {translated_text}')

            # Create and return the translation model instance
            translation = Translation.objects.create(
                user=request.user,
                original_text=original_text,
                translated_text=translated_text,
                content_type=content_type
            )
            serializer = TranslationSerializer(translation)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(f"Error: {e}")  
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AdminTranslationListView(APIView):
    """
    View to list all translations for a specific user, accessible only by admin users.
    """
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, user_id, *args, **kwargs):
        """
        Retrieves all translations made by a specified user.

        Args:
            request: The HTTP request object.
            user_id: The unique identifier for a user whose translations are to be retrieved.
            args: Additional arguments.
            kwargs: Keyword arguments.

        Returns:
            Response: Serialized data of the translations or an error message.
        """
        try:
            user = User.objects.get(id=user_id)
            translations = Translation.objects.filter(user=user)
            serializer = TranslationSerializer(translations, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class AdminUserListView(APIView):
    """
    View to retrieve a list of all users, accessible only by admin users.

    Attributes:
        permission_classes: Specifies the permissions that control access to this view.
    """
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):
        """
        Retrieves all users from the database.

        Args:
            request: The HTTP request object.
            args: Additional arguments.
            kwargs: Keyword arguments.

        Returns:
            Response: Serialized data of all users or an error message.
        """
        try:
            users = User.objects.all()
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TranslationListView(generics.ListAPIView):
    """
    View to list all translations associated with the authenticated user.
    """
    serializer_class = TranslationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Retrieves translations made by the currently authenticated user.

        Returns:
            QuerySet: A queryset of Translation objects for the authenticated user.
        """
        return Translation.objects.filter(user=self.request.user)
    
class UserDetailView(generics.RetrieveAPIView):
    """
    Provides detail view for the currently authenticated user.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """
        Returns the user from the current request context.

        Returns:
            User instance: The user instance associated with the current authenticated user.
        """
        return self.request.user
    
