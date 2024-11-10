from typing import Any
from django.core.validators import BaseValidator
from django.core.files.uploadedfile import UploadedFile
from django.core.exceptions import ValidationError
from common.utils import format_file_size
from django.utils.translation import gettext_lazy as _

class FileExtensionValidator(BaseValidator):
    def compare(self, a: Any, b: Any) -> bool:
        return False
    
    def clean(self, value: UploadedFile) -> Any:
        allowed_extensions = self.limit_value
        extension = value.name.split('.')[-1].lower()
        if extension not in allowed_extensions:
            raise ValidationError(_("Only {allowed_extensions} files are allowed.").format(allowed_extensions= _(' or ').join(allowed_extensions)))
        return value
        
class LimitedFileSizeValidator(BaseValidator):
    def compare(self, a: Any, b: Any) -> bool:
        return False
    def clean(self, value: UploadedFile) -> Any:
        max_size = self.limit_value
        
        if value.size > max_size:
            raise ValidationError(_("File size can't be bigger than {max_size}").format(max_size= format_file_size(max_size)))
        return value