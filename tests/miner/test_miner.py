import pytest
import uvicorn
from fastapi.testclient import TestClient
from eden_subnet.miner.miner import app, GenerateRequest, Miner
from eden_subnet.miner.data_models import MinerSettings
from communex.client import Ss58Address

client = TestClient(app)


@pytest.mark.parametrize(
    "messages, model, expected_status, expected_response",
    [
        # Test ID: 1 - Happy path with valid input
        (
            [{"content": "Hello, world!"}],
            "cl100k_base",
            200,
            {
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": [9906, 11, 1917, 0],
                        },
                    }
                ]
            },
        ),
        # Test ID: 2 - Edge case with empty message
        (
            [{"content": ""}],
            "cl100k_base",
            200,
            {
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": []},
                    }
                ]
            },
        ),
        # Test ID: 3 - Error case with invalid model
        (
            [{"content": "Hello, world!"}],
            "unknown_model",
            200,
            {
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": [9906, 11, 1917, 0],
                        },
                    }
                ]
            },
        ),
    ],
    ids=["happy-path", "edge-case-empty-message", "error-invalid-model"],
)
def test_generate_endpoint(messages, model, expected_status, expected_response):
    # Arrange
    request = GenerateRequest(messages=messages, model=model)

    # Act
    response = client.post("/generate", json=request.model_dump())

    # Assert
    assert response.status_code == expected_status
    assert response.json() == expected_response


@pytest.mark.parametrize(
    "key_name, module_path, host, port, ss58_address, use_testnet, call_timeout, expected_instance",
    [
        # Test ID: 4 - Happy path with valid miner initialization
        (
            "miner.Miner",
            "miner.Miner",
            "127.0.0.1",
            8080,
            Ss58Address("miner.Miner"),
            True,
            60,
            Miner,
        ),
    ],
    ids=["happy-path-miner-init"],
)
def test_miner_initialization(
    key_name,
    module_path,
    host,
    port,
    ss58_address,
    use_testnet,
    call_timeout,
    expected_instance,
):
    # Arrange
    miner = Miner(
        key_name, module_path, host, port, ss58_address, use_testnet, call_timeout
    )

    # Assert
    assert isinstance(miner, expected_instance)
    assert miner.key_name == key_name
    assert miner.module_path == module_path
    assert miner.host == host
    assert miner.port == port
    assert miner.ss58_address == ss58_address
    assert miner.use_testnet == use_testnet
    assert miner.call_timeout == call_timeout


@pytest.mark.parametrize(
    "settings, expected_host, expected_port",
    [
        # Test ID: 5 - Happy path for serve endpoint
        (
            MinerSettings(
                key_name="admin", module_path="admin", host="127.0.0.1", port=8080
            ),
            "127.0.0.1",
            8080,
        ),
    ],
    ids=["happy-path-serve"],
)
def test_serve_endpoint(settings, expected_host, expected_port, monkeypatch):
    # Arrange
    def mock_run(app, host, port):
        assert host == expected_host
        assert port == expected_port

    monkeypatch.setattr(uvicorn, "run", mock_run)

    # Act
    miner = Miner(
        "miner.Miner",
        "miner.Miner",
        "127.0.0.1",
        8080,
        Ss58Address("5C5QeEQQChqXr7DeZng9CwtvmQFfDAeHCtU88caEUu8C7Qgn"),
        True,
        60,
    )
    miner.serve(settings)

    # Assert - Assertions are done within the mock_run function
