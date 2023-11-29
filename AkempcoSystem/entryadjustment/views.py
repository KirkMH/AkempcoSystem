from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, CreateView
from django.contrib import messages
from django.db.models import Q
from django_serverside_datatable.views import ServerSideDatatableView
from django.contrib.messages.views import SuccessMessageMixin

from AkempcoSystem.decorators import user_is_allowed
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from admin_area.models import Feature, UserType
from .models import EntryAdjustment
from .forms import EntryAdjustmentForm


@login_required
@user_is_allowed(Feature.TR_ENTRYADJ)
def request_list(request):
    return render(request, "entryadj/entry_adjustment.html")


@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_ENTRYADJ), name='dispatch')
class RequestDTListView(ServerSideDatatableView):
    
    def get(self, request, *args, **kwargs):
        userType = request.user.userdetail.userType
        if userType == UserType.GM or userType == UserType.AUDIT:
            # GM and Audit must be able to see all the requests
            self.queryset = EntryAdjustment.objects.all()
        else:
            # other users will only see the requests they made
            self.queryset = EntryAdjustment.objects.filter(requested_by=request.user)
        self.columns = ['pk', 'requested_at', 'transaction_type', 'reference_num', 'adjustment_detail', 'reason', 'status']
        return super().get(request, *args, **kwargs)

    
@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_ENTRYADJ), name='dispatch')
class RequestCreateView(SuccessMessageMixin, CreateView):
    model = EntryAdjustment
    form_class = EntryAdjustmentForm
    template_name = 'entryadj/entry_adjustment_new.html'
    success_message = "New entry adjustment request submitted."
    success_url = reverse_lazy('request_list')
    
    def form_valid(self, form):
       adjustment = form.save(commit=False)
       form.instance.requested_by = self.request.user
       form.save()
       return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_ENTRYADJ), name='dispatch')
class RequestDetailView(DetailView):
    model = EntryAdjustment
    template_name = "entryadj/entry_adjustment_view.html"
    context_object_name = 'adjustment'


@login_required
@user_is_allowed(Feature.TR_ENTRYADJ)
def approve_request(request, pk):
    adjustment = get_object_or_404(EntryAdjustment, pk=pk)
    adjustment.approve(request.user)
    messages.success(request, "Entry adjustment was approved.")
    return redirect('request_list')


@login_required
@user_is_allowed(Feature.TR_ENTRYADJ)
def cancel_request(request, pk):
    adjustment = get_object_or_404(EntryAdjustment, pk=pk)
    adjustment.cancel(request.user)
    messages.success(request, "Entry adjustment was cancelled.")
    return redirect('request_list')