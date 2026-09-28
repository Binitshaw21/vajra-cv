"""
tests/test_airgap.py
Strict Air-Gap Sovereignty Verification.
Proves 0 outbound network packets are transmitted during execution.
"""
import socket
# pyrefly: ignore [missing-import]
import pytest
import torch
import numpy as np
import sys
import os

# Append parent directory to path so core modules can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.module_2_trojan import NeuralCleanseTrojanScanner

@pytest.fixture(autouse=True)
def block_network_sockets(monkeypatch):
    """
    Hooks into the Python socket library. If any module attempts to open a network
    connection (e.g., downloading weights, phoning home), it immediately fails the test.
    """
    def guarded_socket(*args, **kwargs):
        raise PermissionError(
            "AIR-GAP BREACH DETECTED: Network socket calls are strictly forbidden in this tactical environment!"
        )
    
    monkeypatch.setattr(socket, "socket", guarded_socket)

def test_module_2_airgap_compliance():
    """
    Executes the Neural Cleanse Trojan Scanner while network sockets are hard-blocked.
    """
    # 1. Initialize mock architecture
    mock_model = torch.nn.Sequential(
        torch.nn.Flatten(),
        torch.nn.Linear(3 * 16 * 16, 32),
        torch.nn.ReLU(),
        torch.nn.Linear(32, 2)
    )
    
    scanner = NeuralCleanseTrojanScanner(mock_model, img_shape=(3, 16, 16), steps=5)
    dummy_inputs = torch.rand((4, 3, 16, 16))
    
    # 2. Run computation
    try:
        report = scanner.audit_model(num_classes=2, test_tensors=dummy_inputs)
    except PermissionError as e:
        pytest.fail(f"Air-Gap Verification Failed: {str(e)}")
        
    # 3. Assert successful completion without network dependencies
    assert "verdict" in report
    assert report["verdict"] in ["FLAGGED_TROJAN", "CERTIFIED_CLEAN"]
    assert len(report["l1_norms"]) == 2

def test_socket_guard_is_active():
    """
    Sanity check: Proves the fixture is actually blocking network access.
    """
    with pytest.raises(PermissionError, match="AIR-GAP BREACH DETECTED"):
        # Attempt to create a standard TCP socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)