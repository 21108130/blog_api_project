from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json

from .models import BlogPost
from .serializers import BlogPostSerializer


def error_response(message, status=400):
    return JsonResponse({"error": message}, status=status)


def success_response(data, status=200):
    return JsonResponse(data, status=status, safe=isinstance(data, dict))


@method_decorator(csrf_exempt, name='dispatch')
class BlogPostListView(View):
    """
    GET  /api/posts/  - List all blog posts
    POST /api/posts/  - Create a new blog post
    """

    async def get(self, request):
        posts = []
        async for post in BlogPost.objects.all():
            serializer = BlogPostSerializer(post)
            posts.append(serializer.data)
        return JsonResponse(posts, safe=False, status=200)

    async def post(self, request):
        try:
            body = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return error_response("Invalid JSON body.", status=400)

        serializer = BlogPostSerializer(data=body)
        if not serializer.is_valid():
            return JsonResponse({"errors": serializer.errors}, status=400)

        post = await BlogPost.objects.acreate(**serializer.validated_data)
        return JsonResponse(BlogPostSerializer(post).data, status=201)


@method_decorator(csrf_exempt, name='dispatch')
class BlogPostDetailView(View):
    """
    GET    /api/posts/<id>/  - Retrieve a blog post
    PUT    /api/posts/<id>/  - Update a blog post
    DELETE /api/posts/<id>/  - Delete a blog post
    """

    async def _get_post(self, pk):
        try:
            return await BlogPost.objects.aget(pk=pk)
        except BlogPost.DoesNotExist:
            return None

    async def get(self, request, pk):
        post = await self._get_post(pk)
        if post is None:
            return error_response(f"BlogPost with id={pk} not found.", status=404)
        return JsonResponse(BlogPostSerializer(post).data, status=200)

    async def put(self, request, pk):
        post = await self._get_post(pk)
        if post is None:
            return error_response(f"BlogPost with id={pk} not found.", status=404)

        try:
            body = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return error_response("Invalid JSON body.", status=400)

        serializer = BlogPostSerializer(post, data=body)
        if not serializer.is_valid():
            return JsonResponse({"errors": serializer.errors}, status=400)

        for attr, value in serializer.validated_data.items():
            setattr(post, attr, value)
        await post.asave()

        return JsonResponse(BlogPostSerializer(post).data, status=200)

    async def delete(self, request, pk):
        post = await self._get_post(pk)
        if post is None:
            return error_response(f"BlogPost with id={pk} not found.", status=404)

        await post.adelete()
        return JsonResponse({"message": f"BlogPost with id={pk} deleted successfully."}, status=200)
