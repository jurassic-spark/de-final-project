from src.hello_world import hello_world

def test_hello_world_returns_hello_world():
    result = hello_world()
    assert result == "hello world"