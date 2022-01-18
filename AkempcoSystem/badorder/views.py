from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from fm.views import get_index, add_search_key
from AkempcoSystem.decorators import user_is_allowed
from admin_area.models import Feature
from .models import *
from .forms import *


# used by pagination
MAX_ITEMS_PER_PAGE = 10


################################
#   Creditor FM
################################

@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_BO), name='dispatch')
class BOListView(ListView):
    model = BadOrder
    context_object_name = 'badorders'
    template_name = "badorder/bo_list.html"
    paginate_by = MAX_ITEMS_PER_PAGE

    def get_queryset(self):
        # check if the user searched for something
        key = get_index(self.request, "table_search")
        object_list = self.model.objects.all()
        if key:
            object_list = object_list.filter(
                Q(supplier__supplier_name__icontains=key) |
                Q(status__icontains=key)
            )
        return object_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return add_search_key(self.request, context)    
    
    
@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_BO), name='dispatch')
class BadOrderCreateView(CreateView):
    model = BadOrder
    form_class = BadOrderForm
    template_name = 'badorder/bo_form.html'

    def post(self, request, *args, **kwargs):
        form = BadOrderForm(request.POST)
        if form.is_valid():
            bo = form.save(commit=False)
            bo.reported_by = self.request.user
            bo.save()
            messages.success(request, "The bad order record was created successfully.")
            return redirect('bo_list')
            # return redirect('bo_items')
        
        else:
            return render(request, 'badorder/bo_form.html', {'form': form})
        

@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_BO), name='dispatch')
class BadOrderUpdateView(SuccessMessageMixin, UpdateView):
    model = BadOrder
    context_object_name = 'badorder'
    form_class = BadOrderForm
    template_name = "badorder/bo_form.html"
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('bo_list')
    success_message = "The bad order record was updated successfully."