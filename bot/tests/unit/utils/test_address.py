import pytest

from app.utils.address import extract_evm_address


@pytest.mark.parametrize(
    "text,expected",
    [
        # exact address
        ("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"),
        # embedded in sentence
        ("Kiểm tra token này: 0x8FB3c6B7bFa1D6dCeF6fB3fBc7e9d1A2b3C4d5E6 nhé", "0x8FB3c6B7bFa1D6dCeF6fB3fBc7e9d1A2b3C4d5E6"),
        # with trailing text
        ("address is 0xdAC17F958D2ee523a2206206994597C13D831ec7 thank you", "0xdAC17F958D2ee523a2206206994597C13D831ec7"),
        # no address
        ("hello world", None),
        # too short (39 hex chars)
        ("0x8FB3c6B7bFa1D6dCeF6fB3fBc7e9d1A2b3C4d5", None),
        # empty
        ("", None),
    ],
)
def test_extract_evm_address(text: str, expected: str | None) -> None:
    assert extract_evm_address(text) == expected
