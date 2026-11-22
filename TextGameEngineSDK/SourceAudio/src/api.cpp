
#include "sourceaudio/api.h"
#include "sourceaudio/audio.hpp"

extern "C" {

SA_Audio sa_create() {
    try {
        return new SourceAudio::Audio();
    } catch (...) {
        return nullptr;
    }
}

void sa_destroy(SA_Audio audio) {
    delete static_cast<SourceAudio::Audio*>(audio);
}

int sa_load_music(SA_Audio audio, const char* path) {
    if (!audio || !path) return 0;

    try {
        return static_cast<SourceAudio::Audio*>(audio)
            ->loadMusic(path) ? 1 : 0;
    } catch (...) {
        return 0;
    }
}

void sa_play_music(SA_Audio audio, int loop) {
    if (!audio) return;

    static_cast<SourceAudio::Audio*>(audio)
        ->playMusic(loop != 0);
}

void sa_stop_music(SA_Audio audio) {
    if (!audio) return;

    static_cast<SourceAudio::Audio*>(audio)
        ->stopMusic();
}

void sa_set_music_volume(SA_Audio audio, float volume) {
    if (!audio) return;

    static_cast<SourceAudio::Audio*>(audio)
        ->setMusicVolume(volume);
}

void sa_set_sound_volume(SA_Audio audio, float volume) {
    if (!audio) return;

    static_cast<SourceAudio::Audio*>(audio)
        ->setSoundVolume(volume);
}

int sa_play_sound(SA_Audio audio, const char* path) {
    if (!audio || !path) return 0;

    try {
        return static_cast<SourceAudio::Audio*>(audio)
            ->playSound(path) ? 1 : 0;
    } catch (...) {
        return 0;
    }
}

}
