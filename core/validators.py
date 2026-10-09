from django.core.exceptions import ValidationError

ALLOVED_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'webp']

def validate_images_size(file, max_mb: int = 5) -> None:
    limit_bytes = max_mb * 1024 * 1024
    if file.size > limit_bytes:
        raise ValidationError(f'Размер файла не должен превышать {max_mb} МБ')
    