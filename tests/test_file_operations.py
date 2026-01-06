import tempfile
import os
from copy-photo.file_operations import _contains_photos

def test_contains_photos():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Создаем тестовый файл
        test_file = os.path.join(tmpdir, "test.jpg")
        with open(test_file, 'w') as f:
            f.write("test")

        assert _contains_photos(tmpdir, ('.jpg', '.jpeg')) == True
        assert _contains_photos(tmpdir, ('.png', '.gif')) == False
