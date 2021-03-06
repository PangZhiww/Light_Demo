from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from django.urls import reverse
from web.forms.wiki import WikiModelForm
from web import models
from django.views.decorators.csrf import csrf_exempt

from utils.encrypt import uid
from utils.tencent.cos import upload_file

def wiki(request, project_id):
    """
    wiki的首页
    :param request:
    :param project_id:
    :return:
    """
    wiki_id = request.GET.get('wiki_id')
    if not wiki_id or not wiki_id.isdecimal():
        return render(request, 'wiki.html')

    wiki_object = models.Wiki.objects.filter(id=wiki_id, project_id=project_id).first()

    return render(request, 'wiki.html', {'wiki_object': wiki_object})


def wiki_add(request, project_id):
    """
    文档添加
    :param request:
    :param project_id:
    :return:
    """
    if request.method == 'GET':
        form = WikiModelForm(request)
        return render(request, 'wiki_form.html', {'form': form})
    form = WikiModelForm(request, data=request.POST)
    if form.is_valid():
        # 判断用户是否已经选择文章
        if form.instance.parent:
            form.instance.depth = form.instance.parent.depth + 1
        else:
            form.instance.depth = 1

        form.instance.project = request.tracer.project
        form.save()
        url = reverse('wiki', kwargs={'project_id': project_id})
        return redirect(url)

    return render(request, 'wiki_form.html', {'form': form})


def wiki_catalog(request, project_id):
    """
    wiki 目录
    :param request:
    :param project_id:
    :return:
    """
    # 获取当前项目所有的目录
    # data = models.Wiki.objects.filter(project=request.tracer.project).values_list('id', 'title', 'parent_id')
    # data = models.Wiki.objects.filter(project=request.tracer.project).values('id', 'title', 'parent_id')
    data = models.Wiki.objects.filter(project=request.tracer.project).values('id', 'title', 'parent_id').order_by(
        'depth', 'id')
    return JsonResponse({'status': True, 'data': list(data)})


# def wiki_detail(request, project_id):
#     """
#     查看文章详细页面
#     :param request:
#     :param project_id:
#     :return:
#     """
#     return HttpResponse('查看文章详细')


def wiki_delete(request, project_id, wiki_id):
    """
    删除文档
    :param request:
    :param project_id:
    :return:
    """
    models.Wiki.objects.filter(project_id=project_id, id=wiki_id).delete()

    url = reverse('wiki', kwargs={'project_id': project_id})
    return redirect(url)


def wiki_edit(request, project_id, wiki_id):
    """
    删除文档
    :param request:
    :param project_id:
    :return:
    """
    wiki_object = models.Wiki.objects.filter(project_id=project_id, id=wiki_id).first()
    if not wiki_object:
        url = reverse('wiki', kwargs={'project_id': project_id})
        return redirect(url)
    if request.method == 'GET':
        form = WikiModelForm(request, instance=wiki_object)
        return render(request, 'wiki_form.html', {'form': form})
    form = WikiModelForm(request, data=request.POST, instance=wiki_object)
    if form.is_valid():
        if form.instance.parent:
            form.instance.depth = form.instance.parent.depth + 1
        else:
            form.instance.depth = 1

        form.save()
        url = reverse('wiki', kwargs={'project_id': project_id})
        preview_url = "{0}?wiki_id={1}".format(url,wiki_id)
        return redirect(preview_url)

    return render(request, 'wiki_form.html', {'form': form})


@csrf_exempt
def wiki_upload(request, project_id):
    """
    markdown 本地上传
    :param request:
    :param project_id:
    :return:
    """
    result = {
        'success': 0,
        'message': None,
        'url': None
    }

    print('收到上传的图片了')
    print(request.FILES)

    # 文件对象上传到当前项目的桶中
    image_object = request.FILES.get('editormd-image-file')
    if not image_object:
        result['message'] = "文件不存在"
        return JsonResponse(result)

    ext = image_object.name.rsplit('.')[-1]
    key = "{}.{}".format(uid(request.tracer.user.mobile_phone),ext)
    image_url = upload_file(
        request.tracer.project.bucket,
        request.tracer.project.region,
        image_object,
        key
    )
    print(image_url)

    # return JsonResponse({})
    result['success'] = 1
    result['url'] = image_url
    #
    return JsonResponse(result)
