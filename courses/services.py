"""
Video streaming abstraction service.
Allows switching providers (Bunny Stream, Mux, or generic embeds)
while keeping controllers and templates completely decoupled.
"""

from django.conf import settings
from django.utils.safestring import mark_safe


class VideoPlayerService:
    @staticmethod
    def render_player(lesson):
        """
        Renders the video player HTML for a given lesson based on its provider.
        """
        provider = lesson.video_provider
        video_id = lesson.video_id_or_url

        if provider == "bunny":
            library_id = getattr(settings, "BUNNY_STREAM_LIBRARY_ID", "") or "default"
            # Bunny stream secure iframe embed
            html = f"""
            <iframe
                src="https://iframe.mediadelivery.net/embed/{library_id}/{video_id}?autoplay=false&preload=true"
                loading="lazy"
                style="border: none; position: absolute; top: 0; height: 100%; width: 100%;"
                allow="accelerometer; gyroscope; autoplay; encrypted-media; picture-in-picture;"
                allowfullscreen="true">
            </iframe>
            """
            return mark_safe(html)

        elif provider == "mux":
            # Mux player embed
            html = f"""
            <mux-player
                playback-id="{video_id}"
                metadata-video-title="{lesson.title}"
                style="width: 100%; height: 100%;">
            </mux-player>
            """
            return mark_safe(html)

        elif provider == "youtube_unlisted":
            # Safe YouTube embed
            html = f"""
            <iframe
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
                <video controls controlsList="nodownload" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;">
                    <source src="{video_id}" type="video/mp4">
                    Votre navigateur ne supporte pas la lecture vidéo HTML5.
                </video>
                """
            else:
                # Placeholder sample video for dev demo
                html = f"""
                <div style="position:absolute; inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center; background:#070b10; color:#fff; text-align:center; padding:20px;">
                    <i class="fa fa-play-circle" style="font-size:64px; color:var(--accent-cyan); margin-bottom:16px;"></i>
                    <h3 style="font-size:20px; margin-bottom:8px;">{lesson.title}</h3>
                    <p style="color:var(--text-muted); font-size:14px; max-width:480px;">
                        Flux vidéo sécurisé ({lesson.get_video_provider_display()}). ID: <code>{video_id}</code>.
                    </p>
                </div>
                """
            return mark_safe(html)
