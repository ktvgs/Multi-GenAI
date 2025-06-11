# users/context_processors.py

import random

def random_background_image(request):
    if request.user.is_authenticated:
        if "background_image" not in request.session:
            backgrounds = [
                'users/backgrounds/bg1.jpg',
                'users/backgrounds/bg2.jpg',
                'users/backgrounds/bg3.jpg',
            ]
            request.session["background_image"] = random.choice(backgrounds)

        return {
            "background_image": request.session["background_image"]
        }
    return {}
