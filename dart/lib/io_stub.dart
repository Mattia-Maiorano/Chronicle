// Stub for non-IO platforms
class _StubStdout {
  void write(Object? object) {
    print(object);
  }
}

final stdout = _StubStdout();
