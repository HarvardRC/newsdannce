import uuid

def make_resource_name(prefix: str = '', extension='') -> str:
  """Generate a random (unique) UUID for a resource folder or file name"""
  return f"{prefix}{uuid.uuid4().hex}{extension}"
