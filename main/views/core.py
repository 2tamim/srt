from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from ..forms import UserLoginForm
from ..models import Project, ProjectCategory, Access,User,Product
import datetime
# import folium
from folium.plugins import FastMarkerCluster
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from django.conf import settings
import os
from offline_folium import offline
import folium
import folium.plugins as plugins
from jinja2 import Template
from folium.map import Marker
from folium.features import DivIcon
import random


"""
    user accounting functions that consist login and logout
"""


def user_login(request):
    try:
        if request.user.is_authenticated:
            return redirect('/')

        next = request.GET.get('next')
        form = UserLoginForm(request.POST or None)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            login(request, user)
            if next:
                return redirect(next)
            return redirect('core:home')

        context = {
            'form': form,
        }

        return render(request, 'main/core/login.html', context)
    except:
        return render(request, 'main/core/login.html')


def user_logout(request):
    try:
        logout(request)
        return redirect('login')
    except:
        return render(request, 'main/core/login.html')


"""
   showing
"""


@login_required(login_url='core:login')
def dashboard(request):
    if request.user.is_superuser or request.user.extension.access == 2:
        projects = Project.objects.all()
    else:
        projects = request.user.authorized_projects.all()
    context = {'projects': projects}
    return render(request, 'main/core/dashboard.html', context)


"""
   project objects
"""


@login_required(login_url='core:login')
def projects_home(request):
    category = ProjectCategory.objects.all()
    users = User.objects.all()
    if request.user.is_superuser or request.user.extension.access == 2:
        projects = Project.objects.all()
    else:
        projects = request.user.authorized_projects.all()
    context = {'categories': category, 'projects': projects, 'users':users}
    return render(request, 'main/core/projects/home.html', context)


@login_required(login_url='core:login')
def projects_single(request, project_id):
    if request.user.is_superuser or request.user.extension.access == 2:
        projects = Project.objects.all()
    else:
        projects = request.user.authorized_projects.all()
    # try:
    project = projects.get(id=project_id)
    products = Product.objects.all()
    context = {'project': project,'products': products}
    return render(request, 'main/core/projects/single.html', context)

    # except:
    #     return redirect('core:project_home')


@login_required(login_url='core:login')
def projects_graph(request, project_id):
    if request.user.is_superuser or request.user.extension.access == 2:
        projects = Project.objects.all()
    else:
        projects = request.user.authorized_projects.all()
    # try:
    project = projects.get(id=project_id)
    products = Product.objects.all()
    context = {'project': project,'products': products}
    return render(request, 'main/core/projects/graph.html', context)

    # except:
    #     return redirect('core:project_home')


@login_required(login_url='core:login')
def add_project(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            # try:
            pro_name = request.POST.get('project_name')
            if request.POST.get('project_parent') and int(request.POST.get('project_parent'))>0 :
                pro_parent = request.POST.get('project_parent')
            else:
                pro_parent = None
            pro_country = request.POST.get('project_country')
            pro_type = request.POST.get('project_type')
            pro_category = request.POST.get('project_category')
            pro_manager = request.POST.get('project_manager')
            if len(request.POST.get('project_deadline')) > 0:
                pro_deadline = datetime.datetime.strptime(request.POST.get('project_deadline'), '%Y-%m-%dT%H:%M').replace(
                    tzinfo=datetime.timezone.utc)
            else:
                pro_deadline = None

            if len(request.POST.get('project_description')) > 0:
                pro_description = request.POST.get('project_description')
            else:
                pro_description = None
            pro_auth_users = User.objects.filter(id__in = [int(x) for x in request.POST.getlist('project_auth_users')]).exclude(id = pro_manager)

            project = Project.objects.create(name=pro_name, category_id=pro_category, mission=pro_type,
                                    country=pro_country, user_id=request.user.id, parent = pro_parent,
                                    manager_id = pro_manager, deadline= pro_deadline, description=pro_description)

            project.authorized_users.set(pro_auth_users)
            messages.success(request, "project added successfully")

            # except Exception as Ex:
            #     messages.error(request, 'Error Adding Project! ' + str(Ex))

            return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'project/'))




"""
   project objects
"""


@login_required(login_url='core:login')
def project_map(request, mission=None):

    countries = gpd.read_file(settings.COUNTRIES_EARTH_FILE_PATH, encoding="utf-8")
    ocean = gpd.read_file(settings.OCEAN_EARTH_FILE_PATH, encoding="utf-8")
    gridlines = gpd.read_file(settings.GRIDLINES_EARTH_FILE_PATH, encoding="utf-8")
    rivers = gpd.read_file(settings.RIVERS_EARTH_FILE_PATH, encoding="utf-8")
    lakes = gpd.read_file(settings.LAKES_EARTH_FILE_PATH, encoding="utf-8")

    if mission == 'mission':
        df = pd.DataFrame(list(Project.objects.filter(mission=0).values('name', 'country')))
    elif mission == 'noun_mission':
        df = pd.DataFrame(list(Project.objects.filter(mission=1).values('name', 'country')))
    elif mission == 'rel_mission':
        df = pd.DataFrame(list(Project.objects.filter(mission=2).values('name', 'country')))
    elif mission == 'all':
        df = pd.DataFrame(list(Project.objects.all().values('name', 'country')))

    countries = countries[["geometry", "iso_a2_eh"]]

    if df.size:
        df = df.rename({"country": "iso_a2_eh"}, axis=1)
        df = df[["name", "iso_a2_eh"]]
        countries = countries.merge(df, on="iso_a2_eh")
        # countries = countries.drop_duplicates(subset=["iso_a2_eh"])

        gf = pd.read_csv(settings.DATABASE_COUNTRIES_FILE_PATH, encoding="utf-8")
        gf = gf.rename({"ISO 3166 Country Code": "iso_a2_eh"}, axis=1)
        gf = gf[["iso_a2_eh", "Country", "Latitude", "Longitude", "y1", "y2", "x1", "x2"]]
        countries = countries.merge(gf, on="iso_a2_eh")
        # countries = countries.drop_duplicates(subset=["iso_a2_eh"])

    geo = folium.GeoJson(
        data=countries.to_json(), style_function=lambda x: {"color": "#a9eafc", "weight": 0.5}
    )

    ocean_json = folium.GeoJson(
        data=ocean.to_json(), style_function=lambda x: {"color": "#a9eafc", "weight": 0.5}
    )

    lines_json = folium.GeoJson(
        data=gridlines.to_json(),
        style_function=lambda x: {"color": "#000000", "weight": 0.5, "dashArray": "5, 5"},
    )

    rivers_json = folium.GeoJson(
        data=rivers.to_json(), style_function=lambda x: {"color": "#a9eafc", "weight": 0.5}
    )

    lakes_json = folium.GeoJson(
        data=lakes.to_json(), style_function=lambda x: {"color": "#a9eafc", "weight": 0.5}
    )

    # Modify Marker template to include the onClick event
    click_template = """{% macro script(this, kwargs) %}
        var {{ this.get_name() }} = L.marker({{ this.location|tojson }},{{ this.options|tojson }})
        .addTo({{ this._parent.get_name() }}).on('click', onClick);
    {% endmacro %}"""

    # Change template to custom template
    Marker._template = Template(click_template)

    m = folium.Map(location=[0, 0], tiles=None, zoom_start=3, max_zoom=5)

    # Create the onClick listener function as a branca element and add to the map html
    click_js = """function onClick(e) {
                     //var point = e; console.log(point)
                     if (document.getElementById('srt_map')){
                     parent.selectMap(document.getElementById('srt_map').getAttribute("name"));
                     }
                     }"""

    e = folium.Element(click_js)
    html = m.get_root()
    html.script.get_root().render()
    html.script._children[e.get_name()] = e

    ocean_json.add_to(m)
    lines_json.add_to(m)
    geo.add_to(m)
    lakes_json.add_to(m)

    for idx, row in df.iterrows():
        try:
            y1 = float(countries[["iso_a2_eh", "Country", "Latitude", "Longitude", "y1", "y2", "x1", "x2"]].iloc[idx, 4])
            y2 = float(countries[["iso_a2_eh", "Country", "Latitude", "Longitude", "y1", "y2", "x1", "x2"]].iloc[idx, 5])
            x1 = float(countries[["iso_a2_eh", "Country", "Latitude", "Longitude", "y1", "y2", "x1", "x2"]].iloc[idx, 6])
            x2 = float(countries[["iso_a2_eh", "Country", "Latitude", "Longitude", "y1", "y2", "x1", "x2"]].iloc[idx, 7])

            if x1 < x2:
                x = x1
            else:
                x = x2

            if y1 < y2:
                y = y1
            else:
                y = y2
            lat = float(countries[["iso_a2_eh", "Country", "Latitude", "Longitude", "y1", "y2", "x1", "x2"]].iloc[idx, 2]) + random.uniform(-(y/3), y/3)
            lon = float(countries[["iso_a2_eh", "Country", "Latitude", "Longitude", "y1", "y2", "x1", "x2"]].iloc[idx, 3]) + random.uniform(-(x/3), x/3)
            coordinates = (lat, lon)
            country_name = countries[["iso_a2_eh", "Country", "Latitude", "Longitude", "y1", "y2", "x1", "x2"]].iloc[idx, 1]
            country_iso = countries[["iso_a2_eh", "Country", "Latitude", "Longitude", "y1", "y2", "x1", "x2"]].iloc[idx, 0]
            pp = folium.Html("""<p id='srt_map' name='"""+country_iso+"""'>"""+country_name+"""</p>""", script=True)
            popup = folium.Popup(pp, max_width=2650)
            folium.Marker(coordinates, popup=popup).add_to(m)

        except:
            continue



    # p1 = [45.3288, -121.6625]
    # folium.Marker(p1, icon=DivIcon(
    #     icon_size=(150, 36),
    #     icon_anchor=(7, 20),
    #     html='<div style="font-size: 18pt; color : black">1</div>',
    # )).add_to(m)
    # m.add_child(folium.CircleMarker(p1, radius=15))
    #
    # p2 = [45.3311, -121.7113]
    # folium.Marker(p2, icon=DivIcon(
    #     icon_size=(150, 36),
    #     icon_anchor=(7, 20),
    #     html='<div style="font-size: 18pt; color : black">2</div>',
    # )).add_to(m)
    # m.add_child(folium.CircleMarker(p2, radius=15))

    m = m._repr_html_()

    #filter_map
    pro = Project.objects.all()
    pro_count = Project.objects.all().count()
    pro_access_count = Access.objects.all().count()
    pro_mission_filter = Project.objects.filter(mission=0).count()
    pro_noun_mission_filter = Project.objects.filter(mission=1).count()
    pro_semi_mission_filter = Project.objects.filter(mission=2).count()


    context = {
        'm': m,
        'pro': pro,
        'pro_count': pro_count,
        'pro_access_count': pro_access_count,
        'pro_mission_filter': pro_mission_filter,
        'pro_noun_mission_filter': pro_noun_mission_filter,
        'pro_semi_mission_filter': pro_semi_mission_filter,
    }

    return render(request, 'main/core/map/home.html', context)


@login_required(login_url='core:login')
def project_map_access(request, mission=None):

    countries = gpd.read_file(settings.COUNTRIES_EARTH_FILE_PATH, encoding="utf-8")
    ocean = gpd.read_file(settings.OCEAN_EARTH_FILE_PATH, encoding="utf-8")
    gridlines = gpd.read_file(settings.GRIDLINES_EARTH_FILE_PATH, encoding="utf-8")
    rivers = gpd.read_file(settings.RIVERS_EARTH_FILE_PATH, encoding="utf-8")
    lakes = gpd.read_file(settings.LAKES_EARTH_FILE_PATH, encoding="utf-8")

    if mission == 'mission':
        df = pd.DataFrame(list(Access.objects.filter(project__mission=0).values('title', 'project__country')))
    elif mission == 'noun_mission':
        df = pd.DataFrame(list(Access.objects.filter(project__mission=1).values('title', 'project__country')))
    elif mission == 'rel_mission':
        df = pd.DataFrame(list(Access.objects.filter(project__mission=2).values('title', 'project__country')))
    elif mission == 'all':
        access = list(Access.objects.all().values('title', 'project__country'))
        df = pd.DataFrame(access)

    countries = countries[["geometry", "iso_a2_eh"]]

    if df.size:
        df = df.rename({"project__country": "iso_a2_eh"}, axis=1)
        df = df[["title", "iso_a2_eh"]]
        countries = countries.merge(df, on="iso_a2_eh")
        # countries = countries.drop_duplicates(subset=["iso_a2_eh"])

        gf = pd.read_csv(settings.DATABASE_COUNTRIES_FILE_PATH, encoding="utf-8")
        gf = gf.rename({"ISO 3166 Country Code": "iso_a2_eh"}, axis=1)
        gf = gf[["iso_a2_eh", "Country", "Latitude", "Longitude"]]
        countries = countries.merge(gf, on="iso_a2_eh")
        # countries = countries.drop_duplicates(subset=["iso_a2_eh"])

    geo = folium.GeoJson(
        data=countries.to_json(), style_function=lambda x: {"color": "#a9eafc", "weight": 0.5}
    )

    ocean_json = folium.GeoJson(
        data=ocean.to_json(), style_function=lambda x: {"color": "#a9eafc", "weight": 0.5}
    )

    lines_json = folium.GeoJson(
        data=gridlines.to_json(),
        style_function=lambda x: {"color": "#000000", "weight": 0.5, "dashArray": "5, 5"},
    )

    rivers_json = folium.GeoJson(
        data=rivers.to_json(), style_function=lambda x: {"color": "#a9eafc", "weight": 0.5}
    )

    lakes_json = folium.GeoJson(
        data=lakes.to_json(), style_function=lambda x: {"color": "#a9eafc", "weight": 0.5}
    )

    # Modify Marker template to include the onClick event
    click_template = """{% macro script(this, kwargs) %}
        var {{ this.get_name() }} = L.marker({{ this.location|tojson }},{{ this.options|tojson }})
        .addTo({{ this._parent.get_name() }}).on('click', onClick);
    {% endmacro %}"""

    # Change template to custom template
    Marker._template = Template(click_template)

    m = folium.Map(location=[0, 0], tiles=None, zoom_start=3, max_zoom=5)

    # Create the onClick listener function as a branca element and add to the map html
    click_js = """function onClick(e) {
                     //var point = e; console.log(point)
                     if (document.getElementById('srt_map')){
                     parent.selectMap(document.getElementById('srt_map').getAttribute("name"));
                     }
                     }"""

    e = folium.Element(click_js)
    html = m.get_root()
    html.script.get_root().render()
    html.script._children[e.get_name()] = e

    m = folium.Map(location=[0, 0], tiles=None, zoom_start=3, max_zoom=5)
    ocean_json.add_to(m)
    lines_json.add_to(m)
    geo.add_to(m)
    lakes_json.add_to(m)

    for idx, row in df.iterrows():
        try:
            y1 = float(countries[["iso_a2_eh", "Country", "Latitude", "Longitude", "y1", "y2", "x1", "x2"]].iloc[idx, 4])
            y2 = float(countries[["iso_a2_eh", "Country", "Latitude", "Longitude", "y1", "y2", "x1", "x2"]].iloc[idx, 5])
            x1 = float(countries[["iso_a2_eh", "Country", "Latitude", "Longitude", "y1", "y2", "x1", "x2"]].iloc[idx, 6])
            x2 = float(countries[["iso_a2_eh", "Country", "Latitude", "Longitude", "y1", "y2", "x1", "x2"]].iloc[idx, 7])

            if x1 < x2:
                x = x1
            else:
                x = x2

            if y1 < y2:
                y = y1
            else:
                y = y2

            lat = float(countries[["iso_a2_eh", "Country", "Latitude", "Longitude", "y1", "y2", "x1", "x2"]].iloc[idx, 2]) + random.uniform(0, y)
            lon = float(countries[["iso_a2_eh", "Country", "Latitude", "Longitude", "y1", "y2", "x1", "x2"]].iloc[idx, 3]) + random.uniform(0, x)
            coordinates = (lat, lon)
            country_name = countries[["iso_a2_eh", "Country", "Latitude", "Longitude"]].iloc[idx, 1]
            country_iso = countries[["iso_a2_eh", "Country", "Latitude", "Longitude"]].iloc[idx, 0]
            pp = folium.Html("""<p id='srt_map' name='"""+country_iso+"""'>"""+country_name+"""</p>""", script=True)
            popup = folium.Popup(pp, max_width=2650)
            folium.Marker(coordinates, popup=popup).add_to(m)
        except:
            continue

    m = m._repr_html_()

    #filter_map

    pro = Project.objects.all()
    pro_count = Project.objects.all().count()
    pro_access_count = Access.objects.all().count()
    pro_mission_filter = Access.objects.filter(project__mission=0).count()
    pro_noun_mission_filter = Access.objects.filter(project__mission=1).count()
    pro_semi_mission_filter = Access.objects.filter(project__mission=2).count()


    context = {
        'm': m,
        'pro': pro,
        'pro_count': pro_count,
        'pro_access_count': pro_access_count,
        'pro_mission_filter': pro_mission_filter,
        'pro_noun_mission_filter': pro_noun_mission_filter,
        'pro_semi_mission_filter': pro_semi_mission_filter,
    }

    return render(request, 'main/core/map/home.html', context)

