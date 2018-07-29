from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Product, ProductImage
from .forms import ProductForm, ProductImageForm
from django.contrib import messages
from django.conf import settings
from hokudai_furima.chat.models import Talk, Chat
from hokudai_furima.chat.forms import TalkForm
from django.http import HttpResponse
from functools import reduce
import os
from versatileimagefield.placeholder import OnDiscPlaceholderImage
from hokudai_furima.account.models import User
from hokudai_furima.notification.models import Notification
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils.datastructures import MultiValueDict
import re
from hokudai_furima.todo_list.models import ReportToRecieveTodo, RatingTodo
from rules.contrib.views import permission_required
from .emails import send_decided_buyer_email, send_rating_other_email, send_want_your_product_email

def get_product_by_pk(request, pk):
    return get_object_or_404(Product, pk=pk)

def get_product_by_pk_for_chat(request, product_pk, wanting_user_pk):
    return get_object_or_404(Product, pk=product_pk)

def get_product_by_product_pk(request, product_pk):
    return get_object_or_404(Product, pk=product_pk)

def product_list(request):
    products = product.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    return render(request, 'product/product_list.html', {'products': products})

def is_totally_valid(product_form, product_image_forms):
    if not product_form.is_valid():
        print(product_form)
        return False
    else:
        for product_image_form in product_image_forms:
            if not product_image_form.is_valid():
                print(product_image_form)
                return False
    return True

@login_required
def create_product(request):
    if request.method == "POST":
        product_image_forms = []
        for i, _file in enumerate(request.FILES.getlist('image')):
            product_image_forms.append(ProductImageForm(i, request.POST, {'image':_file}))
        product_form = ProductForm(request.POST)
        if is_totally_valid(product_form, product_image_forms):
            product = product_form.save(commit=False)
            product.seller = request.user
            product.save()
            for product_image_form in product_image_forms:
                product_image = product_image_form.save(commit=False)
                product_image.product = product
                product_image.save()
                product.productimage_set.add(product_image)
            product.save()
            messages.success(request, '出品に成功しました')
            return redirect('product:product_details', pk=product.pk)
    else:
        product_form = ProductForm()
    product_image_forms = [ProductImageForm(_i) for _i in range(4)]
    return render(request, 'product/create_product.html', {'product_form': product_form, 'product_image_forms': product_image_forms})


def get_original_filename(versatileimagefield_filepath):
    original_filename_without_extent = re.search(r'/(.+)_',versatileimagefield_filepath.image.name).group(1)
    original_extent = re.search(r'(\..+)$',versatileimagefield_filepath.image.name).group(1)
    return original_filename_without_extent+original_extent


def make_product_image_forms(request):
    product_image_forms = []
    for i, _file in enumerate(request.FILES.getlist('image')):
        product_image_forms.append(ProductImageForm(i, request.POST, {'image':_file}))
    return product_image_forms


def get_posted_product_images(request):
    posted_images = request.FILES.getlist('image')
    return posted_images


@login_required
def update_product(request, product_pk):
    print(request.POST)
    product = get_object_or_404(Product, pk=product_pk)
    product_seller_id = product.seller.id
    if product_seller_id != request.user.id:
        return HttpResponse('invalid request')
    else:
        if request.method == "POST":
            product_form = ProductForm(request.POST, instance=product)
            product_image_forms = make_product_image_forms(request)
            if is_totally_valid(product_form, product_image_forms):
                product = product_form.save(commit=False)
                product.seller = request.user
                product.save()
                changed_image_flags = [request.POST['image_'+str(i)+'_exists'] for i in range(4)]
                changed_flag_1_length = len([_ for _ in changed_image_flags if _ == '1'])
                before_product_images = [bpi for bpi in product.productimage_set.all()]
                posted_images = get_posted_product_images(request)
                posted_image_index = 0
                for image_form_index, flag in enumerate(changed_image_flags):
                    if flag == '1':
                        if posted_image_index < len(posted_images):
                            if image_form_index < len(before_product_images):
                                if posted_images[posted_image_index].name != get_original_filename(before_product_images[posted_image_index]):
                                    product_image = before_product_images[image_form_index]
                                    product_image.image = product_image_forms[posted_image_index].save(commit=False).image
                                    product_image.product = product
                                    product_image.update()
                                    posted_image_index += 1
                            else:
                                product_image = product_image_forms[posted_image_index].save(commit=False)
                                product_image.product = product
                                product_image.save()
                                product.productimage_set.add(product_image)
                                product.save()
                                posted_image_index += 1
                    elif flag == '2':
                        before_product_image = before_product_images[image_form_index]
                        before_product_image.delete()
                messages.success(request, '商品情報を更新しました')
                return redirect('product:product_details', pk=product.pk)

        product_form = ProductForm(instance=product)
        product_image_forms = []
        product_images = product.productimage_set.all()
        product_image_thumbnail_urls = [product_image.thumbnail_url for product_image in product_images]
        for _i in range(4):
            if _i < len(product_images):
                product_image_forms.append(ProductImageForm(_i, instance=product_images[_i]))
            else:
                product_image_forms.append(ProductImageForm(_i))
        return render(request, 'product/update_product.html', {'product_form': product_form, 'product_image_forms': product_image_forms, 'product':product, 'product_image_thumbnail_urls': product_image_thumbnail_urls, 'placeholder_image_number_list': range(len(product_image_thumbnail_urls), 4)})

@permission_required('products.can_access', fn=get_product_by_pk, raise_exception=True)
def product_details(request, pk):
    product = get_object_or_404(Product, pk=pk)
    talk_form = TalkForm()
    talk_records = Chat.objects.filter(product=product)
    if talk_records.exists():
        talks = list(map(lambda x: x.talk_set.all(),list(talk_records)))[0]
    else:
        talks = []
    
    wanting_users = product.wanting_users.all()
    if request.user.is_authenticated:
        return render(request, 'product/product_details.html', {'product': product, 'form': talk_form, 'talks':talks, 'wanting_users': wanting_users})
    else:
        return render(request, 'product/product_details.html', {'product': product, 'talks':talks})


@login_required
@permission_required('products.can_access', fn=get_product_by_pk, raise_exception=True)
def want_product(request, pk):
    if request.method == 'POST':
        wanting_user = request.user
        product = get_object_or_404(Product, pk=pk)
        product.wanting_users.add(wanting_user)
        product.save()
        relative_url = reverse('product:product_details', kwargs={'pk': product.pk})
        notification = Notification(reciever=product.seller, message=wanting_user.username+'さんが「'+product.title+'」の購入を希望しました。', relative_url=relative_url)
        notification.save()

        send_want_your_product_email(pk, wanting_user.pk, product.seller.email)

        messages.success(request, '購入希望が送信されました')
        return redirect('product:product_details', pk=product.pk)
    else:
        return HttpResponse('can\'t accept GET request')


@login_required
@permission_required('products.can_access', fn=get_product_by_pk, raise_exception=True)
def cancel_want_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.wanting_users.remove(request.user)
    return redirect('product:product_details', pk=product.pk)   


@permission_required('products.can_access', fn=get_product_by_pk_for_chat, raise_exception=True)
@login_required
def product_direct_chat(request, product_pk, wanting_user_pk):
    wanting_user = get_object_or_404(User, pk=wanting_user_pk)
    product = get_object_or_404(Product, pk=product_pk)
    if (request.user == wanting_user and request.user != product.seller) or (request.user == product.seller and request.user != wanting_user):
        chat = Chat.objects.filter(product=product, product_wanting_user=wanting_user, product_seller=product.seller)
        if chat.exists():
            talks = chat[0].talk_set.all()
        else:
            # 売り手から新しいユーザとのチャットルームを作成することはできない
            if request.user != product.seller:
                chat = Chat(product=product, product_wanting_user=wanting_user, product_seller=product.seller, created_date=timezone.now())
                chat.save()
                talks = []
            else:
                return HttpResponse('invalid request')
        if request.user == product.seller:
            talk_reciever_id = wanting_user.id
        else:
            talk_reciever_id = product.seller.id 
        talk_form = TalkForm()
        return render(request, 'product/product_direct_chat.html', {'product': product, 'form': talk_form, 'talks':talks, 'wanting_user': wanting_user, 'chat': chat, 'talk_reciever_id': talk_reciever_id})
    else:
        return HttpResponse('invalid request')


@login_required
def decide_to_sell(request, product_pk, wanting_user_pk):
    wanting_user = get_object_or_404(User, pk=wanting_user_pk)
    product = get_object_or_404(Product, pk=product_pk)
    if request.user == product.seller:
        product.is_sold = True
        product.buyer = wanting_user
        product.update()
        relative_url = reverse('product:product_direct_chat', kwargs={'product_pk': product.pk, 'wanting_user_pk': wanting_user.pk})
        notification = Notification(reciever=wanting_user, message=request.user.username+'が「'+product.title+'」をあなたに販売することを確定しました。チャットで出品者と取引方法を確認し合ってください', relative_url=relative_url)
        notification.save()
        todo = ReportToRecieveTodo(user=product.buyer, relative_url=relative_url, product=product)
        todo.set_template_message()
        todo.save()

        send_decided_buyer_email(product_pk, wanting_user_pk, wanting_user.email)

        messages.success(request, '購入者を決定しました。チャットで購入者と話し合いの上、商品と料金の受け渡し方法を決定してください。このサイト上での決済はできませんのでご注意ください。')
        return redirect('product:product_details', pk=product.pk)   
    else:
        return HttpResponse('invalid request')


@permission_required('products.can_access', fn=get_product_by_product_pk, raise_exception=True)
@login_required
def complete_to_recieve(request, product_pk):
    product = get_object_or_404(Product, pk=product_pk)
    if request.user == product.buyer:
        rating_relative_url = reverse('rating:post_rating', kwargs={'product_pk': product.pk})
        notification = Notification(reciever=request.user, message=product.seller.username+'との間での「'+product.title+'」の受け渡しの完了を確認しました。最後に出品者を評価してください。', relative_url=rating_relative_url)
        notification.save()
        notification = Notification(reciever=product.seller, message=request.user.username+'との間での「'+product.title+'」の受け渡しの完了を確認しました。最後に購入者を評価してください。', relative_url=rating_relative_url)
        notification.save()

        report_to_recieve_todo = ReportToRecieveTodo.objects.get(user=product.buyer, product=product)
        report_to_recieve_todo.done()
        report_to_recieve_todo.update()

        seller_rating_todo = RatingTodo(user=product.seller, relative_url=rating_relative_url, product=product)
        seller_rating_todo.set_template_message()
        seller_rating_todo.save()
        buyer_rating_todo = RatingTodo(user=product.buyer, relative_url=rating_relative_url, product=product)
        buyer_rating_todo.set_template_message()
        buyer_rating_todo.save()

        send_rating_other_email(product_pk, product.seller.username, product.buyer.email)
        send_rating_other_email(product_pk, product.buyer.username, product.seller.email)

        messages.success(request, '商品の受け取り処理が完了しました。最後に出品者を評価してください。')
        return redirect('rating:post_rating', product_pk=product.pk)
    else:
        return HttpResponse('invalid request')


