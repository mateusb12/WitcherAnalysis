from django.urls import URLResolver, URLPattern


def get_all_url_patterns(urlpatterns, prefix=''):
    """
    Returns a list of all URL patterns in a Django application.
    The list includes URL patterns defined in the root urls.py file and in all included urls.py files.
    """
    urls = []
    for pattern in urlpatterns:
        if isinstance(pattern, URLResolver):
            urls += get_all_url_patterns(pattern.url_patterns, prefix + str(pattern.pattern))
        elif isinstance(pattern, URLPattern):
            url = prefix + str(pattern.pattern)
            url = url.replace('^', '/').replace('$', '')
            if len(url.split('/')) == 2 and '(' not in url and ')' not in url:
                urls.append(url)
    return tuple(urls)

