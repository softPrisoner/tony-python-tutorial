from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone

from .models import Choice, Question


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """Return the last five published questions """
        return Question.objects.order_by("-pub_date")[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"


class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results"


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Exception):
        return render(request, "polls/details.html", {"question": question, "error_message": "you did't choose anyone"})
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # return HttpResponse("you are voting on question.%s " % question_id)
        return HttpResponseRedirect(reverse('polls:results', args=(question_id,)))


def get_queryset(self):
    """
    Return the last five published questions (not including those set to be published in the future)

    """
    return Question.objects.filter(pub_date_lte=timezone.now()).order_by("-pub_date")[:5]