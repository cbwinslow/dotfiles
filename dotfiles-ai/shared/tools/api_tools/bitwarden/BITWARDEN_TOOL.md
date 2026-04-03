# Bitwarden API Tool

## Overview
Provides secure access to Bitwarden credentials and API keys for AI agents through the Bitwarden CLI.

## Operations

### 1. get_api_key
Retrieve an API key from Bitwarden by name.

**Parameters:**
- `key_name` (string): The name of the API key to retrieve
- `vault_name` (string, optional): The Bitwarden vault name (default: "Personal")

**Returns:**
- `api_key` (string): The API key value
- `metadata` (object): Key metadata including creation date, last used, etc.

**Example:**
```yaml
operation: get_api_key
key_name: "OpenAI API Key"
vault_name: "Work Vault"
```

### 2. populate_env_file
Populate a .env file with credentials from Bitwarden.

**Parameters:**
- `env_file_path` (string): Path to the .env file to populate
- `credentials` (array): Array of credential objects with name and vault

**Returns:**
- `success` (boolean): Whether the operation succeeded
- `updated_keys` (array): List of keys that were updated

**Example:**
```yaml
operation: populate_env_file
env_file_path: "/home/cbwinslow/project/.env"
credentials:
  - name: "OpenAI API Key"
    vault: "Personal"
  - name: "Database Password"
    vault: "Work Vault"
```

### 3. list_vaults
List all available Bitwarden vaults.

**Parameters:**
- `include_folders` (boolean, optional): Include folder structure (default: false)

**Returns:**
- `vaults` (array): List of vault names
- `folders` (array, optional): Folder structure if requested

**Example:**
```yaml
operation: list_vaults
include_folders: true
```

### 4. search_credentials
Search for credentials by name or tag.

**Parameters:**
- `query` (string): Search query
- `search_type` (string, optional): "name", "tag", or "all" (default: "all")

**Returns:**
- `results` (array): Matching credentials with metadata
- `total_count` (number): Total number of matches

**Example:**
```yaml
operation: search_credentials
query: "api"
search_type: "tag"
```

## Configuration

### Environment Variables
```bash
# Bitwarden CLI configuration
BW_CLIENT_ID=your-client-id
BW_CLIENT_SECRET=your-client-secret
BW_PASSWORD=your-master-password
BW_SESSION=your-session-token
```

### Required Tools
- `bw` (Bitwarden CLI) - https://bitwarden.com/download/
- `python3` with `requests` library

## Security Considerations

1. **Session Management**: Use BW_SESSION for authenticated operations
2. **Vault Access**: Only access authorized vaults
3. **Key Storage**: Never store API keys in plain text
4. **Audit Trail**: Log all credential access attempts

## Error Handling

### Common Errors
- **Authentication Failed**: Check BW_SESSION and credentials
- **Vault Not Found**: Verify vault name exists
- **Permission Denied**: Check vault access permissions
- **Network Issues**: Verify Bitwarden service availability

### Error Codes
- `AUTH_001`: Authentication failed
- `VAULT_002`: Vault not found
- `PERM_003`: Permission denied
- `NET_004`: Network connectivity issue
- `KEY_005`: Key not found

## Examples

### Basic Usage
```yaml
# Get OpenAI API key
operation: get_api_key
key_name: "OpenAI API Key"
vault_name: "Personal"
```

### Environment File Population
```yaml
# Populate .env file
operation: populate_env_file
env_file_path: "/home/cbwinslow/project/.env"
credentials:
  - name: "OpenAI API Key"
    vault: "Personal"
  - name: "Database Password"
    vault: "Work Vault"
```

### Credential Search
```yaml
# Search for API-related credentials
operation: search_credentials
query: "api"
search_type: "tag"
```

## Integration Examples

### LangChain Integration
```python
from langchain.tools import Tool
from bitwarden_tool import BitwardenClient

class BitwardenTool(Tool):
    def __init__(self, client: BitwardenClient):
        self.client = client
    
    def _run(self, key_name: str) -> str:
        """Get API key from Bitwarden"""
        return self.client.get_api_key(key_name)
    
    def _arun(self, *args, **kwargs):
        return self._run(*args, **kwargs)
```

### CrewAI Integration
```python
from crewai import Agent
from bitwarden_tool import BitwardenClient

class BitwardenAgent(Agent):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        self.bitwarden = BitwardenClient()
    
    def get_api_credentials(self, service_name: str) -> dict:
        """Get credentials for a specific service"""
        return self.bitwarden.search_credentials(service_name)
```

## Dependencies

### Python Packages
- `requests` - HTTP requests
- `python-dotenv` - .env file handling
- `pyyaml` - YAML configuration

### System Tools
- `bw` - Bitwarden CLI
- `openssl` - Encryption utilities

## Testing

### Unit Tests
```python
import unittest
from bitwarden_tool import BitwardenClient

class TestBitwardenTool(unittest.TestCase):
    def setUp(self):
        self.client = BitwardenClient()
    
    def test_get_api_key(self):
        key = self.client.get_api_key("Test Key")
        self.assertIsNotNone(key)
    
    def test_populate_env_file(self):
        result = self.client.populate_env_file("/tmp/test.env", ["Test Key"])
        self.assertTrue(result["success"])
```

### Integration Tests
```python
import pytest
from bitwarden_tool import BitwardenClient

@pytest.fixture
def bitwarden_client():
    return BitwardenClient()

def test_full_workflow(bitwarden_client):
    # Test complete workflow
    key = bitwarden_client.get_api_key("Test Key")
    result = bitwarden_client.populate_env_file("/tmp/test.env", ["Test Key"])
    assert result["success"]
```

## Performance Considerations

- **Caching**: Cache frequently accessed keys
- **Batching**: Batch multiple credential requests
- **Connection Pooling**: Reuse Bitwarden CLI connections
- **Async Operations**: Use async for multiple requests

## Logging

```python
import logging

logger = logging.getLogger("bitwarden_tool")

# Log levels
logger.debug("Debug information")
logger.info("Operation completed")
logger.warning("Potential issue detected")
logger.error("Error occurred")
```

## Version History

### v1.0.0
- Initial release with core operations
- Basic error handling
- Simple configuration

### v1.1.0 (Planned)
- Async support
- Enhanced caching
- Advanced search capabilities
- Multi-vault support

## Support

- **Documentation**: See docs/bitwarden_integration.md
- **Examples**: See examples/bitwarden_usage/
- **Issues**: Create issue in GitHub repository
- **Community**: Join Discord channel for support

## License

MIT License - see LICENSE file for details.