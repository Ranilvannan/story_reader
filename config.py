class Config(object):
    DEBUG = False
    TESTING = False


class ProductionConfig(Config):
    MONGO_URI = "mongodb://localhost:27017/story_book"
    MONGO_DATABASE = "story_book"

    IMPORT_PATH = "/var/story_book"
    CUSTOM_IMAGES_PATH = "/var/story_book/images"

    MONGO_CATEGORY_TABLE = "category"
    MONGO_GALLERY_TABLE = "gallery"


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True