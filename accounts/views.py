from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm

# Create your views here.
def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = SignUpForm()

    return render(request,'accounts/signup.html',{'form':form})

def terms(request):
    return render(request,'accounts/riyokiyaku.html')