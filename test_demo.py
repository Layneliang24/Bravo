# Test file for demonstrating pre-commit hooks


def test_function():
    # TODO: This is a test comment
    # FIXME: This needs to be fixed
    # HACK: This is a temporary solution
    password = "hardcoded_password_123"  # This should trigger security warnings

    # Some code with potential issues
    x = 1 + 2  # Missing spaces around operators
    if x == 3:  # Missing spaces
        print("Hello World")

    return x


# XXX: This is another marker
if __name__ == "__main__":
    test_function()
