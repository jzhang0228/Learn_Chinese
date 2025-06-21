# ! encoding=utf8
import json
import os
import random
import re
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.views.generic import View

from openai import OpenAI

from .forms import AudioForm, LessonForm
from .models import Character, Lesson


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
    def save_characters(self, characters):
        for character in characters:
            items = Character.objects.filter(character=character)
            if not items:
                Character.objects.create(character=character, right_count=0)

    def get(self, request):
        characters = Character.objects.all()
        context = {
            "characters": [
                {"character": c.character, "count": c.right_count} for c in characters
            ],
        }
        print(context)
        return render(request, "main_game/practice.html", context)

    def post(self, request):
        is_random = request.POST.get("random", False)
        if is_random:
            characters = Character.objects.all()
            characters = [c.character for c in characters]
            character = random.choice(characters)
            prompt = (
                "Write a short Chinese sentence with the character '%s‘." % character
            )
        else:
            string = request.POST.get("character", "好")
            if len(string) > 1:
                characters = list(string)
                self.save_characters(characters)
                prompt = (
                    "Write a Chinese sentence with of these characters '%s‘."
                    % ", ".join(characters)
                )
            else:
                self.save_characters([string])
                prompt = (
                    "Write a short Chinese sentence with the character '%s‘." % string
                )

        client = OpenAI()
        response = client.responses.create(
            model="gpt-4.1",
            input="""
                %s Only output generated sentence, pinyin and English translation in
                JSON format with keys: sentence, pinyin and english.
            """
            % prompt,
            temperature=2,
        )

        print(response.output_text)
        response_dict = json.loads(response.output_text)
        print(response_dict)
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


class SaveCharactersView(View):
    def success(self, characters):
        items = Character.objects.filter(character__in=characters)
        for item in items:
            if item.right_count >= 6:
                item.delete()
            else:
                item.right_count += 1
                item.save()

    def fail(self, characters):
        for character in characters:
            try:
                item = Character.objects.get(character=character)
                item.right_count = 0
                item.save()
            except ObjectDoesNotExist:
                Character.objects.create(character=character, right_count=0)

    def post(self, request):
        success_characters = json.loads(request.POST.get("successCharacters", "[]"))
        failed_characters = json.loads(request.POST.get("failedCharacters", "[]"))
        self.success(success_characters)
        self.fail(failed_characters)
        characters = Character.objects.all()
        context = {
            "characters": [
                {"character": c.character, "count": c.right_count} for c in characters
            ],
        }
        return JsonResponse(
            {
                "success": True,
                "html": render_to_string("main_game/saved_characters.html", context),
            }
        )
