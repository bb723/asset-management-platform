"""
Azure Blob Storage helper for document management
"""
import os
import logging
from datetime import datetime, timedelta
from typing import Optional, BinaryIO
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, generate_blob_sas, BlobSasPermissions

logger = logging.getLogger(__name__)


class AzureStorageHelper:
    """Helper class for Azure Blob Storage operations"""

    def __init__(self):
        """Initialize Azure Blob Storage client"""
        self.use_azure = os.getenv('USE_AZURE_STORAGE', 'false').lower() == 'true'

        if self.use_azure:
            connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
            if not connection_string:
                logger.warning("Azure Storage connection string not found. Falling back to local storage.")
                self.use_azure = False
            else:
                try:
                    self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
                    self.account_name = os.getenv('AZURE_STORAGE_ACCOUNT_NAME')
                    self.account_key = os.getenv('AZURE_STORAGE_ACCOUNT_KEY')
                    self.entity_container = os.getenv('AZURE_ENTITY_DOCUMENTS_CONTAINER', 'entity-documents')
                    self.building_container = os.getenv('AZURE_BUILDING_DOCUMENTS_CONTAINER', 'building-documents')

                    # Ensure containers exist
                    self._ensure_containers_exist()
                    logger.info("Azure Blob Storage initialized successfully")
                except Exception as e:
                    logger.error(f"Failed to initialize Azure Blob Storage: {e}")
                    self.use_azure = False

        if not self.use_azure:
            logger.info("Using local file storage")
            self.upload_folder = os.getenv('UPLOAD_FOLDER', './uploads')
            os.makedirs(self.upload_folder, exist_ok=True)

    def _ensure_containers_exist(self):
        """Create containers if they don't exist"""
        try:
            # Create entity documents container
            try:
                self.blob_service_client.create_container(self.entity_container)
                logger.info(f"Created container: {self.entity_container}")
            except Exception:
                pass  # Container already exists

            # Create building documents container
            try:
                self.blob_service_client.create_container(self.building_container)
                logger.info(f"Created container: {self.building_container}")
            except Exception:
                pass  # Container already exists
        except Exception as e:
            logger.error(f"Error ensuring containers exist: {e}")

    def upload_entity_document(self, entity_id: str, filename: str, file_stream: BinaryIO) -> str:
        """
        Upload an entity document

        Args:
            entity_id: Entity ID
            filename: Original filename
            file_stream: File-like object to upload

        Returns:
            Blob path/URL for storage in database
        """
        if self.use_azure:
            blob_name = f"{entity_id}/{filename}"
            blob_client = self.blob_service_client.get_blob_client(
                container=self.entity_container,
                blob=blob_name
            )

            try:
                # Reset stream position to beginning
                file_stream.seek(0)
                blob_client.upload_blob(file_stream, overwrite=True)
                logger.info(f"Uploaded entity document to Azure: {blob_name}")
                return blob_name
            except Exception as e:
                logger.error(f"Failed to upload to Azure Blob Storage: {e}")
                raise
        else:
            # Local storage fallback
            entity_folder = os.path.join(self.upload_folder, 'entities', entity_id)
            os.makedirs(entity_folder, exist_ok=True)
            file_path = os.path.join(entity_folder, filename)

            file_stream.seek(0)
            with open(file_path, 'wb') as f:
                f.write(file_stream.read())

            logger.info(f"Uploaded entity document locally: {file_path}")
            return file_path

    def upload_building_document(self, building_id: str, filename: str, file_stream: BinaryIO) -> str:
        """
        Upload a building document

        Args:
            building_id: Building ID
            filename: Original filename
            file_stream: File-like object to upload

        Returns:
            Blob path/URL for storage in database
        """
        if self.use_azure:
            blob_name = f"{building_id}/{filename}"
            blob_client = self.blob_service_client.get_blob_client(
                container=self.building_container,
                blob=blob_name
            )

            try:
                file_stream.seek(0)
                blob_client.upload_blob(file_stream, overwrite=True)
                logger.info(f"Uploaded building document to Azure: {blob_name}")
                return blob_name
            except Exception as e:
                logger.error(f"Failed to upload to Azure Blob Storage: {e}")
                raise
        else:
            # Local storage fallback
            building_folder = os.path.join(self.upload_folder, building_id)
            os.makedirs(building_folder, exist_ok=True)
            file_path = os.path.join(building_folder, filename)

            file_stream.seek(0)
            with open(file_path, 'wb') as f:
                f.write(file_stream.read())

            logger.info(f"Uploaded building document locally: {file_path}")
            return file_path

    def get_download_url(self, blob_path: str, container: str, expiry_hours: int = 1) -> str:
        """
        Get a time-limited SAS URL for downloading a document

        Args:
            blob_path: Path to blob (or local file path)
            container: Container name ('entity-documents' or 'building-documents')
            expiry_hours: How many hours the URL should be valid (default: 1)

        Returns:
            Download URL (SAS URL for Azure, or blob_path for local)
        """
        if self.use_azure:
            try:
                sas_token = generate_blob_sas(
                    account_name=self.account_name,
                    container_name=container,
                    blob_name=blob_path,
                    account_key=self.account_key,
                    permission=BlobSasPermissions(read=True),
                    expiry=datetime.utcnow() + timedelta(hours=expiry_hours)
                )

                blob_url = f"https://{self.account_name}.blob.core.windows.net/{container}/{blob_path}?{sas_token}"
                return blob_url
            except Exception as e:
                logger.error(f"Failed to generate SAS URL: {e}")
                raise
        else:
            # For local storage, return the file path
            return blob_path

    def download_blob(self, blob_path: str, container: str) -> bytes:
        """
        Download blob content as bytes

        Args:
            blob_path: Path to blob (or local file path)
            container: Container name

        Returns:
            File content as bytes
        """
        if self.use_azure:
            blob_client = self.blob_service_client.get_blob_client(
                container=container,
                blob=blob_path
            )

            try:
                return blob_client.download_blob().readall()
            except Exception as e:
                logger.error(f"Failed to download from Azure: {e}")
                raise
        else:
            # Local storage
            with open(blob_path, 'rb') as f:
                return f.read()

    def delete_entity_document(self, blob_path: str) -> bool:
        """
        Delete an entity document

        Args:
            blob_path: Path to blob (or local file path)

        Returns:
            True if successful, False otherwise
        """
        if self.use_azure:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.entity_container,
                blob=blob_path
            )

            try:
                blob_client.delete_blob()
                logger.info(f"Deleted entity document from Azure: {blob_path}")
                return True
            except Exception as e:
                logger.error(f"Failed to delete from Azure: {e}")
                return False
        else:
            # Local storage
            try:
                if os.path.exists(blob_path):
                    os.remove(blob_path)
                    logger.info(f"Deleted entity document locally: {blob_path}")
                    return True
                return False
            except Exception as e:
                logger.error(f"Failed to delete local file: {e}")
                return False

    def delete_building_document(self, blob_path: str) -> bool:
        """
        Delete a building document

        Args:
            blob_path: Path to blob (or local file path)

        Returns:
            True if successful, False otherwise
        """
        if self.use_azure:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.building_container,
                blob=blob_path
            )

            try:
                blob_client.delete_blob()
                logger.info(f"Deleted building document from Azure: {blob_path}")
                return True
            except Exception as e:
                logger.error(f"Failed to delete from Azure: {e}")
                return False
        else:
            # Local storage
            try:
                if os.path.exists(blob_path):
                    os.remove(blob_path)
                    logger.info(f"Deleted building document locally: {blob_path}")
                    return True
                return False
            except Exception as e:
                logger.error(f"Failed to delete local file: {e}")
                return False

    def blob_exists(self, blob_path: str, container: str) -> bool:
        """
        Check if a blob exists

        Args:
            blob_path: Path to blob (or local file path)
            container: Container name

        Returns:
            True if exists, False otherwise
        """
        if self.use_azure:
            blob_client = self.blob_service_client.get_blob_client(
                container=container,
                blob=blob_path
            )
            return blob_client.exists()
        else:
            return os.path.exists(blob_path)


# Global instance
azure_storage = AzureStorageHelper()
