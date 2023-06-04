from django.urls import path

from .views import (
    DeleteProfilePicture,
    UpdateProfile,
    FollowUserProfile,
    DetailedGeneralProfileInfo,
    UnfollowUserProfile,
    PersonalProfileInfo,
    WalletInfoView,
    ChargeWalletView,
    GetTicketsList,
    GetTicket,
    CreateTicket
    )

app_name = "user_profile"
urlpatterns = [
    path("", PersonalProfileInfo.as_view(), name="personal_profile"),
    path("update/", UpdateProfile.as_view(), name="update_profile"),
    path(
        "delete/picture/", DeleteProfilePicture.as_view(), name="delete_profile_image"
    ),
    path("follow/", FollowUserProfile.as_view(), name="follow_user"),
    path("unfollow/<str:username>", UnfollowUserProfile.as_view(), name="unfollow_user"),
    path("general/<str:username>", DetailedGeneralProfileInfo.as_view(), name="detail-general-profile"),
    path("wallet", WalletInfoView.as_view(), name="wallet-info"),
    path("wallet/charge", ChargeWalletView.as_view(), name="charge-wallet"),
    path("tickets", GetTicketsList.as_view(), name="ticket-list"),
    path("ticket/<int:ticket_id>", GetTicket.as_view(), name="get-ticket"),
    path("ticket/create", CreateTicket.as_view(), name="create-ticket")
]
