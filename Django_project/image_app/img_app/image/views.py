from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render, HttpResponse
from .forms import CommentForm, ImagesForm
from image.models import Images, ImageComment


def index(request):
    return render(request, "index.html")


def images(request):
    pictures = Images.objects.all()
    form = ImagesForm()
    if request.method == 'POST':
        form = ImagesForm(request.POST, request.FILES)
        if form.is_valid():
            if 'image' in request.FILES:
                form.image = request.FILES['image']
            form.save(commit=True)
            return HttpResponse('Image has been uploaded')
        else:
            print(form.errors)
    return render(request, "images.html", {'pictures': pictures, 'form': form})


def create_photo_comments(request, pk):
    picture = Images.objects.get(pk=pk)
    comments = ImageComment.objects.filter(name_id=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            record = ImageComment(name=picture, comment=form.clean()['comment'])
            record.save()
    else:
        form = CommentForm()
    return render(request, 'photo.html', {'picture': picture, 'comments': comments, 'form': form})


def edit_photo_comments(request, pk, id):
    try:
        comment = ImageComment.objects.get(id=id)
        if request.method == 'POST':
            comment.comment = request.POST.get('comment')
            comment.save()
            return HttpResponseRedirect('/')
        else:
            return render(request, 'edit.html', {'comment': comment})
    except ImageComment.DoesNotExist:
        return HttpResponseNotFound('<h2>Комментарий не найден<h2>')


def delete_photo_comments(request, pk, id):
    try:
        comment = ImageComment.objects.get(id=id)
        comment.delete()
        return HttpResponseRedirect('/')
    except ImageComment.DoesNotExist:
        return HttpResponseNotFound('<h2>Комментарий не найден<h2>')
