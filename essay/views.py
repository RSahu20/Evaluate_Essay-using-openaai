from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import EssayForm
import string,re
from .models import Essay
from spellchecker import SpellChecker
from openai import OpenAI
@login_required
def submit_essay(request):
    if request.method == 'POST':
        form = EssayForm(request.POST)
        if form.is_valid():
            essay = form.save(commit=False)
            essay.user = request.user
            essay.save()
            feedback = evaluate_essay(essay.title, essay.body)
            spelling_errors = mispell_index(essay.word, essay.body)
            misspelled = mispell_words(essay.body)
            misspelled_str = ", ".join(misspelled)
            length = len(misspelled)   
            essay.feedback_text = feedback
            essay.mispelled_word = spelling_errors
            essay.word = misspelled_str
            essay.words_count = length
            essay.save()

            return render(request, 'essay/feedback.html', {'essay': essay, 'feedback': feedback,'spelling_errors': spelling_errors,'misspelled_str':misspelled_str, 'length':length})
    else:
        form = EssayForm()
    return render(request, 'essay/submit.html', {'form': form})

def evaluate_essay(title, body):
      # Replace 'YOUR_OPENAI_API_KEY' with your actual OpenAI API key
    client = OpenAI(api_key='')
    # Concatenate title and body for evaluation
    prompt = f"Please evaluate the essay titled {title} and {body} based on the following criteria: Content relevance with {title}: (yes/no), Essay score (out of 10): " "single word answer for each criteria "

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ]

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0,  # Set temperature to 0 for deterministic results
        max_tokens=500,  # Limit the maximum number of tokens in the response
    )

    feedback = completion.choices[0].message.content.strip()
    print(feedback)
    return feedback



def mispell_words(body):  
    body_cleaned = body.translate(str.maketrans('', '', string.punctuation))
    spell = SpellChecker()
    # Find misspelled words
    misspelled = spell.unknown(body_cleaned.lower().split())
    # misspelled_str = ", ".join(misspelled)
    print(misspelled)
    print(len(misspelled))

    return misspelled
    # Collect misspelled words and their indices
def mispell_index(word, body):  
    spelling_errors = []
    index = mispell_words(body)
    for word in index:
        matches = re.finditer(r'\b' + re.escape(word) + r'\b', body.lower())
        for match in matches:
            start_index = match.start()
            end_index = match.end()
            spelling_errors.append({'word': word, 'start_index': start_index, 'end_index': end_index})
    # word = Essay.objects.create(word=misspelled_str)
    # Construct feedback message
    print(spelling_errors)
    return spelling_errors

@login_required  
def essay_history(request):
    # Retrieve all essays submitted by the current user ordered by submission date
    essays = Essay.objects.filter(user=request.user).order_by('-submission_date')
    return render(request, 'essay/history.html', {'essays': essays})
