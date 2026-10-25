import hashlib
import time
from django.conf import settings
from django.utils.safestring import mark_safe


class VideoPlayerService:
    @staticmethod
    def generate_bunny_signed_url(library_id: str, video_id: str, token_key: str, expiration_seconds: int = 7200) -> str:
        """
        Generates a token-authenticated iframe embed URL for Bunny Stream using SHA-256 HMAC.
        Bunny Token Auth format:
        token = sha256_hex(token_key + video_id + expires)
        embed_url = https://iframe.mediadelivery.net/embed/{library_id}/{video_id}?token={token}&expires={expires}&autoplay=false&preload=true
        """
        expires = int(time.time()) + expiration_seconds
        raw_signature = f"{token_key}{video_id}{expires}"
        token = hashlib.sha256(raw_signature.encode("utf-8")).hexdigest()
        return f"https://iframe.mediadelivery.net/embed/{library_id}/{video_id}?token={token}&expires={expires}&autoplay=false&preload=true"

    @classmethod
    def render_player(cls, lesson, user=None):
        """
        Renders the video player HTML for a given lesson based on its provider,
        verifying server-side access rights before generating signed stream credentials.
        """
        if user is not None and not lesson.can_access(user):
            return mark_safe(
                '<div style="position:absolute; inset:0; display:flex; flex-direction:column; align-items:center; '
                'justify-content:center; background:#070b10; color:#ff6347; text-align:center; padding:20px;">'
                '<i class="fa fa-lock" style="font-size:48px; margin-bottom:12px;"></i>'
                '<h3 style="font-size:18px; font-family:\'Righteous\', sans-serif;">Accès Réservé</h3>'
                '<p style="color:#a0a0a0; font-size:13px; max-width:400px; margin-top:6px;">'
                'Cette leçon fait partie d\'une formation payante. Veuillez vous inscrire pour débloquer le lecteur vidéo.'
                '</p></div>'
            )

        provider = lesson.video_provider
        video_id = lesson.video_id_or_url

        if provider == "bunny":
            library_id = getattr(settings, "BUNNY_STREAM_LIBRARY_ID", "") or "default"
            token_key = getattr(settings, "BUNNY_STREAM_TOKEN_KEY", "")

            if token_key:
                embed_src = cls.generate_bunny_signed_url(library_id, video_id, token_key)
            else:
                embed_src = f"https://iframe.mediadelivery.net/embed/{library_id}/{video_id}?autoplay=false&preload=true"

            html = f"""
            <iframe
                id="bunny-stream-player"
                src="{embed_src}"
                loading="lazy"
                style="border: none; position: absolute; top: 0; left: 0; height: 100%; width: 100%;"
                allow="accelerometer; gyroscope; autoplay; encrypted-media; picture-in-picture;"
                allowfullscreen="true">
            </iframe>
            """
            return mark_safe(html)

        elif provider == "mux":
            html = f"""
            <mux-player
                id="mux-video-player"
                playback-id="{video_id}"
                metadata-video-title="{lesson.title}"
                style="width: 100%; height: 100%;">
            </mux-player>
            """
            return mark_safe(html)

        elif provider == "youtube_unlisted":
            html = f"""
            <iframe
                id="youtube-video-player"
                src="https://www.youtube-nocookie.com/embed/{video_id}?rel=0&modestbranding=1"
                title="{lesson.title}"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowfullscreen
                style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border:0;">
            </iframe>
            """
            return mark_safe(html)

        else:
            # Native HTML5 video player or custom embed
            if video_id.startswith("http"):
                html = f"""
                <video id="html5-video-player" controls controlsList="nodownload" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;">
                    <source src="{video_id}" type="video/mp4">
                    Votre navigateur ne supporte pas la lecture vidéo HTML5.
                </video>
                """
            else:
                # Placeholder sample video for dev demo
                html = f"""
                <div style="position:absolute; inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center; background:#070b10; color:#fff; text-align:center; padding:20px;">
                    <i class="fa fa-play-circle" style="font-size:64px; color:#00FFFF; margin-bottom:16px;"></i>
                    <h3 style="font-size:20px; margin-bottom:8px; font-family:'Righteous', sans-serif;">{lesson.title}</h3>
                    <p style="color:#a0a0a0; font-size:14px; max-width:480px;">
                        Flux vidéo ({lesson.get_video_provider_display()}). ID: <code>{video_id}</code>.
                    </p>
                </div>
                """
            return mark_safe(html)
