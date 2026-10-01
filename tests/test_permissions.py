from django.urls import reverse


def test_staff_forbidden_on_admin_pages(client, staff_user):
    client.force_login(staff_user)
    response = client.get(reverse("participants:list"))
    assert response.status_code == 403


def test_anonymous_redirect_to_login(client):
    response = client.get(reverse("scanner:page"))
    assert response.status_code == 302


def test_staff_can_open_scanner(client, staff_user):
    client.force_login(staff_user)
    response = client.get(reverse("scanner:page"))
    assert response.status_code == 200
