from django.http import JsonResponse


# Return sample clues for testing
def get_clues(request):
    clues = [
        {
            "clue_id": "clue_001",
            "name": "Bloody Knife",
            "description": "A knife found near the crime scene.",
            "location": "Kitchen"
        },
        {
            "clue_id": "clue_002",
            "name": "Broken Watch",
            "description": "A watch found near the victim.",
            "location": "Living Room"
        }
    ]

    return JsonResponse({"clues": clues})