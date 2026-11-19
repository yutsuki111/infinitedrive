from django.shortcuts import render
from django.views.generic import CreateView, TemplateView
from django.urls import reverse
from .forms import CreateRoomForm

# Create your views here.
class RoomCreateView(CreateView):
    template_name = "room/room_create.html"
    form_class = CreateRoomForm

    def get_success_url(self):
        return reverse('room:top', kwargs={'room_id':self.object.id})
