from django.shortcuts import render
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from .models import Invoice


class InvoiceCreateView(CreateView):
    model = Invoice
    template_name = 'invoices/supplier/invoice_form.html'


    def form_valid(self, form):
        form.instance.user = self.request.user
        form.save()
        return super(InvoiceCreateView, self).form_valid(form)