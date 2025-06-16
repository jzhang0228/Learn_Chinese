# ! encoding=utf8
import json
import os
import random
import re
from pathlib import Path

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.generic import View

from openai import OpenAI

from .forms import AudioForm, LessonForm
from .models import Lesson


def split_word(sentence):
    sentence.strip()
    if " " in sentence:
        return sentence.split()
    return list(sentence)


def get_sentence(text):
    trim_pattern = re.compile(r"^[,.;，。：]+|[,.;，。：]+$", re.UNICODE)
    split_pattern = re.compile(r"[,.;，。：]", re.UNICODE)

    plain_text = text
    plain_text = "".join(plain_text.splitlines())
    plain_text = re.sub(trim_pattern, "", plain_text)
    sentences = re.split(split_pattern, plain_text)
    sentences = [split_word(sentence) for sentence in sentences if sentence]
    return json.dumps(sentences)


class LessonsView(View):
    def get(self, request):
        lessons = Lesson.objects.all()
        context = {
            "lessons": lessons,
        }
        return render(request, "main_game/lessons.html", context)


class LessonView(View):
    def get_extension(self, name):
        if not name:
            return None
        return name.rsplit(".", -1)[-1]

    def get(self, request, lesson_id=None):
        lesson_id = lesson_id or 1
        lesson = Lesson.objects.get(id=lesson_id)
        context = {
            "lesson": lesson,
            "plain_text": get_sentence(lesson.text),
            "audio_extension": self.get_extension(lesson.audio.name),
            "english_audio_extension": self.get_extension(lesson.english_audio.name),
        }
        return render(request, "main_game/lesson.html", context)


class EditView(View):
    def get(self, request, lesson_id=None):
        if lesson_id:
            lesson = Lesson.objects.get(id=lesson_id)
            form = LessonForm(instance=lesson)
        else:
            form = LessonForm()
        context = {
            "form": form,
            "lesson_id": lesson_id,
        }
        return render(request, "main_game/edit.html", context)

    def post(self, request, lesson_id=None):
        if lesson_id:
            lesson = Lesson.objects.get(id=lesson_id)
            form = LessonForm(request.POST, request.FILES, instance=lesson)
        else:
            form = LessonForm(request.POST, request.FILES)

        if form.is_valid():
            lesson = form.save()
            return redirect("lesson", lesson.id)
        else:
            context = {
                "form": form,
            }
            return render(request, "main_game/edit.html", context)


class UploadAudio(View):
    def post(self, request, lesson_id):
        lesson = Lesson.objects.get(id=lesson_id)
        form = AudioForm(request.POST, request.FILES, instance=lesson)
        if form.is_valid():
            lesson = form.save()
        lesson.save()

        context = {
            "form": form,
        }
        return render(request, "main_game/lesson.html", context)


class PracticeView(View):
    def get(self, request):
        return render(request, "main_game/practice.html", {})

    def post(self, request):
        client = OpenAI()
        character = request.POST.get("character", "好")
        response = client.responses.create(
            model="gpt-4.1",
            input="""
                Write a Chinese sentence with '%s‘ with less than 10 characters.
                Only output generated sentence, pinyin and English translation in
                JSON format with keys: sentence, pinyin and english.
            """
            % character,
        )

        response_dict = json.loads(response.output_text)

        random_number = random.randint(1, 10)
        audio_filename = "uploads/speech/%i.mp3" % random_number
        file_path = os.path.join(settings.MEDIA_ROOT, audio_filename)
        os.makedirs(
            os.path.dirname(file_path), exist_ok=True
        )  # Create directory if it doesn't exist
        meida_file_path = os.path.join(settings.MEDIA_URL, audio_filename)

        with client.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",
            voice="alloy",
            input=response_dict["sentence"],
            instructions="Speak in a cheerful and positive tone.",
        ) as response:
            response.stream_to_file(file_path)

        context = {
            "sentence": response_dict["sentence"],
            "pinyin": response_dict["pinyin"],
            "english": response_dict["english"],
            "speech": meida_file_path,
            "plain_text": get_sentence(response_dict["sentence"]),
        }

        return JsonResponse(context)
