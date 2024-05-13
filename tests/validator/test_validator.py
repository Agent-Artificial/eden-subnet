import pytest
from unittest.mock import patch, MagicMock
from pydantic import BaseModel
from eden_subnet.base.base import BaseValidator, Message
from eden_subnet.validator.validator import Validator, ValidatorSettings
from communex.compat.key import Ss58Address
from communex.client import CommuneClient

config = ValidatorSettings(
    key_name="validator.Validator",
    module_path="validator.Valdiator",
    host="localhost",
    port=8080,
)


# Test for BaseValidator.extract_address
@pytest.mark.parametrize(
    "input_string, expected_output, test_id",
    [
        ("192.168.1.1:8080", "192.168.1.1:8080", "T1"),
        ("no ip here", None, "T2"),
        ("256.256.256.256:9999", None, "T3"),
        ("192.168.1.1:65536", None, "T4"),
        ("192.168.1.1", None, "T5"),
        ("192.168.1.1:8080 extra text", "192.168.1.1:8080", "T6"),
    ],
)
def test_extract_address(input_string, expected_output, test_id):
    # Arrange

    # Act
    match = BaseValidator.extract_address(input_string)

    # Assert
    if expected_output:
        assert match.group(0) == expected_output
    else:
        assert match is None


# Test for BaseValidator.get_netuid
@pytest.mark.parametrize(
    "subnets, subnet_name, expected_output, test_id",
    [
        ({1: "Eden", 2: "Utopia"}, "Eden", 1, "T7"),
        ({1: "Eden", 2: "Utopia"}, "Utopia", 2, "T8"),
        ({1: "Eden", 2: "Utopia"}, "Nowhere", None, "T9"),
    ],
)
def test_get_netuid(subnets, subnet_name, expected_output, test_id):
    # Arrange
    client = MagicMock(spec=CommuneClient)
    client.query_map_subnet_names.return_value = subnets

    # Act
    if expected_output is not None:
        netuid = BaseValidator.get_netuid(client, subnet_name)
        # Assert
        assert netuid == expected_output
    else:
        with pytest.raises(ValueError):
            BaseValidator.get_netuid(client, subnet_name)


# Test for BaseValidator.make_validation_request
@pytest.mark.parametrize(
    "uid, miner_input, module_host, module_port, response_status, response_content, expected_output, test_id",
    [
        (
            1,
            Message(content="test", role="miner"),
            "localhost",
            8080,
            200,
            b"result",
            {1: b"result"},
            "T10",
        ),
        (
            1,
            Message(content="test", role="miner"),
            "localhost",
            8080,
            404,
            b"error",
            {1: b"0x00001"},
            "T11",
        ),
    ],
)
def test_make_validation_request(
    uid,
    miner_input,
    module_host,
    module_port,
    response_status,
    response_content,
    expected_output,
    test_id,
):
    # Arrange
    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = response_status
        mock_response.content = response_content
        mock_post.return_value = mock_response
        validator = BaseValidator(config=config)

        # Act
        result = validator.make_validation_request(
            uid, miner_input, module_host, module_port
        )

        # Assert
        assert result == expected_output
