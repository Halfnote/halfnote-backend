from django.core.files.storage import Storage
import cloudinary.uploader
import cloudinary.api
import cloudinary.utils
import uuid
import os
from django.conf import settings

class SimpleCloudinaryStorage(Storage):
    """
    Custom Cloudinary storage that bypasses django-cloudinary-storage 
    and uses cloudinary library directly to avoid signature issues
    """
    
    def _save(self, name, content):
        """Upload file directly to Cloudinary"""
        # Generate a simple unique filename
        file_extension = name.split('.')[-1] if '.' in name else 'jpg'
        unique_name = f"banner_{uuid.uuid4().hex[:8]}"
        
        # Configure cloudinary if not already done
        if not hasattr(cloudinary.config(), 'cloud_name') or not cloudinary.config().cloud_name:
            cloudinary.config(
                cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
                api_key=os.getenv('CLOUDINARY_API_KEY'),
                api_secret=os.getenv('CLOUDINARY_API_SECRET')
            )
        
        # Upload with absolute minimal parameters
        try:
            response = cloudinary.uploader.upload(
                content,
                public_id=unique_name,
                resource_type='auto'
            )
            return response['public_id']
        except Exception as e:
            print(f"Cloudinary upload error: {e}")
            raise
    
    def _open(self, name, mode='rb'):
        """Not implemented - we don't need to read files"""
        raise NotImplementedError("Reading files is not supported")
    
    def delete(self, name):
        """Delete file from Cloudinary"""
        try:
            cloudinary.uploader.destroy(name)
        except Exception as e:
            print(f"Error deleting from Cloudinary: {e}")
    
    def exists(self, name):
        """Check if file exists in Cloudinary"""
        try:
            cloudinary.api.resource(name)
            return True
        except:
            return False
    
    def url(self, name):
        """Get URL for the file"""
        if not name:
            return None
        return cloudinary.utils.cloudinary_url(name)[0]
    
    def size(self, name):
        """Get file size"""
        try:
            resource = cloudinary.api.resource(name)
            return resource.get('bytes', 0)
        except:
            return 0 