import os
import json
from typing import Optional
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.mgmt.resource import ResourceManagementClient
from mcp.server.fastmcp import FastMCP
import dotenv

# Load environment variables from .env file
dotenv.load_dotenv()

# Setup Azure credentials
subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
if not subscription_id:
    raise ValueError("AZURE_SUBSCRIPTION_ID is not set in environment.")

if all([os.getenv("AZURE_TENANT_ID"), os.getenv("AZURE_CLIENT_ID"), os.getenv("AZURE_CLIENT_SECRET")]):
    credential = ClientSecretCredential(
        tenant_id=os.getenv("AZURE_TENANT_ID"),
        client_id=os.getenv("AZURE_CLIENT_ID"),
        client_secret=os.getenv("AZURE_CLIENT_SECRET")
    )
else:
    credential = DefaultAzureCredential()

# Initialize Resource Management client
resource_client = ResourceManagementClient(credential, subscription_id)

# MCP server setup
mcp = FastMCP(
    name="Azure Resource Group Creator",
    dependencies=[
        "azure-identity",
        "azure-mgmt-resource"
    ]
)

@mcp.tool()
def create_resource_group(name: str, location: str, tags: Optional[str] = None) -> str:
    """
    Create a new Azure Resource Group.

    Args:
        name: Name of the resource group.
        location: Azure region (e.g., 'eastus').
        tags: Optional tags as JSON string.
    """
    try:
        tag_dict = json.loads(tags) if tags else {}

        resource_client.resource_groups.create_or_update(
            resource_group_name=name,
            parameters={
                'location': location,
                'tags': tag_dict
            }
        )

        return f"Resource group '{name}' created successfully in {location}."
    
    except json.JSONDecodeError:
        return "Error: Tags must be valid JSON."
    except Exception as e:
        return f"Failed to create resource group: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio")