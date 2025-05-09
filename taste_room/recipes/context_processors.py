from django.template.loader import render_to_string


def empty_block(request):
    return {
        'empty_block': render_to_string('additions/empty_block.html'),
    }