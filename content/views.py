from .models import Lookbook
from django.shortcuts import render, get_object_or_404


def lookbook_index(request):
    lookbooks = Lookbook.objects.all()
    return render(request, "content/lookbook_index.html", {
        "lookbooks": lookbooks
    })
def lookbook_detail(request, slug):
    lookbook = get_object_or_404(
        Lookbook.objects.prefetch_related("images"),
        slug=slug
    )

    # 🔥 Спец-шаблон для Penn & Ink
    if lookbook.slug == "penn_ink_winter_imited_2025":
        template_name = "content/pennandink_winter_imited_2025_lookbook.html"
    else:
        template_name = "content/lookbook_detail.html"

    return render(request, template_name, {
        "lookbook": lookbook
    })
