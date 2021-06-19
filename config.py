class Config(object):
    DEBUG = False
    TESTING = False


class ProductionConfig(Config):
    MONGO_URI = "mongodb://localhost:27017/tamil_book"
    MONGO_DATABASE = "tamil_book"
    BLOG_CODE = "Tamil"
    IMPORT_PATH = "/var/tamil_book/"
    CUSTOM_STATIC_PATH = "/var/tamil_book/images/"
    TEMPLATE_FOLDER_PATH = "test"
    MONGO_BLOG_TABLE = "blog"
    MONGO_CATEGORY_TABLE = "category"
    MONGO_GALLERY_TABLE = "gallery"


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True