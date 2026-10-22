from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.http import Http404
from .models import Category, Post, Tag


def post_list_view(request):
    """
    Paginated blog articles list with search and filtering by category or tag.
    """
    search_query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category", "").strip()
    tag_slug = request.GET.get("tag", "").strip()

    posts = Post.objects.published().select_related("category", "author").prefetch_related("tags")

    selected_category = None
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        posts = posts.filter(category=selected_category)

    selected_tag = None
    if tag_slug:
        selected_tag = get_object_or_404(Tag, slug=tag_slug)
        posts = posts.filter(tags=selected_tag)

    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query)
            | Q(excerpt__icontains=search_query)
            | Q(content_markdown__icontains=search_query)
        )

    paginator = Paginator(posts, 6) # 6 articles per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()
    popular_tags = Tag.objects.all()[:12]

    context = {
        "page_obj": page_obj,
        "search_query": search_query,
        "selected_category": selected_category,
        "selected_tag": selected_tag,
        "categories": categories,
        "popular_tags": popular_tags,
    }
    return render(request, "blog/post_list.html", context)


def post_detail_view(request, slug):
    """
    Optimized reading page with sanitized Markdown rendering, estimated reading time,
    navigation between articles and related posts.
    """
    # Allow staff to preview unpublished drafts
    if request.user.is_staff:
        post = get_object_or_404(Post, slug=slug)
    else:
        post = get_object_or_404(Post.objects.published(), slug=slug)

    # Increment view count safely
    Post.objects.filter(pk=post.pk).update(views_count=post.views_count + 1)

    # Next and Previous posts
    prev_post = Post.objects.published().filter(published_at__lt=post.published_at).order_by("-published_at").first()
    next_post = Post.objects.published().filter(published_at__gt=post.published_at).order_by("published_at").first()

    # Related posts by category
    related_posts = []
    if post.category:
        related_posts = Post.objects.published().filter(category=post.category).exclude(id=post.id)[:3]

    rendered_content = post.render_markdown()

    context = {
        "post": post,
        "rendered_content": rendered_content,
        "prev_post": prev_post,
        "next_post": next_post,
        "related_posts": related_posts,
    }
    return render(request, "blog/post_detail.html", context)


def category_detail_view(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.published().filter(category=category).select_related("author")
    paginator = Paginator(posts, 6)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "blog/post_list.html", {
        "page_obj": page_obj,
        "selected_category": category,
        "categories": Category.objects.all(),
        "popular_tags": Tag.objects.all()[:12],
    })


def tag_detail_view(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    posts = Post.objects.published().filter(tags=tag).select_related("author", "category")
    paginator = Paginator(posts, 6)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "blog/post_list.html", {
        "page_obj": page_obj,
        "selected_tag": tag,
        "categories": Category.objects.all(),
        "popular_tags": Tag.objects.all()[:12],
    })
