try:
    VERSION = __import__('pkg_resources').get_distribution('sentry-unfuddle').version
except Exception, e:
    VERSION = "unknown"
