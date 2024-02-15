from django.http import Http404  # added by me
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import (
    generics,
    status,
)
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.parsers import JSONParser

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
import uuid
from user.models import (
    User,
)
from user.serializers import (
    UserSerializer,
    UserImageSerializer,
    UserCoverSerializer,
    UserDeleteSerializer,
    UserDialogSerializer,
    UserGenderChoiceSerializer,
    UserRoleDialogSerializer,
)

from user.filters import UserFilter

from rcm_api.pagination import StandardResultsSetPagination


# separating creating user and upload his photo Approach
class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Capitalize the user's name before saving
        name = serializer.validated_data.get("name", "")
        capitalized_name = name.lower()
        serializer.save(name=capitalized_name)

    def create(self, request, *args, **kwargs):
        user = self.request.user
        allowed_roles = ["SUPERUSER", "OWNER", "ADMIN"]
        if user.role not in allowed_roles:
            raise PermissionDenied(_("You don't have permission to create users."))

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(
            {"detail": _("User created successfully")}, status=status.HTTP_201_CREATED
        )




# class UploadUserPhotoView(generics.UpdateAPIView):
#     serializer_class = UserImageSerializer
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated]
#     lookup_field = "id"  # Set the lookup field to 'id'

#     def get_queryset(self):
#         return get_user_model().objects.all()

#     def get_object(self):
#         user_id = self.request.query_params.get("user_id")
#         try:
#             user = User.objects.get(id=user_id)
#             self.check_object_permissions(self.request, user)
#             return user
#         except User.DoesNotExist:
#             raise Http404(_("User not found."))

#     def update(self, request, *args, **kwargs):
#         partial = kwargs.pop("partial", False)
#         instance = self.get_object()
#         serializer = self.get_serializer(instance, data=request.data, partial=partial)
#         serializer.is_valid(raise_exception=True)
#         self.perform_update(serializer)
#         # return Response(serializer.data)
#         return Response(
#             {"detail": _("Your photo changed successfully")},
#             status=status.HTTP_200_OK,
#         )

#     def get_serializer_class(self):
#         return self.serializer_class


class UploadUserPhotoView(generics.UpdateAPIView):
    serializer_class = UserImageSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        self.action = self.request.method.lower()

    @action(methods=["POST"], detail=True, url_path="upload-image")
    def upload_image(self, request, pk=None):
        user = self.request.user
        serializer = self.get_serializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_serializer_class(self):
        if self.action == "upload_image":
            return UserImageSerializer
        return self.serializer_class

    def update(self, request, *args, **kwargs):
        user = self.request.user  # Get the user from the JWT token
        serializer = self.get_serializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            user.resize_and_save_avatar()
            return Response(
                {"detail": _("Your photo changed successfully")},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UploadUserCoverView(generics.UpdateAPIView):
    serializer_class = UserCoverSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        self.action = self.request.method.lower()

    @action(methods=["POST"], detail=True, url_path="upload-image")
    def upload_image(self, request, pk=None):
        user = self.request.user
        serializer = self.get_serializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_serializer_class(self):
        if self.action == "upload_image":
            return UserImageSerializer
        return self.serializer_class

    def update(self, request, *args, **kwargs):
        user = self.request.user  # Get the user from the JWT token
        serializer = self.get_serializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": _("Your cover photo changed successfully")},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ManagerUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        allowed_roles = ["OWNER", "SUPERUSER", "MANAGER"]

        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        if instance.role not in allowed_roles:
            return Response(
                {"detail": _("You are not authorized to change the role.")},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(
            {"detail": _("Your data Updated successfully")}, status=status.HTTP_200_OK
        )


class UserListView(generics.ListAPIView):
    # queryset = User.objects.filter(is_deleted=False)
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = UserFilter
    search_fields = ["name", "name_ar", "mobile_number", "email", "identification"]
    ordering_fields = ["name_ar"]

    def get_queryset(self):
        user = self.request.user
        allowed_roles = ["SUPERUSER", "OWNER", "MANAGER"]
        if user.role not in allowed_roles:
            raise PermissionDenied(_("You don't have permission to view users."))

        queryset = User.objects.filter(is_deleted=False, is_superuser=False)
        return queryset


class DeletedUserView(generics.ListAPIView):
    # queryset = User.objects.filter(is_deleted=True)
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = UserFilter
    search_fields = ["name", "name_ar", "mobile_number", "email", "identification"]
    ordering_fields = ["name_ar"]

    def get_queryset(self):
        user = self.request.user
        allowed_roles = ["SUPERUSER", "OWNER", "MANAGER"]
        if user.role not in allowed_roles:
            raise PermissionDenied(
                _("You don't have permission to view deleted users.")
            )

        queryset = User.objects.filter(is_deleted=True)
        return queryset


class UserRetrieveView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        return User.objects.filter(is_deleted=False)

    def get_object(self):
        user_id = self.request.query_params.get("user_id")
        user = get_object_or_404(self.get_queryset(), id=user_id)
        return user


class UserDeleteTemporaryView(generics.RetrieveUpdateAPIView):
    serializer_class = UserDeleteSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_object(self):
        user_id = self.request.query_params.get("user_id")
        user = get_object_or_404(User, id=user_id)
        return user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        user = self.request.user
        allowed_roles = ["SUPERUSER", "OWNER", "MANAGER"]

        if user.role not in allowed_roles:
            raise PermissionDenied(_("You don't have permission to delete."))

        if instance.is_deleted:
            return Response(
                {"detail": _("User is already deleted")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(
            {"detail": _("User temp deleted successfully")}, status=status.HTTP_200_OK
        )


class UserRestoreView(generics.RetrieveUpdateAPIView):
    serializer_class = UserDeleteSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_object(self):
        user_id = self.request.query_params.get("user_id")
        user = get_object_or_404(User, id=user_id)
        return user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        user = self.request.user
        allowed_roles = ["SUPERUSER", "OWNER", "MANAGER"]

        if user.role not in allowed_roles:
            raise PermissionDenied(_("You don't have permission to restore."))

        if instance.is_deleted == False:
            return Response(
                {"detail": _("User is not deleted")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(
            {"detail": _("User restored successfully")}, status=status.HTTP_200_OK
        )


class UserUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_object(self):
        user_id = self.request.query_params.get("user_id")
        user = get_object_or_404(User, id=user_id)
        return user

    def update(self, request, *args, **kwargs):
        user = self.request.user
        allowed_roles = ["SUPERUSER", "OWNER", "MANAGER"]

        if user.role not in allowed_roles:
            raise PermissionDenied(_("You don't have permission to update."))

        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(
            {"detail": _("User Updated successfully")}, status=status.HTTP_200_OK
        )


# class UserDeleteView(generics.RetrieveDestroyAPIView):
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated]
#     lookup_field = "id"  # Change this to the field used for the primary key

# def get_object(self):
#     user_id = self.request.query_params.get("user_id")
#     user = get_object_or_404(User, id=user_id)
#     return user

# def delete(self, request, *args, **kwargs):
#     user = self.get_object()  # Get the user instance
#     user.delete()
#     return Response(
#         {"detail": _("User permanently deleted successfully")},
#         status=status.HTTP_204_NO_CONTENT,
#     )


# class UserDeleteView(generics.RetrieveDestroyAPIView):
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated]

#     def delete(self, request, *args, **kwargs):
#         user = self.request.user
#         allowed_roles = ["SUPERUSER", "OWNER", "MANAGER"]
#         if user.role not in allowed_roles:
#             raise PermissionDenied(_("You are not allowed to delete"))

#         user_id_list = self.request.data.get("user_id", "").split(',')

#         if not user_id_list:
#             return Response(
#                 {"detail": _("No user IDs provided for deletion")},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         # Check if each UUID is valid
#         for uid in user_id_list:
#             try:
#                 uuid.UUID(uid.strip())
#             except ValueError:
#                 raise ValidationError(_("'{}' is not a valid UUID.".format(uid)))

#         users = User.objects.filter(id__in=user_id_list)
#         if not users.exists():
#             return Response(
#                 {"detail": _("No users found")},
#                 status=status.HTTP_404_NOT_FOUND,
#             )

#         users.delete()

#         return Response(
#             {"detail": _("Users permanently deleted successfully")},
#             status=status.HTTP_204_NO_CONTENT,
#         )
from rest_framework.parsers import JSONParser


class UserDeleteView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request, format=None):
        user = self.request.user
        allowed_roles = ["SUPERUSER", "OWNER", "MANAGER"]
        if user.role not in allowed_roles:
            raise PermissionDenied(_("You are not allowed to delete"))

        data = JSONParser().parse(request)
        user_id_list = data.get("user_id", [])

        if not user_id_list:
            return Response(
                {"detail": _("No user IDs provided for deletion")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if each UUID is valid
        for uid in user_id_list:
            try:
                uuid.UUID(uid.strip())
            except ValueError:
                raise ValidationError(_("'{}' is not a valid UUID.".format(uid)))

        users = User.objects.filter(id__in=user_id_list)
        if not users.exists():
            return Response(
                {"detail": _("No users found")},
                status=status.HTTP_404_NOT_FOUND,
            )

        users.delete()

        return Response(
            {"detail": _("Users permanently deleted successfully")},
            status=status.HTTP_204_NO_CONTENT,
        )


# User login view
class LoginView(APIView):
    # Primary login view
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        identifier = request.data.get("identifier")  # Field for email or phone number
        password = request.data.get("password")

        # Filter using Q objects to match either email or phone_number
        user = User.objects.filter(
            Q(email=identifier) | Q(mobile_number=identifier)
        ).first()

        if user is None:
            raise AuthenticationFailed(
                _("Email or phone number or password is invalid")
            )
        if user.is_staff == False:
            raise AuthenticationFailed(
                _("Email or phone number or password is invalid!!!")
            )
        if not user.is_active:
            raise AuthenticationFailed(_("User account is inactive"))
        if user.is_deleted == True:
            raise AuthenticationFailed(_("This user is deleted"))
        if not user.check_password(password):
            raise AuthenticationFailed(
                _("Email or phone number or password is invalid")
            )

        refresh = RefreshToken.for_user(user)
        response = Response()
        response.data = {
            "identifier": user.email
            if user.email == identifier
            else user.mobile_number,
            "role": user.role,
            "name": user.name,
            "is_staff": user.is_staff,
            "access_token": str(refresh.access_token),
            # "refresh_token": str(refresh),
        }
        return response


# User Dialogs
class UserDialogView(generics.ListAPIView):
    serializer_class = UserDialogSerializer
    queryset = User.objects.filter(is_deleted=False)
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


class UserGenderDialogView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Define the gender choices here
        gender_choices = [
            {"value": "male", "display": _("Male")},
            {"value": "female", "display": _("Female")},
        ]

        serializer = UserGenderChoiceSerializer(gender_choices, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserRoleDialogView(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Define the role choices here

        role_choices = [
            {"value": "OWNER", "display": _("Owner")},
            {"value": "MANAGER", "display": _("Manager")},
            {"value": "WAITER", "display": _("Waiter")},
            {"value": "CASHIER", "display": _("Cashier")},
            {"value": "CHEF", "display": _("Chef")},
            {"value": "DELIVERY", "display": _("Delivery")},
        ]

        serializer = UserRoleDialogSerializer(role_choices, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
