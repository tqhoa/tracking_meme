import re

_EVM_ADDRESS_RE = re.compile(r"0x[0-9a-fA-F]{40}\b")


def extract_evm_address(text: str) -> str | None:
    match = _EVM_ADDRESS_RE.search(text)
    return match.group(0) if match else None
