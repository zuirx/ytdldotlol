import yt_dlp, os, re, subprocess
from django.shortcuts import render, redirect
from django.http import FileResponse
from django.utils import timezone
from datetime import timedelta
from .models import YtdlpVersion

DOWNLOAD_DIR = 'ytdl-downloads'

def home_yt(request, subpath=''):

    video_id = request.GET.get("v") or request.GET.get("watch")
    message = ''

    if "https://www.youtube.com/watch" in subpath:
        return download_yt(subpath,video_id,"?v=")
    
    elif "https://youtu.be" in subpath:
        return download_yt(subpath)
    
    try: ytdlpver = YtdlpVersion.objects.last().version
    except: ytdlpver = 'unknown'

    theme = request.COOKIES.get('theme')
    context = {
        'theme' : theme,
        'message' : message,
        'ytdlpver' : ytdlpver
    }
    return render(request, 'main/home.html', context)


def dl_from_opt(request):
    action = request.POST.get("action")
    itag = action.split(' - ')[0]
    url = action.split(' - ')[1]
    typeitag = action.split(' - ')[2]
    return download_yt(subpath=url,itag=itag,typeitag=typeitag)


def user_def_cookie(request):
    color_def = request.POST.get("coloropt")

    response = redirect('home_yt')

    if color_def:
        response.set_cookie(
            key='theme',
            value=color_def,
            expires=timezone.now() + timedelta(days=7)
        )

    return response


def download_yt(subpath='', video_id='', middle='', type='video', itag=0, typeitag=''):
    url = subpath + middle + video_id
    if not video_id:
        video_id = subpath.split("/")[-1]
        if '?v=' in subpath:
            video_id = subpath.split("?v=")[-1]

    try: os.remove(final_path)
    except: pass

    match type:
        case 'video': 
            format = 'best'
            filetype = 'mp4'
        case 'audio': 
            format = 'bestaudio'
            filetype = 'mp3'
        case _: 
            format = 'best'
            filetype = 'mp4'

    if itag: format = itag
    if typeitag: filetype = typeitag

    final_path = os.path.join(DOWNLOAD_DIR, f'{video_id}.{filetype}')
    # print(final_path)
    ydl_opts = {
        'format': format,
        'outtmpl': final_path,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl: 
        info = ydl.extract_info(url, download=True)
        # print(info)

    response = FileResponse(open(final_path, 'rb'), as_attachment=True, filename=f'{video_id}.{filetype}')
    return response


def get_info(request):

    url = request.POST.get("yt_link")
    action = request.POST.get("action")
    message = ''

    if not url:
        message = 'No link provided.'

    if not re.search('http', url):
        message = 'Invalid link. (we need the https:// or http://)'
        context = {'message': message}
        return render(request, 'main/home.html', context)


    match action:
        case 'info':
            
            with yt_dlp.YoutubeDL({"listformats": True}) as ydl: 
                info = ydl.extract_info(url,download=False)
            
            formats_dict = {
                'video': {},
                'audio': {}
            }

            for f in info['formats']:
                format_id = f.get('format_id')
                filenum = f.get('filesize')
                
                if filenum:
                    filesize_calc = round(float(f.get('filesize')) / 1024.0 / 1024,2) 
                    filesize_final = f"{filesize_calc} MB"
                else:
                    filesize_final = 'empty'

                entry = {
                    'ext': f.get('ext'),
                    'resolution': f.get('resolution'),
                    'fps': f.get('fps'),
                    'vcodec': f.get('vcodec'),
                    'acodec': f.get('acodec'),
                    'filesize': filesize_final,
                    'url': url,
                }

                if f.get('vcodec') != 'none':
                    formats_dict['video'][format_id] = entry
                else: 
                    formats_dict['audio'][format_id] = entry

            context = {
                'dl_opts': formats_dict,
                'message': message,
            }
            return render(request, 'main/home.html', context)
        
        case 'video':
            return download_yt(subpath=url,type='video')

        case 'audio':
            return download_yt(subpath=url,type='audio')


# TODO
# show progress on download
# convert on home page:
#   select which common type you want (video [good, medium, bad], audio, transcript)
#   (maybe just get what yt-dlp can detect, then download selected [possibly mix audio/video with ffmpeg])
#   playlist support
# add limitations so my server doesnt blow
# donation page OR single ad
# updates/about page
# dark/light theme (cookie)
# short domain and separate project: ytdl.lol/
# translation languages