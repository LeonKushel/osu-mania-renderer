"""R3D_X264_* knobs on the libx264 master (render/encode.py). With none set the
command must be what it always was; set, they replace the flat bitrate target
and add the preset / thread cap; they never touch another encoder."""
from pathlib import Path

from osu_mania_renderer_v2.render import encode as enc

_KNOBS = ("_X264_PRESET", "_X264_CRF", "_X264_THREADS", "_X264_PARAMS")


def _video_args(encoder="libx264", override=None, **knobs):
    saved = {k: getattr(enc, k) for k in _KNOBS}
    try:
        for k in _KNOBS:
            setattr(enc, k, knobs.get(k, ""))
        cmd = enc.build_ffmpeg_cmd(
            encoder=encoder, encoder_device=None, resolution=(1920, 1080),
            fps=60, audio_path=None, audio_rate=1.0, audio_lead_in_ms=0,
            video_bitrate="2500k", video_bitrate_override=override,
            audio_bitrate="160k", output_path=Path("/x/out.mp4"))
    finally:
        for k, v in saved.items():
            setattr(enc, k, v)
    i = cmd.index("-c:v")
    return cmd[i:cmd.index("-color_range")]


def test_unset_is_the_command_as_it_was():
    assert _video_args() == ["-c:v", "libx264", "-b:v", "2500k"]


def test_crf_replaces_the_bitrate_target():
    assert _video_args(_X264_CRF="20", _X264_PRESET="veryfast",
                       _X264_THREADS="6") == [
        "-c:v", "libx264", "-crf", "20", "-preset", "veryfast", "-threads", "6"]


def test_preset_alone_keeps_the_bitrate_target():
    assert _video_args(_X264_PRESET="veryfast") == [
        "-c:v", "libx264", "-b:v", "2500k", "-preset", "veryfast"]


def test_an_explicit_bitrate_override_wins_over_crf():
    assert _video_args(override=6_000_000, _X264_CRF="20") == [
        "-c:v", "libx264", "-b:v", "6000000"]


def test_params_are_passed_through():
    assert _video_args(_X264_PARAMS="ref=2:bframes=1")[-2:] == [
        "-x264-params", "ref=2:bframes=1"]


def test_other_encoders_are_untouched():
    assert _video_args(encoder="libopenh264", _X264_CRF="20",
                       _X264_PRESET="veryfast", _X264_THREADS="6") == [
        "-c:v", "libopenh264", "-b:v", "2500k"]
