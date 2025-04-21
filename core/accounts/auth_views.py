from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            # Delete the token associated with the user
            request.user.auth_token.delete()
            return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)
        except (AttributeError, Token.DoesNotExist):
            # Handle cases where the user might not have a token (e.g., session auth)
            # Or if the token was already deleted
            return Response({"error": "No active token found or already logged out."}, status=status.HTTP_400_BAD_REQUEST) 