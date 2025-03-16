# middleware.py
from django.utils.deprecation import MiddlewareMixin
from additions.models import MetaTag

class MetaTagsMiddleware(MiddlewareMixin):
    def process_request(self, request):
        try:
            meta_tag = MetaTag.objects.get(url=request.path)

            request.meta_title = meta_tag.title
            request.meta_description = meta_tag.description
            request.meta_og_title = meta_tag.og_title
            request.meta_og_description = meta_tag.og_description
            request.meta_og_image = meta_tag.og_image
        except MetaTag.DoesNotExist:
            request.meta_title = "Заголовок по умолчанию"
            request.meta_description = "Описание по умолчанию"
            request.meta_og_title = "Описание по умолчанию"
            request.meta_og_description = "Описание по умолчанию"
            request.meta_og_image = "Описание по умолчанию"