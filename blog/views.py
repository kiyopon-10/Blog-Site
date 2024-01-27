from typing import Any, Dict
from django.db.models.query import QuerySet
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.views.generic import ListView, DetailView
from django.views import View

from .models import Post
from .forms import CommentForm

# Create your views here.

#-----------------------------------------------------------------------------------------------------------------------

# functional view

def starting_page(request):
    latest_posts = Post.objects.all().order_by("-date")[:3]
    return render(request, "blog/index.html", {
        "posts": latest_posts
    })
    
# class-based view

class Starting_Page_View(ListView):
    template_name = "blog/index.html"
    model = Post
    
    ordering = ["-date"]
    context_object_name = "posts"
    
    def get_queryset(self):
        query_set = super().get_queryset()
        data = query_set[:3]
        
        return data
    
    

#------------------------------------------------------------------------------------------------------------------------------

# functional view

def posts(request):
    all_posts = Post.objects.all().order_by("-date")
    return render(request, "blog/all-posts.html",{
        "all_posts" : all_posts
    })
    
# class-based view

class AllPostsView(ListView):
    template_name = "blog/all-posts.html"
    model = Post
    ordering = ["-date"]
    context_object_name = "all_posts"


#------------------------------------------------------------------------------------------------------------------------------
# functional view:

def post_detail(request, slug):
    identifed_post = get_object_or_404(Post, slug=slug)
    return render(request, "blog/post-detail.html", {
        "post" : identifed_post,
        "post_tags" : identifed_post.tags.all()
    })

# class-based view:

class PostDetailView(View):
    
    def is_saved(self, request, post_id):
        stored_posts = request.session.get("stored_posts")
        
        if stored_posts is not None:
            is_saved_for_later = post_id in stored_posts
            
        else:
            is_saved_for_later = False
            
        return is_saved_for_later
        
    
    def get(self, request, slug):
        post = Post.objects.get(slug=slug)
        
        context = {
            "post" : post,
            "post_tags" : post.tags.all,
            "comment_form" : CommentForm(),
            "comments" : post.comments.all().order_by("-id"),      # gives all the objects of the class comments for the given post
            "saved_for_later" : self.is_saved(request, post.id)
        }
        return render(request, "blog/post-detail.html", context)
    
        
    def post(self, request, slug):
        post = Post.objects.get(slug=slug)
        comment_form = CommentForm(request.POST)
        
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)    # this will create an instance of the class but not save it to the database
            comment.post = post
            comment.save()
            
            return HttpResponseRedirect(reverse("post-detail-page", args=[slug])) 
            # gets back to the same page we are at but as a get request this time
        
        context = {
            "post" : post,
            "post_tags" : post.tags.all,
            "comment_form" : CommentForm(),
            "comments" : post.comments.all().order_by("-id"),      #gives all the objects of the class comments for the given post
            "saved_for_later" : self.is_saved(request, post.id)
        }
        return render(request, "blog/post-detail.html", context)
        

class ReadLaterView(View):
    
    def get(self, request):
        stored_posts = request.session.get("stored_posts")
        
        context = {}
        
        if stored_posts is None or len(stored_posts) == 0 :
            context["posts"] = []
            context["has_posts"] = False
        else:
            posts = Post.objects.filter(id__in=stored_posts)    # we fetch only those ids which are part of the stored_posts list
            context["posts"] = posts
            context["has_posts"] = True
            
        return render(request, "blog/stored_posts.html", context)
            
    
    def post(self, request):
        stored_posts = request.session.get("stored_posts")
        
        if stored_posts is None:
            stored_posts = []
            
        post_id = int(request.POST["post_id"])
        
        if post_id not in stored_posts:
            stored_posts.append(post_id)
        else:
            stored_posts.remove(post_id)
            
        request.session["stored_posts"] = stored_posts
            
        return HttpResponseRedirect("/")
            
        
        
