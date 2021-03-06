from my_django.contrib.sites.models import get_current_site
from my_django.core import urlresolvers
from my_django.core.paginator import EmptyPage, PageNotAnInteger
from my_django.http import Http404
from my_django.template.response import TemplateResponse

def index(request, sitemaps,
          template_name='sitemap_index.xml', mimetype='application/xml',
          sitemap_url_name='my_django.contrib.sitemaps.views.sitemap'):
    req_protocol = 'https' if request.is_secure() else 'http'
    req_site = get_current_site(request)

    sites = []
    for section, site in sitemaps.items():
        if callable(site):
            site = site()
        protocol = req_protocol if site.protocol is None else site.protocol
        sitemap_url = urlresolvers.reverse(
                sitemap_url_name, kwargs={'section': section})
        absolute_url = '%s://%s%s' % (protocol, req_site.domain, sitemap_url)
        sites.append(absolute_url)
        for page in range(2, site.paginator.num_pages + 1):
            sites.append('%s?p=%s' % (absolute_url, page))

    return TemplateResponse(request, template_name, {'sitemaps': sites},
                            content_type=mimetype)

def sitemap(request, sitemaps, section=None,
            template_name='sitemap.xml', mimetype='application/xml'):
    req_protocol = 'https' if request.is_secure() else 'http'
    req_site = get_current_site(request)

    if section is not None:
        if section not in sitemaps:
            raise Http404("No sitemap available for section: %r" % section)
        maps = [sitemaps[section]]
    else:
        maps = sitemaps.values()
    page = request.GET.get("p", 1)

    urls = []
    for site in maps:
        try:
            if callable(site):
                site = site()
            urls.extend(site.get_urls(page=page, site=req_site,
                                      protocol=req_protocol))
        except EmptyPage:
            raise Http404("Page %s empty" % page)
        except PageNotAnInteger:
            raise Http404("No page '%s'" % page)
    return TemplateResponse(request, template_name, {'urlset': urls},
                            content_type=mimetype)
