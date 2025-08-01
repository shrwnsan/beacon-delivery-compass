"""Configuration for pytest and hypothesis."""

from hypothesis import settings, HealthCheck

# Define a 'dev' profile for faster local testing
# This profile runs fewer examples per test.
settings.register_profile(
    "dev",
    max_examples=10,
    suppress_health_check=[HealthCheck.too_slow]
)

# Define a 'ci' profile for more thorough testing in CI environments
# This runs the default number of examples.
settings.register_profile(
    "ci",
    max_examples=100  # Default number of examples
)

# Load the 'dev' profile by default when running tests locally
settings.load_profile("dev")
