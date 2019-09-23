from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView

from .models import File
from django.urls import (
    reverse_lazy
)

class SupplierHome(LoginRequiredMixin, TemplateView):
    template_name = 'supplier_app/supplier-home.html'
    login_url = '/'

class CreateFileView(CreateView):
    model = File
    fields = ['file']

    def get_success_url(self):
        return reverse_lazy('supplier-home')

    def form_valid(self, form):
        form.instance.file = self.request.FILES['file']
        self.object = form.save()
        return super(CreateFileView, self).form_valid(form)
