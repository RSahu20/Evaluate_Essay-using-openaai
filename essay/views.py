from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import EssayForm
from openai import OpenAI 
from .models import Essay
from decouple import config
@login_required
def submit_essay(request):
    if request.method == 'POST':
        form = EssayForm(request.POST)
        if form.is_valid():
            essay = form.save(commit=False)
            essay.user = request.user
            essay.save()
            feedback = evaluate_essay(essay.title, essay.body)
            essay.feedback_text = feedback
            essay.save()
            return render(request, 'essay/feedback.html', {'essay': essay, 'feedback': feedback})
    else:
        form = EssayForm()
    return render(request, 'essay/submit.html', {'form': form})



def evaluate_essay(title, body):
    # Replace 'YOUR_OPENAI_API_KEY' with your actual OpenAI API key
    client = OpenAI(api_key=config('OPENAI_API_KEY'))
    # Concatenate title and body for evaluation
    prompt = f"Can you provide feedback on the essay of {title} by the {body}  the format of answer should be in this format:Count of spelling error, content relevance with {title} (yes/no) , Essay score(out of 10)"
    messages=[
          {"role": "system", "content": "You are a helpful assistant."},
             {"role": "user", "content": prompt
              }
            ]
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0,  # Set temperature to 0 for deterministic results
        max_tokens=500,  # Limit the maximum number of tokens in the response
       # Stop generation at the end of the essay
    )

    feedback = completion.choices[0].message.content.strip()
    print(feedback)
    # spelling_errors = feedback.get("count_spelling")
    # content_related_to_title = feedback.get("content_related")
    # essay_score = feedback.get("Essay_score")
    # print(spelling_errors)

    
    return feedback

def essay_history(request):
    # Retrieve all essays submitted by the current user ordered by submission date
    essays = Essay.objects.filter(user=request.user).order_by('-submission_date')
    return render(request, 'essay/history.html', {'essays': essays})