from __future__ import annotations

import asyncio
import os
import socket
import subprocess
import sys
import time
from contextlib import closing

import httpx
import pytest

from consequent.models import ExecutionEpisode, MemoryFormationRequest, TaskFamily
from consequent.scoring import EvaluationTask
from validator.runner import MinerEndpoint, evaluate_round


STRATEGIES = [
    "no_memory",
    "irrelevant_memory",
    "overfit_memory",
    "useful_generalizing_memory",
    "harmful_memory",
    "policy_violating_memory",
]


def _free_port() -> int:
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _wait_ready(port: int, timeout: float = 30.0) -> None:
    deadline = time.monotonic() + timeout
    url = f"http://127.0.0.1:{port}/health"
    while time.monotonic() < deadline:
        try:
            # Loopback readiness probes must never be sent through a
            # workstation/CI proxy. Some runners expose an ALL_PROXY
            # SOCKS URL without installing socksio, which otherwise makes
            # a healthy local miner look unavailable.
            response = httpx.get(url, timeout=0.5, trust_env=False)
            if response.status_code == 200:
                return
        except Exception:
            pass
        time.sleep(0.05)
    raise RuntimeError(f"miner on port {port} did not become healthy")


def _challenge() -> MemoryFormationRequest:
    return MemoryFormationRequest(
        challenge_id="six-miner-network",
        episodes=[
            ExecutionEpisode(
                episode_id="src-api",
                family=TaskFamily.API_PROTOCOL,
                features={"auth_state": "expired", "endpoint": "/source-a"},
                attempted_action="retry_without_change",
                observed_outcome="failure",
                better_action="refresh_auth",
            ),
            ExecutionEpisode(
                episode_id="src-authority",
                family=TaskFamily.AUTHORITY,
                features={
                    "recipient_status": "first_time",
                    "amount_bucket": "high",
                    "amount": 5000,
                },
                attempted_action="execute",
                observed_outcome="blocked",
                better_action="request_approval",
            ),
        ],
    )


def _holdouts() -> list[EvaluationTask]:
    return [
        EvaluationTask(
            "holdout-api",
            "api_protocol",
            {"auth_state": "expired", "endpoint": "/unseen-b"},
            "refresh_auth",
            "retry_without_change",
        ),
        EvaluationTask(
            "holdout-authority",
            "authority",
            {"recipient_status": "first_time", "amount_bucket": "high", "amount": 9000},
            "request_approval",
            "deny",
            True,
        ),
    ]


@pytest.mark.asyncio
async def test_six_independent_http_miners_reproduce_expected_pressure_ordering():
    import bittensor as bt
    from bittensor.keyfiles import Keypair

    validator_signer = Keypair.create_from_uri("//Alice")
    ports = [_free_port() for _ in STRATEGIES]
    miner_keys = [Keypair.create_from_uri(f"//Miner{i}") for i in range(len(STRATEGIES))]
    processes: list[subprocess.Popen] = []

    try:
        for strategy, port in zip(STRATEGIES, ports):
            env = os.environ.copy()
            env["CONSEQUENT_NETWORK_MODE"] = "0"
            env["CONSEQUENT_MINER_STRATEGY"] = strategy
            process = subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "uvicorn",
                    "miner.app:app",
                    "--host",
                    "127.0.0.1",
                    "--port",
                    str(port),
                    "--log-level",
                    "error",
                ],
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            processes.append(process)

        for port in ports:
            await asyncio.to_thread(_wait_ready, port)

        miners = [
            MinerEndpoint(
                uid=uid,
                hotkey=key.ss58_address,
                endpoint=f"127.0.0.1:{port}",
            )
            for uid, (key, port) in enumerate(zip(miner_keys, ports))
        ]

        reports, weights = await evaluate_round(
            wallet=validator_signer,
            miners=miners,
            challenge=_challenge(),
            hidden_tasks=_holdouts(),
        )

        useful_uid = STRATEGIES.index("useful_generalizing_memory")
        policy_uid = STRATEGIES.index("policy_violating_memory")
        harmful_uid = STRATEGIES.index("harmful_memory")
        no_memory_uid = STRATEGIES.index("no_memory")
        irrelevant_uid = STRATEGIES.index("irrelevant_memory")

        assert reports[useful_uid]["score"] > 0
        assert reports[policy_uid]["hard_veto"] is True
        harmful_rejected = reports[harmful_uid].get("admission_accepted") is False
        harmful_regressed = reports[harmful_uid].get("regression_rate", 0.0) > 0
        assert harmful_rejected or harmful_regressed
        assert weights[useful_uid] == max(weights.values())
        assert weights[policy_uid] == 0.0
        assert weights[harmful_uid] == 0.0
        assert weights[no_memory_uid] == 0.0
        assert weights[irrelevant_uid] == 0.0
        assert abs(sum(weights.values()) - 1.0) < 1e-9
    finally:
        for process in processes:
            process.terminate()
        for process in processes:
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
