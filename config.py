class Config(object):
    MERCHANT_ID='bghrebe563458'


class ProductionConfig(Config):
    MERCHANT_ID='&^GYG4dyyrw'
    DATABASE_URI=''
    MAIL_SERVER='smtp.gmail.com'
    MAIL_PORT=465
    MAIL_USERNAME='' 
    MAIL_PASSWORD=''
    MAIL_USE_SSL=True


class DevelopmentConfig(Config):
    MERCHANT_ID='hjerebge'
    DATABASE_URI=''



    
















