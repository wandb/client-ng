"""Sweep tests"""
import wandb
import json


def test_create_sweep(live_mock_server, test_settings):
    live_mock_server.set_ctx({"resume": True})
    sweep_config = {
        "name": "My Sweep",
        "method": "grid",
        "parameters": {
                "parameter1": {
                    "values": [1, 2, 3]
                }
            }
    }
    sweep_id = wandb.sweep(sweep_config)
    assert sweep_id == 'test'


def test_agent(live_mock_server, dummy_api_key):
    def train():
        # Here we're in a different process. It's hard to communicate
        # back to the main process for assertions.

        # Fuck. I can't get this thing to get the SWEEP_ID that's set
        # by the agent

        settings = wandb.Settings(
            base_url="http://localhost",
            api_key=dummy_api_key)
        
        open('/tmp/settings.txt', 'w').write(json.dumps(dict(settings)))
        run = wandb.init(settings=settings)
        print('RUN SWEEP_ID', run.sweep_id)
        # If this assertion fails, the test will timeout (because we
        # never complete 1 agent run)
        import json
        import os
        open('/tmp/sweep.txt', 'w').write(json.dumps(run.sweep_id))
        open('/tmp/env.txt', 'w').write(json.dumps(dict(os.environ)))
        # assert run.sweep_id == ''
    wandb.agent('test-sweep-id', function=train, count=1)
