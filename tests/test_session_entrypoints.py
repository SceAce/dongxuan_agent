import bazi_session
import daliuren_session
from dongxuan_agent.apps.sessions.bazi import main as bazi_main
from dongxuan_agent.apps.sessions.daliuren import main as daliuren_main


def test_root_session_entrypoints_delegate_to_canonical_modules():
    assert bazi_session.main is bazi_main
    assert daliuren_session.main is daliuren_main
