from dataclasses import replace
import json
import pytest

from backend.platform.voice.repository import (
    VoiceDNAAccessError, VoiceDNANotFoundError, VoiceDNARepository,
    VoiceDNAVersionConflictError,
)
from backend.platform.voice.voice_dna import ConsentStatus, VoiceConsent, VoiceDNA, VoiceUsageClass


def dna(version=1, products=('forgecall',), project='p1'):
    return VoiceDNA(
        voice_id='voice-1', name='Priya', owner_id='owner-1', project_id=project,
        usage_class=VoiceUsageClass.AUTHORIZED_CLONED,
        languages=('en', 'bn'), reference_asset_ids=('asset-ref-1',),
        consent=VoiceConsent(ConsentStatus.AUTHORIZED, 'consent-1', True, False, True),
        allowed_products=products, version=version,
    )


def test_repository_persists_and_hydrates_voice_dna(tmp_path):
    repo = VoiceDNARepository(tmp_path)
    repo.save(dna())
    loaded = repo.get('voice-1')
    assert loaded == dna()
    assert loaded.reference_asset_ids == ('asset-ref-1',)
def test_repository_preserves_version_history_and_rejects_conflict(tmp_path):
    repo = VoiceDNARepository(tmp_path)
    repo.save(dna())
    repo.save(replace(dna(), version=2, warmth=0.8))
    assert [item.version for item in repo.history('voice-1')] == [1, 2]
    assert repo.get('voice-1').warmth == 0.8
    with pytest.raises(VoiceDNAVersionConflictError):
        repo.save(replace(dna(), version=2))


def test_repository_enforces_product_and_project_scope(tmp_path):
    repo = VoiceDNARepository(tmp_path)
    repo.save(dna())
    assert repo.get_authorized('voice-1', product_id='forgecall', project_id='p1').voice_id == 'voice-1'
    with pytest.raises(PermissionError):
        repo.get_authorized('voice-1', product_id='forgesocial', project_id='p1')
    with pytest.raises(VoiceDNAAccessError):
        repo.get_authorized('voice-1', product_id='forgecall', project_id='p2')


def test_repository_stores_only_opaque_reference_ids_not_audio(tmp_path):
    repo = VoiceDNARepository(tmp_path)
    repo.save(dna())
    raw = (tmp_path / 'voice-1' / 'v1.json').read_text(encoding='utf-8')
    payload = json.loads(raw)
    assert payload['reference_asset_ids'] == ['asset-ref-1']
    assert 'audio' not in raw.lower()
    assert 'base64' not in raw.lower()
    assert 'credential' not in raw.lower()
def test_list_for_product_returns_only_permitted_latest_profiles(tmp_path):
    repo = VoiceDNARepository(tmp_path)
    repo.save(dna())
    repo.save(VoiceDNA(
        voice_id='voice-2', name='Narrator', owner_id='owner-1', project_id='p1',
        usage_class=VoiceUsageClass.DESIGNED_FICTIONAL,
        allowed_products=('forgestudio',), version=1,
    ))
    assert [item.voice_id for item in repo.list_for_product('forgecall', project_id='p1')] == ['voice-1']


def test_missing_voice_is_explicit(tmp_path):
    repo = VoiceDNARepository(tmp_path)
    with pytest.raises(VoiceDNANotFoundError):
        repo.get('missing')
