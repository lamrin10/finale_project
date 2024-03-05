from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.http import JsonResponse
from .forms import ProfileEditForm
from django.shortcuts import render, redirect

from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.forms import PasswordChangeForm

from django.urls import reverse_lazy

from django.http import JsonResponse
from django.db import models
from django.contrib.auth.models import User





import json

from .models import *

from django.shortcuts import render
from django.views import View

import os
import pickle
import numpy as np
import pandas as pd
from django.conf import settings
from pickle import load


from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.urls import reverse

import json
from django.http import JsonResponse, HttpResponse
from django.shortcuts import reverse
from django.http import HttpResponseRedirect
from .models import Post, Comment
from .utils import preprocess_and_predict

def sentiment_analyzer(text):
    # Your sentiment analysis logic here
    sentiment_result = preprocess_and_predict(text)
    print(sentiment_result)
    threshold = 0.5
    
    
    if sentiment_result > threshold:
        return "Negative"
    elif sentiment_result < threshold:
        return "Positive"
    else:
        return "Neutral/Undecisive"

    
#for recommerndations
class RecommendView(View):
    template_name = 'network/recommend.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        user_input = request.POST.get('user_input')

        file_path1 = os.path.join(settings.BASE_DIR, 'data', 'final_book_df.pkl')
        file_path2 = os.path.join(settings.BASE_DIR, 'data', 'similarity.pkl')
        file_path = os.path.join(settings.BASE_DIR, 'data', 'book_df.pkl')

        if os.path.exists(file_path1) and os.path.exists(file_path2) and os.path.exists(file_path):
            with open(file_path1, 'rb') as file:
                final_book_df = pickle.load(file)

            with open(file_path2, 'rb') as file:
                similarity = pickle.load(file)

            with open(file_path, 'rb') as file:
                book_df = pickle.load(file)
        else:
            return render(request, self.template_name, {'data': [], 'not_available_message': "Data files not found"})

        # Attempt to find recommendations based on user input
        filtered_books = final_book_df.dropna(subset=['BookName'])
        filtered_books = filtered_books[filtered_books['BookName'] == user_input]

        if not filtered_books.empty:
            book_instance = filtered_books.iloc[0]
            distances = similarity[book_instance.name]
            book_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[:8]

            data = []
            for i in book_list:
                recommended_book_name = final_book_df.iloc[i[0]]["BookName"]
                temp_df = book_df[book_df['BookName'] == recommended_book_name]

                if 'AuthorName' in temp_df.columns and 'ImageURL' in temp_df.columns and 'Genre' in temp_df.columns:
                    author_name = temp_df['Writer'].values[0]
                    image_url = temp_df['ImageURL'].values[0]
                    genre = temp_df['Genre'].values[0]
                    

                    recommended_book_info = {
                        'title': recommended_book_name,
                        'image': image_url,
                        'author': author_name,
                        'genre':genre
                    }
                    if recommended_book_name == user_input:
                        input_book_info = recommended_book_info
                    else:
                        data.append(recommended_book_info)

            # Add the input book info at the beginning of the recommendations
            if input_book_info:
                data.insert(0, input_book_info)

            # Render the template with recommendations and no error message
            return render(request, self.template_name, {'data': data, 'not_available_message': None,'showtitle':True,'source':'recommendations','user_input':user_input})
        else:
    # No recommendations found, perform keyword-based search
    # Handle NaN values in 'BookName' column before applying the filter
            # final_book_df = final_book_df.dropna(subset=['BookName'])
            keyword_results = final_book_df[final_book_df['BookName'].str.contains(user_input, case=False, na=False)]

            if not keyword_results.empty:
    # Process keyword results and return them
                keyword_data = []
                for index, row in keyword_results.iterrows():
                    recommended_book_name = row["BookName"]
                    temp_df = book_df[book_df['BookName'] == recommended_book_name]

                    if not temp_df.empty and 'Writer' in temp_df.columns and 'ImageURL' in temp_df.columns:
                        author_name = temp_df['Writer'].values[0]
                        image_url = temp_df['ImageURL'].values[0]

                        recommended_book_info = {
                            'title': recommended_book_name,
                            'image': image_url,
                            'author': author_name
                        }
                        if recommended_book_name == user_input:
                            input_book_info = recommended_book_info
                        else:
                            keyword_data.append(recommended_book_info)

                return render(request, self.template_name, {'data': keyword_data, 'not_available_message': None, 'showtitle':True,'source':'search_results','user_input':user_input})
            else:
                # No results found for both recommendations and keyword search
                not_available_message = "No results found for the requested book or related keywords"
                return render(request, self.template_name, {'data': [], 'not_available_message': not_available_message})



class BookscollView(View):
    template_name = 'network/bookscoll.html'

    def get(self, request):
        # Use settings.BASE_DIR to get the base directory
        book_file_path = os.path.join(settings.BASE_DIR, 'data', 'book_df.pkl')
        awards_file_path = os.path.join(settings.BASE_DIR, 'data', 'awards_df.pkl')

        try:
            with open(book_file_path, 'rb') as file:
                book_df = pickle.load(file)
        except FileNotFoundError:
            book_df = None
            print(f"The file {book_file_path} is not found.")
            # Log the error or provide a user-friendly message to the frontend

        try:
            with open(awards_file_path, 'rb') as file:
                awards_df = pickle.load(file)
        except FileNotFoundError:
            awards_df = None
            print(f"The file {awards_file_path} is not found.")
            # Log the error or provide a user-friendly message to the frontend

        # Fetch unique genres from the "Genre" column of book_df
        genres = self.get_genres(book_df)

        # Fetch unique awards from the "Award" column of awards_df
        awards = self.get_awards(awards_df)

        # Retrieve selected genre and award from the request
        selected_genre = request.GET.get('genre')
        selected_award = request.GET.get('award')

        if selected_genre:
            # Filter books based on the selected genre from book_df
            books_data = self.filter_books_by_genre(selected_genre, book_df)
        else:
            books_data = self.get_all_books(book_df)

        if selected_award:
            # Filter books based on the selected award name
            books_data = self.filter_books_by_award(selected_award, books_data, awards_df)

        # Convert the Pandas DataFrame to a list of dictionaries
        books = books_data.to_dict(orient='records')
        book_images = book_df['ImageURL'].tolist() if book_df is not None and 'ImageURL' in book_df.columns else ["" for _ in range(len(books))]
        print(len(book_images), 'in book images')
        book_images_in_dict = [data['ImageURL'] for data in books]
        print(len(book_images_in_dict), 'in dict')

        # Combine books and book_images using zip_longest
        # combined_data = list(zip_longest(books, book_images))

        print(books)
        return render(request, self.template_name, {
            'combined_data': books,  # Pass the combined data to the template
            'genres': genres,
            'awards': awards,
            'selected_genre': selected_genre,
            'selected_award': selected_award,
        })
    def get_genres(self, book_df):
        # Fetch unique genres from the "Genre" column of book_df
        return book_df['Genre'].unique().tolist() if book_df is not None else []

    def get_awards(self, awards_df):
        # Fetch unique awards from the "Award" column of awards_df
        return awards_df['Awards'].drop_duplicates().tolist() if awards_df is not None else []

    def filter_books_by_genre(self, selected_genre, book_df):
        # Filter books based on the selected genre from book_df
        selected_genre_lower = selected_genre.lower()

        if book_df is not None:
            return book_df[book_df['Genre'].str.lower().str.strip() == selected_genre_lower]
        return pd.DataFrame()

    def get_all_books(self, book_df):
        # Get all books from book_df
        return book_df if book_df is not None else pd.DataFrame()

    def filter_books_by_award(self, selected_award, books, awards_df):
        # Filter books based on the selected award name
        selected_award_lower = selected_award.lower().strip()

        if awards_df is not None:
            # Use case-insensitive matching and strip extra whitespaces
            matching_books = awards_df[awards_df['Awards'].str.lower().str.strip() == selected_award_lower]['BookName'].tolist()
            # Filter books based on matching book names
            return books[books['BookName'].str.strip().isin(matching_books)]
        return books



def index(request):
    all_posts = Post.objects.all().order_by('-date_created')
    paginator = Paginator(all_posts, 10)
    page_number = request.GET.get('page')
    if page_number == None:
        page_number = 1
    posts = paginator.get_page(page_number)
    followings = []
    suggestions = []
    if request.user.is_authenticated:
        followings = Follower.objects.filter(followers=request.user).values_list('user', flat=True)
        suggestions = User.objects.exclude(pk__in=followings).exclude(username=request.user.username).order_by("?")[:6]
    return render(request, "network/index.html", {
        "posts": posts,
        "suggestions": suggestions,
        "page": "all_posts",
        'profile': False
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        fname = request.POST["firstname"]
        lname = request.POST["lastname"]
        profile = request.FILES.get("profile")
        print(f"--------------------------Profile: {profile}----------------------------")
        cover = request.FILES.get('cover')
        print(f"--------------------------Cover: {cover}----------------------------")

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.first_name = fname
            user.last_name = lname
            if profile is not None:
                user.profile_pic = profile
            else:
                user.profile_pic = "profile_pic/no_pic.png"
            user.cover = cover           
            user.save()
            Follower.objects.create(user=user)
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")



def profile(request, username):
    user = User.objects.get(username=username)
    all_posts = Post.objects.filter(creater=user).order_by('-date_created')
    paginator = Paginator(all_posts, 10)
    page_number = request.GET.get('page')
    if page_number == None:
        page_number = 1
    posts = paginator.get_page(page_number)
    followings = []
    suggestions = []
    follower = False
    if request.user.is_authenticated:
        followings = Follower.objects.filter(followers=request.user).values_list('user', flat=True)
        suggestions = User.objects.exclude(pk__in=followings).exclude(username=request.user.username).order_by("?")[:6]

        if request.user in Follower.objects.get(user=user).followers.all():
            follower = True
    
    follower_count = Follower.objects.get(user=user).followers.all().count()
    following_count = Follower.objects.filter(followers=user).count()
    return render(request, 'network/profile.html', {
        "username": user,
        "posts": posts,
        "posts_count": all_posts.count(),
        "suggestions": suggestions,
        "page": "profile",
        "is_follower": follower,
        "follower_count": follower_count,
        "following_count": following_count
    })


#Password Change View Starts
class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'profile_edit.html' 


def profile_edit_view(request):
    if request.method == 'POST':
        profile_form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        password_change_view = PasswordChangeView.as_view(
            success_url=reverse_lazy('profile_edit'),  # Redirect to the profile edit page after successful password change
        )
        
        if profile_form.is_valid():
            profile_form.save()
            
            # Handle password change separately
            return password_change_view(request)
    else:
        profile_form = ProfileEditForm(instance=request.user)
    
    context = {
        'profile_form': profile_form,
    }
    
    return render(request, 'profile_edit.html', context)

#Password Change View End

def following(request):
    if request.user.is_authenticated:
        following_user = Follower.objects.filter(followers=request.user).values('user')
        all_posts = Post.objects.filter(creater__in=following_user).order_by('-date_created')
        paginator = Paginator(all_posts, 10)
        page_number = request.GET.get('page')
        if page_number == None:
            page_number = 1
        posts = paginator.get_page(page_number)
        followings = Follower.objects.filter(followers=request.user).values_list('user', flat=True)
        suggestions = User.objects.exclude(pk__in=followings).exclude(username=request.user.username).order_by("?")[:6]
        return render(request, "network/index.html", {
            "posts": posts,
            "suggestions": suggestions,
            "page": "following"
        })
    else:
        return HttpResponseRedirect(reverse('login'))

def saved(request):
    if request.user.is_authenticated:
        all_posts = Post.objects.filter(savers=request.user).order_by('-date_created')

        paginator = Paginator(all_posts, 10)
        page_number = request.GET.get('page')
        if page_number == None:
            page_number = 1
        posts = paginator.get_page(page_number)

        followings = Follower.objects.filter(followers=request.user).values_list('user', flat=True)
        suggestions = User.objects.exclude(pk__in=followings).exclude(username=request.user.username).order_by("?")[:6]
        return render(request, "network/index.html", {
            "posts": posts,
            "suggestions": suggestions,
            "page": "saved"
        })
    else:
        return HttpResponseRedirect(reverse('login'))

'''
def search_view(request):
    if request.method == 'GET':
        query = request.GET.get('query', '')
        results = User.objects.filter(
            models.Q(username__icontains=query) |
            models.Q(first_name__icontains=query) |
            models.Q(last_name__icontains=query)
        ).values('id', 'username', 'profile_pic', 'first_name', 'last_name')

        results_list = list(results)
        return JsonResponse({'results': results_list})

    return render(request, 'layout.html')
'''

def search_view(request):
    if request.method == 'GET':
        query = request.GET.get('query', '').strip()

        if query:
            results = User.objects.filter(
                models.Q(username__icontains=query) |
                models.Q(first_name__icontains=query) |
                models.Q(last_name__icontains=query)
            ).values('id', 'username', 'profile_pic', 'first_name', 'last_name')

            results_list = list(results)
            return JsonResponse({'suggestions': results_list})

    return JsonResponse({'suggestions': []})

@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect(reverse('index')) 
              # Redirect to the user's profile page
    else:
        form = ProfileEditForm(instance=request.user)

    return render(request, 'network/profile_edit.html', {'form': form})


@login_required
def create_post(request):
    if request.method == 'POST':
        text = request.POST.get('text')
        pic = request.FILES.get('picture')
        try:
            post = Post.objects.create(creater=request.user, content_text=text, content_image=pic)
            return HttpResponseRedirect(reverse('index'))
        except Exception as e:
            return HttpResponse(e)
    else:
        return HttpResponse("Method must be 'POST'")

@login_required
@csrf_exempt
def edit_post(request, post_id):
    if request.method == 'POST':
        text = request.POST.get('text')
        pic = request.FILES.get('picture')
        img_chg = request.POST.get('img_change')
        post_id = request.POST.get('id')
        post = Post.objects.get(id=post_id)
        try:
            post.content_text = text
            if img_chg != 'false':
                post.content_image = pic
            post.save()
            
            if(post.content_text):
                post_text = post.content_text
            else:
                post_text = False
            if(post.content_image):
                post_image = post.img_url()
            else:
                post_image = False
            
            return JsonResponse({
                "success": True,
                "text": post_text,
                "picture": post_image
            })
        except Exception as e:
            print('-----------------------------------------------')
            print(e)
            print('-----------------------------------------------')
            return JsonResponse({
                "success": False
            })
    else:
            return HttpResponse("Method must be 'POST'")

@csrf_exempt
def like_post(request, id):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            post = Post.objects.get(pk=id)
            print(post)
            try:
                post.likers.add(request.user)
                post.save()
                return HttpResponse(status=204)
            except Exception as e:
                return HttpResponse(e)
        else:
            return HttpResponse("Method must be 'PUT'")
    else:
        return HttpResponseRedirect(reverse('login'))

@csrf_exempt
def unlike_post(request, id):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            post = Post.objects.get(pk=id)
            print(post)
            try:
                post.likers.remove(request.user)
                post.save()
                return HttpResponse(status=204)
            except Exception as e:
                return HttpResponse(e)
        else:
            return HttpResponse("Method must be 'PUT'")
    else:
        return HttpResponseRedirect(reverse('login'))

@csrf_exempt
def save_post(request, id):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            post = Post.objects.get(pk=id)
            print(post)
            try:
                post.savers.add(request.user)
                post.save()
                return HttpResponse(status=204)
            except Exception as e:
                return HttpResponse(e)
        else:
            return HttpResponse("Method must be 'PUT'")
    else:
        return HttpResponseRedirect(reverse('login'))

@csrf_exempt
def unsave_post(request, id):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            post = Post.objects.get(pk=id)
            print(post)
            try:
                post.savers.remove(request.user)
                post.save()
                return HttpResponse(status=204)
            except Exception as e:
                return HttpResponse(e)
        else:
            return HttpResponse("Method must be 'PUT'")
    else:
        return HttpResponseRedirect(reverse('login'))

@csrf_exempt
def follow(request, username):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            user = User.objects.get(username=username)
            print(f".....................User: {user}......................")
            print(f".....................Follower: {request.user}......................")
            try:
                (follower, create) = Follower.objects.get_or_create(user=user)
                follower.followers.add(request.user)
                follower.save()
                return HttpResponse(status=204)
            except Exception as e:
                return HttpResponse(e)
        else:
            return HttpResponse("Method must be 'PUT'")
    else:
        return HttpResponseRedirect(reverse('login'))

@csrf_exempt
def unfollow(request, username):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            user = User.objects.get(username=username)
            print(f".....................User: {user}......................")
            print(f".....................Unfollower: {request.user}......................")
            try:
                follower = Follower.objects.get(user=user)
                follower.followers.remove(request.user)
                follower.save()
                return HttpResponse(status=204)
            except Exception as e:
                return HttpResponse(e)
        else:
            return HttpResponse("Method must be 'PUT'")
    else:
        return HttpResponseRedirect(reverse('login'))


@csrf_exempt
def comment(request, post_id):
    if request.user.is_authenticated:
        if request.method == 'POST':
            data = json.loads(request.body)    # it loads the JSON data from the request body and extracts the comment text.
            comment = data.get('comment_text')
           
           

            post = Post.objects.get(id=post_id) # retrieves the post with the specified ID from the Post model.
            try:
                sentiment = sentiment_analyzer(comment)
                newcomment = Comment.objects.create(post=post,commenter=request.user,comment_content=comment, sentiment=sentiment)#creates a new Comment object associated with the post, the commenter (current user), and the sentiment.
                post.comment_count += 1
                post.save()
                print(newcomment.serialize())
                return JsonResponse([newcomment.serialize()], safe=False, status=201)#prints the serialized form of the new comment and returns a JSON response containing the serialized comment with a status code of 201 (Created).
            except Exception as e:
                return HttpResponse(e)
    
        post = Post.objects.get(id=post_id)
        comments = Comment.objects.filter(post=post)
        comments = comments.order_by('-comment_time').all()
        return JsonResponse([comment.serialize() for comment in comments], safe=False)
    else:
        return HttpResponseRedirect(reverse('login'))

@csrf_exempt
def delete_post(request, post_id):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            post = Post.objects.get(id=post_id)
            if request.user == post.creater:
                try:
                    delet = post.delete()
                    return HttpResponse(status=201)
                except Exception as e:
                    return HttpResponse(e)
            else:
                return HttpResponse(status=404)
        else:
            return HttpResponse("Method must be 'PUT'")
    else:
        return HttpResponseRedirect(reverse('login'))

