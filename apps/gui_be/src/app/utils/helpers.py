import uuid
def make_resource_folder_name() -> str:
  return uuid.uuid4().hex
