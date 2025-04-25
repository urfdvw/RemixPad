def run_tests(test_class, *args, **kwargs):
    test_instance = test_class(*args, **kwargs)
    passed = []
    failed = []

    for attr in dir(test_instance):
        if attr.startswith("test_") and callable(getattr(test_instance, attr)):
            test_func = getattr(test_instance, attr)
            try:
                test_func()
                passed.append(attr)
            except AssertionError as e:
                failed.append((attr, str(e)))
            except Exception as e:
                failed.append((attr, f"Exception: {e}"))

    print("\n\n# Test Report: ", test_class.__name__, *args, **kwargs)
    if passed:
        print("\n## Passed Tests:")
    for name in passed:
        print(f"✅ {name}")
        
    if failed:
        print("\n## Failed Tests:")
    for name, reason in failed:
        print(f"❌ {name} - {reason}")

class TestExample:
    def test_addition(self):
        assert 1 + 1 == 2

    def test_subtraction(self):
        assert 5 - 3 == 1  # will fail

    def test_error(self):
        raise ValueError("Unexpected error")  # will also be caught