from apps.participants.models import Participant
from apps.qr.services import extract_token, generate_token, hash_token


def test_extract_token_from_url():
    token = generate_token()
    assert extract_token(f"https://example.com/q/{token}") == token


def test_valid_and_invalid_token_lookup(db, participant):
    assert Participant.objects.filter(qr_token_hash=hash_token(participant._raw_token), qr_active=True).exists()
    assert not Participant.objects.filter(qr_token_hash=hash_token("bad-token"), qr_active=True).exists()


def test_deactivated_qr_rejected(db, participant):
    participant.qr_active = False
    participant.save(update_fields=["qr_active"])
    assert not Participant.objects.filter(qr_token_hash=hash_token(participant._raw_token), qr_active=True).exists()
