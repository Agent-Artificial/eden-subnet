import pytest
from eden_subnet.base.data_models import (
    ModuleSettings,
    Ss58Address,
    SampleInput,
    AccessControl,
)
from communex.compat.key import local_key_addresses


# Mock for local_key_addresses
@pytest.fixture
def mock_local_keys(monkeypatch):
    def mock_keys():
        return {
            "admin": Ss58Address("5FHneW46xGXgs5mUiveU4sbTyGBzmstUspZC92UhjJM694ty")
        }

    monkeypatch.setattr("communex.compat.key.local_key_addresses", mock_keys)


# Tests for ModuleSettings.get_ss58_address
@pytest.mark.parametrize(
    "key_name, expected_address, test_id",
    [
        (
            "admin",
            "5GjeD4Qkx8ZzcdbQ1V9m6davKnkqqLHnDWJjqy7eGoVZ7GXG",
            "happy_path_valid_key",
        ),
        ("", None, "error_case_empty_key_name"),
        ("unknown", None, "error_case_nonexistent_key"),
    ],
)
def test_get_ss58_address(key_name, expected_address, test_id, mock_local_keys):
    # Arrange
    settings = ModuleSettings(
        module_path="/path/to/module", key_name="admin", host="127.0.0.1", port=8080
    )

    # Act
    if key_name == "":
        with pytest.raises(ValueError) as exc_info:
            address = settings.get_ss58_address(key_name)
    elif key_name == "unknown":
        with pytest.raises(ValueError) as exc_info:
            address = settings.get_ss58_address(key_name)
    else:
        address = settings.get_ss58_address(key_name)

    # Assert
    if key_name in ["", "unknown"]:
        assert "not found" in str(exc_info.value) or "No key_name provided" in str(
            exc_info.value
        )
    else:
        assert address == expected_address


# Tests for AccessControl
@pytest.mark.parametrize(
    "whitelist, blacklist, test_id",
    [
        (["192.168.1.1:8080"], [], "happy_path_whitelist_only"),
        ([], ["192.168.1.1:8080"], "happy_path_blacklist_only"),
        (["192.168.1.1:8080"], ["10.0.0.1:8080"], "happy_path_both_lists"),
        ([], [], "edge_case_empty_lists"),
    ],
)
def test_access_control(whitelist, blacklist, test_id):
    # Arrange
    ac = AccessControl(whitelist=whitelist, blacklist=blacklist)

    # Act
    # No action needed as we are just testing initialization and storage

    # Assert
    assert ac.whitelist == whitelist
    assert ac.blacklist == blacklist


# Tests for SampleInput
@pytest.mark.parametrize(
    "prompt, test_id",
    [("Hello, world!", "happy_path_valid_prompt"), ("", "edge_case_empty_prompt")],
)
def test_sample_input(prompt, test_id):
    # Arrange
    sample = SampleInput(prompt=prompt)

    # Act
    # No action needed as we are just testing initialization and storage

    # Assert
    assert sample.prompt == prompt
