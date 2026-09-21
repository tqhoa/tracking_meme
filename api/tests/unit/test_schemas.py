import pytest
from pydantic import ValidationError

from app.schemas.token import TokenSearchRequest


def test_valid_address_lowercased() -> None:
    req = TokenSearchRequest(address="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")
    assert req.address == "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"


def test_valid_address_with_chain() -> None:
    req = TokenSearchRequest(address="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", chain="eth")
    assert req.chain == "eth"


def test_invalid_address_too_short() -> None:
    with pytest.raises(ValidationError):
        TokenSearchRequest(address="0x8FB3c6B7")


def test_invalid_address_no_prefix() -> None:
    with pytest.raises(ValidationError):
        TokenSearchRequest(address="A0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")


def test_invalid_address_wrong_chars() -> None:
    with pytest.raises(ValidationError):
        TokenSearchRequest(address="0xZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ")


def test_chain_defaults_to_none() -> None:
    req = TokenSearchRequest(address="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")
    assert req.chain is None
