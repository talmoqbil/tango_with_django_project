from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category
from rango.models import Page
from rango.forms import CategoryForm
from django.shortcuts import redirect
from rango.forms import PageForm
from django.urls import reverse
from rango.forms import UserForm, UserProfileForm
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from datetime import datetime


def index(request):
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    
    context_dict = {}
    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list
    context_dict['pages'] = page_list
    
    visitor_cookie_handler(request)

    response = render(request, 'rango/index.html', context=context_dict)
    return response


def about(request):
    context_dict={}
    
    visitor_cookie_handler(request)
    # should be after the call to the visitor_cookie_handler() function.
    context_dict['visits'] = request.session['visits']
    
    return render(request, 'rango/about.html', context=context_dict)


def show_category(request, category_name_slug):
    context_dict = {}

    try:
        category = Category.objects.get(slug=category_name_slug)
        pages = Page.objects.filter(category=category)

        context_dict['pages'] = pages
        context_dict['category'] = category
    
    except Category.DoesNotExist:
        context_dict['category'] = None
        context_dict['pages'] = None
    
    return render(request, 'rango/category.html', context=context_dict)

@login_required
def add_category(request):
    form = CategoryForm()
    
    # is it a HTTP post?
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        
        
        if form.is_valid():
            form.save(commit=True)
            # redirect the user back to the index view.
            return redirect('/rango/')
        
        else:
            # print error
            print(form.errors)
        
        # Render the form with error messages
    return render(request, 'rango/add_category.html', {'form': form})


@login_required
def add_page(request, category_name_slug):
    
    try:
        category = Category.objects.get(slug=category_name_slug)
        
    except Category.DoesNotExist:
        category = None
        
    # You cannot add a page to a Category that does not exist...
    if category is None:
        return redirect('/rango/')
    
    form = PageForm()
    
    if request.method == 'POST':
        form = PageForm(request.POST)
        
        if form.is_valid():
            
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
            return redirect(reverse('rango:show_category', kwargs={'category_name_slug': category_name_slug}))

        else:
            print(form.errors)
            
    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context=context_dict)    

    

def register(request):
    # tells if registration was successful. true if yes but is set false initially
    registered = False

    if request.method == 'POST':
        # grabs info from the raw form information from user and userprofile.
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            # Save the user form data
            user = user_form.save()
            # then hash the user
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            
            # Did the user provide a profile picture?
            # If user put a pic put in the UserProfile model.
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            profile.save()
            # successful registration
            registered = True
        else:
            print(user_form.errors, profile_form.errors)
    else:
        # since its not HTTP POST, render form using two ModelForm instances. which will be blank
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request, 'rango/register.html',context = {'user_form': user_form,'profile_form': profile_form,'registered': registered})


def user_login(request):
    # If request is HTTP POST pull out the info
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # see if the login details are valid if so then a User object is returned
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return redirect(reverse('rango:index'))
            else:
                return HttpResponse("Your Rango account is disabled.")
        else:
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")
    else:
        return render(request, 'rango/login.html')

@login_required
def restricted(request):
    return render(request, 'rango/restricted.html')


@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse('rango:index'))

# helper method
def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val


def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, 'visits', '1'))
    last_visit_cookie = get_server_side_cookie(request,'last_visit',str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7],'%Y-%m-%d %H:%M:%S')

    # If it's been more than a day since the last visit...
    if (datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        # Update the last visit cookie now that we have updated the count
        request.session['last_visit'] = str(datetime.now())
    else:
        # Set the last  cookie
        request.session['last_visit'] = last_visit_cookie
        # Update/set the visits cookie
    request.session['visits'] = visits


